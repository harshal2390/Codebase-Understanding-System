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

        for r in results:
            file_path = r["metadata"]["file"].replace("data/repos/Wanderlust/", "").replace("\\", "/")
            content = r["content"]

            # =========================
            # MAIN CONTENT
            # =========================
            context_parts.append(f"""
FILE: {file_path}
CODE SNIPPET:
{content[:800]}
""")

            # =========================
            # GRAPH NEIGHBORS
            # =========================
            neighbors = self.graph.get_neighbors(file_path)

            for neighbor in neighbors[:2]:
                context_parts.append(f"[RELATED FILE] {neighbor}")

        final_context = "\n\n".join(context_parts)

        # =========================
        # DEBUG (PRINT ONCE ✅)
        # =========================
        print("\n================ DEBUG CONTEXT ================\n")
        print(final_context[:1500])
        print("\n==============================================\n")

        return final_context