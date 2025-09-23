# Flask API for Level 9 RAG with chat history upto n ( 3-5 ) contexts of past answer and queries
import os
import pickle
import hashlib
import time
import pandas as pd
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from collections import deque, defaultdict

from retriever import Retriever
from bm25_retriever import BM25Retriever
from hybrid_retriever import HybridRetriever
from reRanker import reRanker
from semantic_deduplicate import SemanticDeduplicate
from chunker import chunk_documents
from llm import llm_generate

# ----------------------------
# 1. Flask Setup
# ----------------------------
app = Flask(__name__)
CORS(app)


# ----------------------------
# Initializing Dictionary 
#-----------------------------

SESSION_MEMORY = defaultdict(lambda: deque(maxlen=5))


# ----------------------------
# 2. Environment Setup
# ----------------------------
TOP_K = int(os.getenv("TOP_K", 5))
MAX_CHARS = int(os.getenv("MAX_CHARS", 300))
OVERLAP = int(os.getenv("OVERLAP", 30))
ALPHA = float(os.getenv("ALPHA", 0.8))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ----------------------------
# 3. Helpers
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
    required_cols = ["Module", "T-Code", "Error", "Description", "Cause", "Step-by-Step Solution"]
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

def rewrite_query(user_query):
    prompt = f"""
    You are a query rewriting assistant.
    Rewrite this SAP troubleshooting query into a formal, detailed question.
    Query: {user_query}
    """
    return llm_generate(prompt, stream=False).strip()

def adaptive_top_k(rewritten, base_k=TOP_K, max_k=3):
    words = len(rewritten.split())
    if words < 3:
        return base_k
    elif words < 6:
        return base_k + 1
    else:
        return min(max_k, base_k + 1)

# ----------------------------
# 4. Cache/Load Documents
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

# ----------------------------
# 5. Setup Retrieval
# ----------------------------
faiss_retriever = Retriever(texts)
bm25_retriever = BM25Retriever(texts)
hybrid_retriever = HybridRetriever(faiss_retriever, bm25_retriever, alpha=ALPHA)

if os.path.exists("faiss.index") and os.path.exists("docs.npy"):
    faiss_retriever.load()
else:
    faiss_retriever.save()

deduper = SemanticDeduplicate()
reranker = reRanker()

# ----------------------------
# 6. API Endpoint
# ----------------------------
@app.route("/rag-query", methods=["POST"])
def rag_query():
    data = request.json
    query = data.get("query")
    session_id = data.get("session_id","default")
    if not query:
        return jsonify({"error": "Missing query"}), 400

    start_time = time.time()

    # Get Memory
    history = list(SESSION_MEMORY[session_id])
    history_text = "\n".join([f"User: {h['query']} \n Bot: {h['answer']}" for h in history])
    
    # Retrieval
    top_k = adaptive_top_k(query)
    retrieved_docs = hybrid_retriever.retrieve(query, top_k=top_k)
    raw_docs = [doc for doc, _ in retrieved_docs]
    deduped_docs = deduper.deduplicate(raw_docs)
    combined_content = "\n".join(deduped_docs[:3])

    # confidence_prompt = f"""
    # Based on this context, how confident are you in answering this?
    # Respond with one word only. (high, medium, low)

    # Context:
    # {combined_content}

    # Question: {query}
    # """
    # confidence = llm_generate(confidence_prompt, stream=False).strip()

    # if confidence.lower() == "low":
    #     expanded_query = rewrite_query(query)
    #     new_top_k = min(top_k + 2, 10)
    #     retrieved_docs = hybrid_retriever.retrieve(expanded_query, top_k=new_top_k)
    #     raw_docs = [doc for doc, _ in retrieved_docs]
    #     deduped_docs = deduper.deduplicate(raw_docs)
    #     combined_content = "\n".join(deduped_docs[:3])
    #     answer = llm_generate(
    #         f"Answer the question based on this context:\n{combined_content}\n\nQuestion: {expanded_query}",
    #         stream=False
    #     )
    # else:



    # Prompt With Memory

    answer = llm_generate(f""" You are a very helpful SAP Troubleshotting assistant
             Conversation So Far:
              {history_text}
            Context From Retrieved Text:
             {combined_content} 
            Current Question: 
            {query}
            If you do not know the answer from the provided context say:
            ` I do not know the answer. Can you please provide more context or more detailed information about the error `""", stream=False)
    # answer = llm_generate(f"""""" )
    
    SESSION_MEMORY[session_id].append({"query": query, "answer": answer})
    def generate_chunks(answer, chunk_size):
        for i in range(0, len(answer), chunk_size):
            yield answer[i:i+chunk_size].encode("utf-8")  # 🔹 must encode to bytes
            time.sleep(0.05)
            print(answer[i:i+chunk_size])
    return Response(stream_with_context(generate_chunks(answer ,5)), mimetype="application/octet-stream")

@app.route("/test-stream", methods=["POST"])
def test_stream():
    def generate():
        text = "Hello! This is a streaming test.Hello! This is a streaming test.Hello! This is a streaming test.Hello! This is a streaming test.Hello! This is a streaming test.Hello! This is a streaming test.Hello! This is a streaming test.Hello! This is a streaming test.Hello! This is a streaming test.Hello! This is a streaming test.Hello! This is a streaming test.Hello! This is a streaming test.Hello! This is a streaming test.Hello! This is a streaming test.Hello! This is a streaming test.Hello! This is a streaming test.Hello! This is a streaming test.Hello! This is a streaming test."
        for i in range(0, len(text), 5):
            yield text[i:i+5].encode("utf-8")
            time.sleep(0.1)
    return Response(generate(), mimetype="application/octet-stream")



# ----------------------------
# 7. Run Flask App
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)
