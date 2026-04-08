class ContextBuilder:
    def __init__(self, graph, vector_store):
        self.graph = graph
        self.vector_store = vector_store

    def build_context(self, query, query_embedding, k=3):
        """
        Hybrid RAG + Graph Context
        """

        # =========================
        # 1. SEMANTIC SEARCH
        # =========================
        semantic_results = self.vector_store.search(query_embedding, k=k)

        # =========================
        # 2. KEYWORD SEARCH
        # =========================
        keyword_results = self.vector_store.keyword_search(query, k=2)

        # Merge results
        results = semantic_results + keyword_results

        context_parts = []
        seen_files = set()   # 🔥 FIX: remove duplicates

        for r in results:
            original_path = r["metadata"]["file"]

            # 🔥 FIX: avoid duplicate files
            if original_path in seen_files:
                continue
            seen_files.add(original_path)

            # Clean path for display only
            clean_path = original_path.replace("data/repos/Wanderlust/", "").replace("\\", "/")

            content = r["content"]

            # =========================
# FLOW TRACING (NEW 🔥)
# =========================
        flow_nodes = self.graph.trace_flow(original_path, depth=2)

        context_parts.append("\n[FLOW TRACE]\n")

        for node in flow_nodes[:5]:
            context_parts.append(f"→ {node}")

            # =========================
            # MAIN CONTENT
            # =========================
            context_parts.append(f"""
FILE: {clean_path}
CODE SNIPPET:
{content[:800]}
""")

            # =========================
            # GRAPH NEIGHBORS (USE ORIGINAL PATH)
            # =========================
            neighbors = self.graph.get_neighbors(original_path)

            for neighbor in neighbors[:2]:
                context_parts.append(f"[RELATED FILE] {neighbor}")

        final_context = "\n\n".join(context_parts)

        # =========================
        # DEBUG
        # =========================
        print("\n================ DEBUG CONTEXT ================\n")
        print(final_context[:1500])
        print("\n==============================================\n")

        return final_context