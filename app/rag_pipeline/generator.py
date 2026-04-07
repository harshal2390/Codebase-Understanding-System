import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class LLMGenerator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def generate(self, query, context):
        prompt = f"""
        You are a senior software engineer analyzing a codebase.

        STRICT RULES:
        1. Answer ONLY from the provided context
        2. DO NOT make assumptions
        3. DO NOT invent file names
        4. If information is missing, say "Not enough information"
        5. ONLY use given file paths

        CONTEXT:
        {context}

        QUESTION:
        {query}

        OUTPUT FORMAT:

        Explanation:
        - Explain ONLY what is present in code

        Relevant Files:
        - list ONLY files from context

        Code Snippets:
        - exact snippets from context

        Final Answer:
        """

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content