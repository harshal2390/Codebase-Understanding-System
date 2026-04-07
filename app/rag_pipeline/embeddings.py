from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self):
        """
        Load embedding model
        """
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, texts):
        """
        Convert list of texts into embeddings
        """
        return self.model.encode(texts, show_progress_bar=True)