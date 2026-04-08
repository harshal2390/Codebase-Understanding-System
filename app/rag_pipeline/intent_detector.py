import re


class IntentDetector:
    def __init__(self):
        """
        Generic intent patterns (domain-independent)
        """
        self.intent_patterns = {
            "flow": [
                "how", "flow", "working", "process", "pipeline"
            ],
            "location": [
                "where", "located", "find", "which file"
            ],
            "logic": [
                "why", "logic", "reason", "behind"
            ],
            "data_flow": [
                "data flow", "data pass", "data movement"
            ],
            "dependency": [
                "dependency", "depends", "relationship", "connected"
            ],
            "usage": [
                "how to use", "usage", "example"
            ]
        }

    # =========================
    # CLEAN QUERY
    # =========================
    def preprocess(self, query):
        query = query.lower()
        query = re.sub(r"[^a-z0-9\s]", "", query)
        return query

    # =========================
    # DETECT INTENT
    # =========================
    def detect_intent(self, query):
        query_clean = self.preprocess(query)

        scores = {}

        for intent, keywords in self.intent_patterns.items():
            score = sum(1 for word in keywords if word in query_clean)
            scores[intent] = score

        # pick highest scoring intent
        intent = max(scores, key=scores.get)

        # fallback if nothing matched
        if scores[intent] == 0:
            intent = "general"

        return intent

    # =========================
    # EXTRACT KEYWORDS
    # =========================
    def extract_keywords(self, query):
        query_clean = self.preprocess(query)

        words = query_clean.split()

        # remove common stopwords
        stopwords = {
            "how", "is", "the", "in", "this", "project",
            "what", "where", "does", "do", "a", "an",
            "if", "by", "and", "can", "it", "that", "user1", "user2"
        }

        keywords = [w for w in words if w not in stopwords]

        return keywords

    # =========================
    # FINAL OUTPUT
    # =========================
    def analyze(self, query):
        intent = self.detect_intent(query)
        keywords = self.extract_keywords(query)

        return {
            "intent": intent,
            "keywords": keywords
        }