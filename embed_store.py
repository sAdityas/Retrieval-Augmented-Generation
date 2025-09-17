import faiss, os , numpy as np
from sentence_transformers import SentenceTransformer

class EmbedStore:
    def __init__(self, model_name='all-MiniLM-L6-v2', index_path='faiss.index'):
        self.model = SentenceTransformer(model_name)
        self.docs = []
        self.embeddings = None
        self.index = None
        self.index_path = index_path

    def add_documents(self,docs):
        # Embed and store Documents in FAISS index.

        self.docs.extend(docs)
        new_embeddings = self.model.encode(docs).astype('float32')

        if self.embeddings is None:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack((self.embeddings, new_embeddings))
        
        self.build_index()
    def build_index(self):

        d = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(d)
        self.index.add(self.embeddings)

    def save(self):
        if self.index is not None:
            faiss.write_index(self.index,self.index_path)
            np.save('docs.npy',self.docs)

    def load(self):
        if os.path.exists(self.index_path) and os.path.exists('docs.npy'):
            self.index = faiss.read_index(self.index_path)
            self.docs = np.load('docs.npy', allow_pickle=True).tolist()
            print(f"Loaded {len(self.docs)} documents from {self.index_path}")
            

    def Search(self, query, top_k = 2):
        if self.index is None:
            raise ValueError("No Documents indexed. Add Documents First.")
        q_emb = self.model.encode([query]).astype('float32')
        D, I = self.index.search(q_emb, k=top_k)
        return [(self.docs[i], float(D[0][j])) for j, i in enumerate(I[0])]
    
