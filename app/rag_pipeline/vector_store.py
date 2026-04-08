import faiss
import numpy as np
import os
import pickle


class VectorStore:
    def __init__(self, dim: int):
        self.dim = dim

        # FAISS index
        self.index = faiss.IndexFlatL2(dim)

        # Stored data
        self.texts = []
        self.metadata = []

    # =========================
    # ADD EMBEDDINGS
    # =========================
    def add_embeddings(self, embeddings, texts, metadatas):
        embeddings = np.array(embeddings).astype("float32")

        if len(embeddings) == 0:
            print("[WARNING] No embeddings to add")
            return

        self.index.add(embeddings)

        self.texts.extend(texts)
        self.metadata.extend(metadatas)

    # =========================
    # SAVE (PER REPO ✅)
    # =========================
    def save(self, repo_name):
        os.makedirs("vector_db", exist_ok=True)

        index_path = f"vector_db/{repo_name}.faiss"
        store_path = f"vector_db/{repo_name}_store.pkl"

        # Save FAISS index
        faiss.write_index(self.index, index_path)

        # Save metadata + texts
        with open(store_path, "wb") as f:
            pickle.dump({
                "texts": self.texts,
                "metadata": self.metadata
            }, f)

        print(f"[INFO] Saved FAISS index for repo: {repo_name}")

    # =========================
    # LOAD (PER REPO ✅)
    # =========================
    def load(self, repo_name):
        index_path = f"vector_db/{repo_name}.faiss"
        store_path = f"vector_db/{repo_name}_store.pkl"

        if not os.path.exists(index_path):
            return False

        # Load FAISS
        self.index = faiss.read_index(index_path)

        # Load metadata
        if os.path.exists(store_path):
            with open(store_path, "rb") as f:
                data = pickle.load(f)
                self.texts = data.get("texts", [])
                self.metadata = data.get("metadata", [])
        else:
            print("[WARNING] Metadata missing, rebuilding needed")
            return False

        print(f"[INFO] Loaded FAISS index for repo: {repo_name}")
        return True

    # =========================
    # SEMANTIC SEARCH
    # =========================
    def search(self, query_embedding, k=5):
        if len(self.texts) == 0:
            return []

        query_embedding = np.array([query_embedding]).astype("float32")

        distances, indices = self.index.search(query_embedding, k)

        results = []

        for idx in indices[0]:
            if 0 <= idx < len(self.texts):
                results.append({
                    "content": self.texts[idx],
                    "metadata": self.metadata[idx]
                })

        return results

    # =========================
    # KEYWORD SEARCH (IMPROVED 🔥)
    # =========================
    def keyword_search(self, query, k=3):
        query_words = query.lower().split()

        scored = []

        for i, text in enumerate(self.texts):
            text_lower = text.lower()

            # score based on keyword matches
            score = sum(1 for w in query_words if w in text_lower)

            if score > 0:
                scored.append((score, i))

        # sort by score descending
        scored.sort(reverse=True)

        results = []

        for _, idx in scored[:k]:
            results.append({
                "content": self.texts[idx],
                "metadata": self.metadata[idx]
            })

        return results