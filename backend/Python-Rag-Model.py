# Flask API for Python RAG with PDF
import os
import pickle
import hashlib
import time
import fitz  # PyMuPDF for PDF reading
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
# 2. Memory
# ----------------------------
SESSION_MEMORY = defaultdict(lambda: deque(maxlen=5))

# ----------------------------
# 3. Environment
# ----------------------------
TOP_K = int(os.getenv("TOP_K", 5))
MAX_CHARS = int(os.getenv("MAX_CHARS", 500))
OVERLAP = int(os.getenv("OVERLAP", 50))
ALPHA = float(os.getenv("ALPHA", 0.8))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ----------------------------
# 4. Helpers
# ----------------------------
def file_hash(path):
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def load_pdf(file_path):
    """Load PDF and return list of text blocks."""
    doc = fitz.open(file_path)
    raw_text = []
    for page in doc:
        text = page.get_text("text")
        raw_text.append(text)
    return raw_text

def rewrite_query(user_query):
    prompt = f"""
    You are a query rewriting assistant.
    Rewrite this Python query into a detailed question.
    Query: {user_query}
    """
    return llm_generate(prompt, stream=False).strip()

def adaptive_top_k(rewritten, base_k=TOP_K, max_k=10):
    words = len(rewritten.split())
    if words < 3:
        return base_k
    elif words < 6:
        return base_k + 2
    else:
        return min(max_k, base_k + 2)

# ----------------------------
# 5. Load PDF and chunk
# ----------------------------
pdf_file = "Python_Guide.pdf"
cache_file = "cached_chunks.pkl"
hash_file = "pdf_hash.txt"

pdf_md5 = file_hash(pdf_file)
rebuild_cache = True

if os.path.exists(cache_file) and os.path.exists(hash_file):
    with open(hash_file, "r") as f:
        cached_hash = f.read().strip()
    if cached_hash == pdf_md5:
        rebuild_cache = False

if rebuild_cache:
    print("📄 Chunking PDF...")
    raw_texts = load_pdf(pdf_file)
    chunked_docs = chunk_documents(raw_texts, max_char=MAX_CHARS, overlap=OVERLAP)
    with open(cache_file, "wb") as f:
        pickle.dump(chunked_docs, f)
    with open(hash_file, "w") as f:
        f.write(pdf_md5)
    print(f"✅ Cached {len(chunked_docs)} chunks and updated hash.")
else:
    print("🔄 Loading cached chunks...")
    with open(cache_file, "rb") as f:
        chunked_docs = pickle.load(f)

texts = [c["text"] for c in chunked_docs]

# ----------------------------
# 6. Setup Retrieval
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
# 7. RAG Endpoint
# ----------------------------
@app.route("/rag-query", methods=["POST"])
def rag_query():
    data = request.json
    query = data.get("query")
    session_id = data.get("session_id", "default")
    if not query:
        return jsonify({"error": "Missing query"}), 400

    # Memory
    history = list(SESSION_MEMORY[session_id])
    history_text = "\n".join([f"User: {h['query']} \nBot: {h['answer']}" for h in history])

    # Retrieval
    top_k = adaptive_top_k(query)
    retrieved_docs = hybrid_retriever.retrieve(query, top_k=top_k)
    raw_docs = [doc for doc, _ in retrieved_docs]
    deduped_docs = deduper.deduplicate(raw_docs)
    combined_content = "\n".join(deduped_docs[:5]).strip()  # top 5 chunks
    print(combined_content)
    # Decide prompt based on whether context exists
    if combined_content:
        role_prompt = """
            You are a Python Programming Assistant.

            Answer ONLY using the retrieved context. 
            If the retrieved context does not contain the answer, reply:
            "I do not know the answer from the provided context."
            """
    else:
        # Allow LLM to generate safe Python code
        role_prompt = """
            You are a Python Programming Assistant.

            The retrieved context does not contain an answer. 
            Generate a safe Python program or explanation using your general knowledge.
            """

    answer = llm_generate(f"""
{role_prompt}

Conversation so far:
{history_text}

Retrieved context:
{combined_content}

Current user question:
{query}

Final Answer:
""", stream=False)

    SESSION_MEMORY[session_id].append({"query": query, "answer": answer})

    # Stream response
    def generate_chunks(answer, chunk_size=50):
        for i in range(0, len(answer), chunk_size):
            yield answer[i:i+chunk_size].encode("utf-8")
            time.sleep(0.01)
    return Response(stream_with_context(generate_chunks(answer)), mimetype="application/octet-stream")


# ----------------------------
# 8. Run Flask App
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)
