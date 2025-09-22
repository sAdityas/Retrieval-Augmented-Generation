from rank_bm25 import BM25Okapi

class BM25Retriever:
    def __init__(self,docs):
        self.docs = docs
        tokenized_docs = [doc.split(' ') for doc in docs]
        self.bm25 = BM25Okapi(tokenized_docs)

    def retrieve(self,query,top_k=5):
        tokenized_query = query.split(" ")
        scores = self.bm25.get_scores(tokenized_query)
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [(self.docs[i], scores[i]) for i in ranked_indices]
    