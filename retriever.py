# retriever.py
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
class Retriever:
    def __init__(self, docs):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.documents = list(docs) # Ensure documents is a list
        self.embeddings = np.array(self.model.encode(docs)).astype("float32")
        self.d = self.embeddings.shape[1]

        self.index = faiss.IndexFlatL2(self.d)
        self.index.add(self.embeddings)

    def retrieve(self, query, top_k=5):
        q_emb = self.model.encode([query]).astype("float32")
        D, I = self.index.search(q_emb, k=top_k)
        return [(self.documents[i], float(D[0][j])) for j, i in enumerate(I[0])]

    def save(self):
        faiss.write_index(self.index, "faiss.index")
        np.save("docs.npy", self.documents)

    def load(self):
        self.index = faiss.read_index("faiss.index")
        self.documents = np.load("docs.npy", allow_pickle=True).tolist()

    def get_all_docs(self):  # <-- Added for Level 3 debugging
        return self.documents
