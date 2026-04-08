class ContextBuilder:
    def __init__(self, graph, vector_store, file_map):
        self.graph = graph
        self.vector_store = vector_store
        self.file_map = file_map

    # =========================
    # CLEAN PATH
    # =========================
    def clean_path(self, path):
        return path.replace("data/repos/Wanderlust/", "").replace("\\", "/")

    # =========================
    # 🔥 STEP 4.1: SCORING FUNCTION
    # =========================
    def score_node(self, node, intent, keywords):
        score = 0
        node_lower = node.lower()

        # Keyword match (most important)
        for kw in keywords:
            if kw in node_lower:
                score += 5

        # Intent-based scoring
        if intent == "flow":
            if "app" in node_lower or "main" in node_lower:
                score += 4
            if "route" in node_lower:
                score += 3

        if intent == "logic":
            if "controller" in node_lower or "service" in node_lower:
                score += 3

        # File importance
        if "model" in node_lower:
            score += 2
        if "controller" in node_lower:
            score += 2

        # Penalize noise
        if "init" in node_lower or "seed" in node_lower:
            score -= 5

        return score

    # =========================
    # MAIN BUILDER
    # =========================
    def build_context(self, query, query_embedding, entry_points, analysis, k=3):
        intent = analysis["intent"]
        keywords = analysis["keywords"]

        context_parts = []
        seen_files = set()

        # =========================
        # 🔥 STEP 4.4: LIMITS
        # =========================
        MAX_FILES = 5
        MAX_FLOW = 6
        MAX_RAG = 4

        # =========================
        # 🔥 STEP 4.2: SORT ENTRY POINTS
        # =========================
        entry_points = sorted(
            entry_points,
            key=lambda x: self.score_node(x, intent, keywords),
            reverse=True
        )

        # =========================
        # ENTRY POINTS
        # =========================
        context_parts.append("\n[ENTRY POINTS]\n")

        for ep in entry_points[:MAX_FILES]:
            if ep in seen_files:
                continue

            seen_files.add(ep)

            clean_ep = self.clean_path(ep)
            content = self.file_map.get(ep, "")

            context_parts.append(f"""
→ {clean_ep}

CODE:
{content[:400]}
""")

        # =========================
        # 🔥 STEP 4.3: FLOW + FILTERING
        # =========================
        context_parts.append("\n[FLOW TRACE]\n")

        for ep in entry_points[:3]:  # only top 2 entry points
            flow_nodes = self.graph.trace_flow(ep, depth=3)

            scored_flow = []

            for node in flow_nodes:
                score = self.score_node(node, intent, keywords)

                if score > 0:
                    scored_flow.append((node, score))

            # sort by score
            scored_flow = sorted(scored_flow, key=lambda x: x[1], reverse=True)

            for node, _ in scored_flow[:MAX_FLOW]:
                if node in seen_files:
                    continue

                seen_files.add(node)

                clean_node = self.clean_path(node)
                content = self.file_map.get(node, "")

                context_parts.append(f"""
→ {clean_node}

CODE:
{content[:350]}
""")

        # =========================
        # RAG CONTEXT
        # =========================
        semantic_results = self.vector_store.search(query_embedding, k=k)
        keyword_results = self.vector_store.keyword_search(query, k=2)

        results = semantic_results + keyword_results

        context_parts.append("\n[RETRIEVED CONTEXT]\n")

        for r in results[:MAX_RAG]:
            file_path = r["metadata"]["file"]

            if file_path in seen_files:
                continue

            seen_files.add(file_path)

            clean_path = self.clean_path(file_path)
            content = r["content"]

            context_parts.append(f"""
FILE: {clean_path}
CODE SNIPPET:
{content[:500]}
""")

        # =========================
        # FINAL
        # =========================
        final_context = "\n\n".join(context_parts)

        print("\n================ DEBUG CONTEXT ================\n")
        print(final_context[:1500])
        print("\n==============================================\n")

        return final_context