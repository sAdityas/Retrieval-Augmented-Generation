# semantic_deduplicate.py
from sentence_transformers import SentenceTransformer, util

class SemanticDeduplicate:
    def __init__(self, threshold=0.9):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.threshold = threshold

    def deduplicate(self, docs):
        """
        Removes semantically similar duplicates.
        """
        embeddings = self.model.encode(docs, convert_to_tensor=True)
        unique_docs = []
        seen = []

        for i, emb in enumerate(embeddings):
            is_duplicate = False
            for j in seen:
                sim = util.cos_sim(emb, embeddings[j])
                if sim > self.threshold:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_docs.append(docs[i])
                seen.append(i)

        return unique_docs
