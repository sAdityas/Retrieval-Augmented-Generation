# main.py - Level 7 (Query Rewriting + Adaptive Retrieval + Self-Reflection + Confidence Scoring)

import os
import pandas as pd
import pickle
import hashlib
import time
from dotenv import load_dotenv
from retriever import Retriever
from bm25_retriever import BM25Retriever
from hybrid_retriever import HybridRetriever
from reRanker import reRanker
from semantic_deduplicate import SemanticDeduplicate
from chunker import chunk_documents
from llm import llm_generate

# ----------------------------
# 1. Load environment variables
# ----------------------------
load_dotenv()
TOP_K = int(os.getenv("TOP_K", 5))
MAX_CHARS = int(os.getenv("MAX_CHARS", 300))
OVERLAP = int(os.getenv("OVERLAP", 30))
ALPHA = float(os.getenv("ALPHA", 0.8))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ----------------------------
# 2. Helper functions
# ----------------------------
def file_hash(path):
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def normalize_columns(df):
    rename_map = {}
    for c in df.columns:
        norm = c.strip().lower()
        if norm in ["module", "sap module"]: 
            rename_map[c] = "Module"
        elif norm in ["t-code", "tcode", "transaction"]:
            rename_map[c] = "T-Code"
        elif norm in ["error", "error message"]:
            rename_map[c] = "Error"
        elif norm in ["description", "error description"]:
            rename_map[c] = "Description"
        elif norm in ["cause", "root cause"]:
            rename_map[c] = "Cause"
        elif norm in ["step-by-step solution", "steps to solve", "solution"]:
            rename_map[c] = "Step-by-Step Solution"
    return df.rename(columns=rename_map)

def load_excel(file_path):
    df = pd.read_excel(file_path)
    df = normalize_columns(df)
    required_cols = ["Module","T-Code","Error","Description","Cause","Step-by-Step Solution"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""
    documents = []
    for _, row in df.iterrows():
        text = (
            f"Module: {row['Module']}\n"
            f"T-Code: {row['T-Code']}\n"
            f"Error: {row['Error']}\n"
            f"Description: {row['Description']}\n"
            f"Cause: {row['Cause']}\n"
            f"Solution: {row['Step-by-Step Solution']}"
        )
        documents.append(text)
    return documents

# ----------------------------
# 3. Query rewriting & adaptive retrieval
# ----------------------------
def rewrite_query(user_query):
    """Use LLM to rewrite or expand the query for better retrieval."""
    prompt = f"""
    You are a query rewriting assistant. 
    Take the following original query and rewrite it into a more formal, detailed, and descriptive version that would be suitable for documentation or troubleshooting search in 1 or 2 sentence.
    These are all issues that are occuring in SAP.
    Query: {user_query}
    """
    rewritten = llm_generate(prompt, stream=False)
    return rewritten.strip()

def adaptive_top_k(rewritten, base_k=TOP_K, max_k=10):
    words = len(rewritten.split())
    if words < 3:
        return base_k
    elif words < 6:
        return base_k + 1
    else:
        return min(max_k, base_k + 2)

# ----------------------------
# 4. Cache or load chunks
# ----------------------------
excel_file = "SAP_TCode_Errors_Template.xlsx"
cache_file = "cached_chunks.pkl"
hash_file = "excel_hash.txt"

excel_md5 = file_hash(excel_file)
rebuild_cache = True

if os.path.exists(cache_file) and os.path.exists(hash_file):
    with open(hash_file, "r") as f:
        cached_hash = f.read().strip()
    if cached_hash == excel_md5:
        rebuild_cache = False

if rebuild_cache:
    print("📄 Chunking Excel...")
    raw_docs = load_excel(excel_file)
    chunked_docs = chunk_documents(raw_docs, max_char=MAX_CHARS, overlap=OVERLAP)
    with open(cache_file, "wb") as f:
        pickle.dump(chunked_docs, f)
    with open(hash_file, "w") as f:
        f.write(excel_md5)
    print(f"✅ Cached {len(chunked_docs)} chunks and updated hash.")
else:
    print("🔄 Loading cached chunks...")
    with open(cache_file, "rb") as f:
        chunked_docs = pickle.load(f)

texts = [c["text"] for c in chunked_docs]
print(f"Loaded {len(texts)} chunks.")

# ----------------------------
# 5. Setup Retrieval (FAISS + BM25 + Hybrid)
# ----------------------------
faiss_retriever = Retriever(texts)
bm25_retriever = BM25Retriever(texts)
hybrid_retriever = HybridRetriever(faiss_retriever, bm25_retriever, alpha=ALPHA)

# Load FAISS index if exists
if os.path.exists("faiss.index") and os.path.exists("docs.npy"):
    faiss_retriever.load()
else:
    faiss_retriever.save()

deduper = SemanticDeduplicate()
reranker = reRanker()

# ----------------------------
# 6. Main Query Loop
# ----------------------------
queries = [
    "Purchase Order Failed while doing ME21N"
]

for q in queries:
    print(f"\n🔎 Original Query: {q}")

    top_k = adaptive_top_k(q)
    retrieved_docs = hybrid_retriever.retrieve(q, top_k=top_k)
    raw_docs = [doc for doc, _ in retrieved_docs]

    deduped_docs = deduper.deduplicate(raw_docs)
    combined_content = "\n".join(deduped_docs[:3])

    # ----------------------------
    # 7. Confidence Scoring
    # ----------------------------
    confidence_prompt = f"""
    Based on this context, how confident are you in answering this?
    Respond with one word only.( high, medium, or low )

    Context:
    {combined_content}

    Question: {q}
    """
    confidence = llm_generate(confidence_prompt, stream=True)
    print(f"\n🔎 Confidence: {confidence}")

    # ----------------------------
    # 8. Self-Reflection & Retry
    # ----------------------------
    if confidence.lower().strip() == "low":
        print("🤔 Low confidence or no answer — retrying with expanded query...")
        
        expanded_query = rewrite_query(q)
        print(f"✍️ Rewritten Query: {expanded_query}")
        new_top_k = min(top_k + 2, 10)
        retrieved_docs = hybrid_retriever.retrieve(expanded_query, top_k=new_top_k)
        raw_docs = [doc for doc, _ in retrieved_docs]
        deduped_docs = deduper.deduplicate(raw_docs)
        combined_content = "\n".join(deduped_docs[:3])
        llm_generate(
            f"Answer the question based on the following context. "
            f"Context:\n{combined_content}\n\nQuestion: {expanded_query}"
        )
    else:
        llm_generate(
            f"Answer the question based on the following context. "
            f"Context:\n{combined_content}\n\nQuestion: {q}"
        )