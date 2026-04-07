import faiss
import numpy as np
import os
import pickle

class VectorStore:
    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)

        self.texts = []
        self.metadata = []

    # =========================
    # ADD EMBEDDINGS
    # =========================
    def add_embeddings(self, embeddings, texts, metadatas):
        embeddings = np.array(embeddings).astype("float32")

        self.index.add(embeddings)

        self.texts.extend(texts)
        self.metadata.extend(metadatas)

    # =========================
    # SAVE / LOAD
    # =========================
    def save(self, path="vector_db/index.faiss"):
        os.makedirs("vector_db", exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, path)

        # Save metadata + texts
        with open("vector_db/store.pkl", "wb") as f:
            pickle.dump({
                "texts": self.texts,
                "metadata": self.metadata
            }, f)


    def load(self, path="vector_db/index.faiss"):
        if os.path.exists(path):
            self.index = faiss.read_index(path)

            # Load metadata + texts
            try:
                with open("vector_db/store.pkl", "rb") as f:
                    data = pickle.load(f)
                    self.texts = data["texts"]
                    self.metadata = data["metadata"]
            except:
                print("[WARNING] Metadata not found, rebuilding required")
                return False

            return True

        return False
    # =========================
    # SEMANTIC SEARCH
    # =========================
    def search(self, query_embedding, k=5):
        query_embedding = np.array([query_embedding]).astype("float32")

        distances, indices = self.index.search(query_embedding, k)

        results = []

        for idx in indices[0]:
            if idx < len(self.texts):
                results.append({
                    "content": self.texts[idx],
                    "metadata": self.metadata[idx]
                })

        return results

    # =========================
    # KEYWORD SEARCH (NEW 🔥)
    # =========================
    def keyword_search(self, query, k=3):
        results = []

        query_lower = query.lower()

        for i, text in enumerate(self.texts):
            if query_lower in text.lower():
                results.append({
                    "content": text,
                    "metadata": self.metadata[i]
                })

        return results[:k]