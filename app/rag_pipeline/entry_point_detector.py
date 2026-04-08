import os


class EntryPointDetector:
    def __init__(self, graph):
        self.graph = graph

    # =========================
    # DETECT ENTRY POINTS
    # =========================
    def detect(self, analysis):
        intent = analysis["intent"]
        keywords = analysis["keywords"]

        candidates = []

        for node, attr in self.graph.graph.nodes(data=True):

            node_type = attr.get("type")

            # 🔥 ONLY ALLOW THESE TYPES
            if node_type not in ["file", "route"]:
                continue

            node_lower = node.lower()
            score = 0

            # Keyword match
            for kw in keywords:
                if kw in node_lower:
                    score += 5

            # File importance
            if "app" in node_lower or "main" in node_lower:
                score += 4

            if "route" in node_lower:
                score += 3

            if "controller" in node_lower:
                score += 2

            # Intent-based
            if intent == "flow":
                if "app" in node_lower or "index" in node_lower:
                    score += 3

            # Penalize noise
            if "init" in node_lower or "seed" in node_lower:
                score -= 5

            if score > 0:
                candidates.append((node, score))

        # Sort
        candidates = sorted(candidates, key=lambda x: x[1], reverse=True)

        unique = []
        seen = set()

        for node, _ in candidates:
            if node not in seen:
                unique.append(node)
                seen.add(node)

        return unique[:5]