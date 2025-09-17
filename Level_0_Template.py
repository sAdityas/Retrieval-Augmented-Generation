from sentence_transformers import SentenceTransformer
import faiss, numpy as np

# Prepare Data
docs = [
    "The Moon affects tides on Earth.",
    "Mars is known as the Red Planet.",
    "Python is a programming language.",
    "The Hubble Space Telescope has provided astronomers with breathtaking images of galaxies and nebulae since its launch in 1990.",
    "A supernova occurs when a massive star explodes at the end of its life cycle, briefly outshining entire galaxies.",
    "Python is a versatile programming language widely used for web development, data analysis, and artificial intelligence, Data Science",
    "“Hello, World!” is often the first program new developers write to test their coding setup in any programming language.",
    "Honey never spoils because its low moisture content and acidic pH prevent the growth of bacteria and microorganisms."
]

# Embed
model = SentenceTransformer('all-MiniLM-L6-v2')
embs = model.encode(docs).astype('float32')


# Create FAISS Index
d = embs.shape[1]
index = faiss.IndexFlatL2(d)
index.add(embs)

# Query
query = "Which language is used for data science?"
q_emb = model.encode([query]).astype('float32')
D, I = index.search(q_emb, k=2)
print("Top Docs: ",[ docs[i] for i in I[0]])


def llm_generate(prompt: str) -> str:
    import ollama
    response = ollama.chat(model='llama3', messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]
