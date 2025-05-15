# summarizer_agent.py

import os
from legal_doc_analyzer.utils.logger import get_logger

logger = get_logger("SummarizerAgent")

class SummarizerAgent:
    def __init__(self):
        self.use_llm = os.getenv("OPENAI_API_KEY") is not None
        if self.use_llm:
            try:
                import openai
                self.openai = openai
                self.openai.api_key = os.getenv("OPENAI_API_KEY")
                logger.info("✅ SummarizerAgent: OpenAI API loaded.")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize OpenAI: {e}")
                self.use_llm = False

    def heuristic_summary(self, clause: str) -> str:
        # Naive heuristic: return first sentence
        summary = clause.strip().split(".")[0]
        return summary + "." if summary and not summary.endswith('.') else summary

    def summarize(self, clause: str) -> str:
        if not clause.strip():
            return "No content provided."

        if self.use_llm:
            try:
                response = self.openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a legal expert."},
                        {"role": "user", "content": f"Summarize the following clause in one sentence:\n\n{clause}"}
                    ],
                    temperature=0.3,
                    max_tokens=100
                )
                summary = response.choices[0].message.content.strip()
                return summary
            except Exception as e:
                logger.warning(f"🔁 LLM failed. Falling back to heuristics. Error: {e}")
        
        # Fallback
        return self.heuristic_summary(clause)
