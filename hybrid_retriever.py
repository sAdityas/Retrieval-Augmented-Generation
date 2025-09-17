import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ALPHA = float(os.getenv("ALPHA", 0.8))
TOP_K = int(os.getenv("TOP_K", 5))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

class HybridRetriever:
    def __init__(self, faiss_retriever, bm25_retriever, alpha=ALPHA):
        self.faiss_retriever = faiss_retriever
        self.bm25_retriever = bm25_retriever
        self.alpha = alpha

    def retrieve(self,query,top_k=TOP_K,DEBUG=DEBUG):
        faiss_result = self.faiss_retriever.retrieve(query,top_k)
        bm25_result = self.bm25_retriever.retrieve(query,top_k)
        

        scores_dict = {}

        for doc, score in faiss_result:
            scores_dict[doc] = scores_dict.get(doc,0) + self.alpha * score
        for doc, score in bm25_result:
            scores_dict[doc] = scores_dict.get(doc,0) + (1-self.alpha) * score
        merged_result = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)

        # if DEBUG:
        #     print(f"FAISS Result: {faiss_result}")
        #     print(f"BM25 Result: {bm25_result}")
        #     print(f"Merged Result: {merged_result}")
        return merged_result[:top_k]