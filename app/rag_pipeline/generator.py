import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class LLMGenerator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def generate(self, query, context):
        prompt = f"""
        You are a senior software engineer analyzing a real-world codebase.

        Your job is to explain how the system works using ONLY the provided context.

        =========================
        STRICT RULES (VERY IMPORTANT)
        =========================
        1. DO NOT make assumptions
        2. DO NOT invent files or logic
        3. ONLY use the provided context
        4. If something is missing → say "Not enough information"
        5. Always reference actual file paths
        6. Prefer step-by-step explanation of flow
        7.Use FLOW TRACE section to explain step-by-step execution

        =========================
        CONTEXT
        =========================
        {context}

        =========================
        QUESTION
        =========================
        {query}

        =========================
        OUTPUT FORMAT (FOLLOW STRICTLY)
        =========================

        🔹 Explanation:
        - High-level explanation of feature

        🔹 Flow (Step-by-step):
        1. Where request starts
        2. Which route/controller handles it
        3. What logic is applied
        4. How data flows
        5. Final result

        🔹 Relevant Files:
        - file_path → what it does

        🔹 Code Snippets:
        - show ONLY important parts (short snippets)

        🔹 Final Answer:
        - concise summary in 2-3 lines

        =========================
        IMPORTANT NOTES
        =========================
        - Focus on FLOW, not just description
        - Connect files logically
        - Explain like teaching a developer
        """

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content