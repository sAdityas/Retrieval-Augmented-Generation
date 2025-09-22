# reRanker.py
from sentence_transformers import CrossEncoder

class reRanker:
    def __init__(self):
        self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def rerank(self, query, docs):
        pairs = [(query, doc) for doc in docs]
        scores = self.model.predict(pairs)

        # Sort by score (descending)
        reranked = [doc for _, doc in sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)]
        return reranked, scores
