from app.ingestion.repo_loader import RepoLoader
from app.ingestion.file_parser import FileParser
from app.graph.dependency_graph import DependencyGraph
from app.rag_pipeline.splitter import CodeSplitter
from app.rag_pipeline.embeddings import EmbeddingModel
from app.rag_pipeline.vector_store import VectorStore
from app.rag_pipeline.context_builder import ContextBuilder
from app.rag_pipeline.generator import LLMGenerator

if __name__ == "__main__":
    repo_url = "https://github.com/harshal2390/Wanderlust"

    # =========================
    # STEP 1: Clone repo
    # =========================
    loader = RepoLoader(repo_url)
    repo_path = loader.clone_repo()

    # =========================
    # STEP 2: Parse files
    # =========================
    parser = FileParser(repo_path)
    parsed_data = parser.parse_files()

    print(f"[INFO] Parsed files: {len(parsed_data)}")

    # =========================
    # STEP 3: Build graph
    # =========================
    graph_builder = DependencyGraph()
    graph_builder.build_graph(parsed_data)
    graph_builder.print_summary()

    # =========================
    # STEP 4: Split into chunks
    # =========================
    splitter = CodeSplitter()
    chunks = splitter.split_documents(parsed_data)

    print(f"[INFO] Total chunks: {len(chunks)}")

    # =========================
    # STEP 5: Generate embeddings
    # =========================
    embedder = EmbeddingModel()

    texts = [c["content"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    vectors = embedder.embed(texts)

    print("[INFO] Embeddings generated")

    # =========================
    # STEP 6: Store in FAISS
    # =========================
    dim = len(vectors[0])

    vector_store = VectorStore(dim)

    if vector_store.load():
        print("[INFO] Loaded existing FAISS index")
    else:
        vector_store.add_embeddings(vectors, texts, metadatas)
        vector_store.save()
        print("[INFO] Created and saved FAISS index")
    # =========================
    # STEP 7: Query loop
    # =======================
    context_builder = ContextBuilder(graph_builder, vector_store)
    llm = LLMGenerator()

    while True:
        query = input("\nAsk a question (or 'exit'): ")

        if query == "exit":
            break

        query_embedding = embedder.embed([query])[0]

        context = context_builder.build_context(query, query_embedding)


        answer = llm.generate(query, context)

        print("\n💡 Answer:\n")
        print(answer)