from app.ingestion.repo_loader import RepoLoader
from app.ingestion.file_parser import FileParser
from app.graph.dependency_graph import DependencyGraph
from app.rag_pipeline.splitter import CodeSplitter
from app.rag_pipeline.embeddings import EmbeddingModel
from app.rag_pipeline.vector_store import VectorStore
from app.rag_pipeline.context_builder import ContextBuilder
from app.rag_pipeline.generator import LLMGenerator
from app.rag_pipeline.intent_detector import IntentDetector
from app.rag_pipeline.entry_point_detector import EntryPointDetector
from app.rag_pipeline.entry_point_detector import EntryPointDetector




if __name__ == "__main__":
    repo_url = "https://github.com/GauravPatil1444/SkillUp.git"
    repo_name = repo_url.split("/")[-1].lower()

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
    # 🔥 NEW: FILE MAP (IMPORTANT)
    # =========================
    file_map = {
        item["file"]: item["content"]
        for item in parsed_data
    }

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

    if vector_store.load(repo_name):
        print("[INFO] Loaded existing FAISS index")
    else:
        vector_store.add_embeddings(vectors, texts, metadatas)
        vector_store.save(repo_name)

    # =========================
    # STEP 7: Setup RAG
    # =========================
    context_builder = ContextBuilder(
        graph_builder,
        vector_store,
        file_map   # 🔥 IMPORTANT FIX
    )
    intent_detector = IntentDetector()
    llm = LLMGenerator()
    entry_detector = EntryPointDetector(graph_builder)
    
    # =========================
    # STEP 8: Query loop
    # =========================
    while True:
        query = input("\nAsk a question (or 'exit'): ")

        if query.lower() == "exit":
            break

        analysis = intent_detector.analyze(query)

        print("\n[INTENT ANALYSIS]")
        print(analysis)
        
        entry_points = entry_detector.detect(analysis)

        print("\n[ENTRY POINTS]")
        for ep in entry_points:
            print(ep)

        # Generate query embedding
        query_embedding = embedder.embed([query])[0]

        # Build context (Hybrid + Graph + Flow)
        context = context_builder.build_context(query,query_embedding,entry_points,analysis)

        # Generate answer
        answer = llm.generate(query, context)

        print("\n💡 Answer:\n")
        print(answer)