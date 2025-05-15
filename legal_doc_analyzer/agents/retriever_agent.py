# risk_analyzer_agent.py

from typing import Literal
import re
from legal_doc_analyzer.utils.llm_utils import call_llm  # Optional fallback to GPT

RiskLevel = Literal["✅ Safe", "⚠️ Medium Risk", "❌ High Risk"]

class RiskAnalyzerAgent:
    def __init__(self, use_llm_fallback: bool = False):
        self.use_llm = use_llm_fallback

        self.high_risk_keywords = [
            "indemnify", "hold harmless", "penalty", "termination without cause", 
            "liquidated damages", "waiver of rights"
        ]
        self.medium_risk_keywords = [
            "non-compete", "non-solicitation", "exclusive", "binding arbitration",
            "governing law", "dispute resolution", "late fees"
        ]

    def analyze(self, clause: str) -> RiskLevel:
        clause_lower = clause.lower()

        if any(kw in clause_lower for kw in self.high_risk_keywords):
            return "❌ High Risk"
        elif any(kw in clause_lower for kw in self.medium_risk_keywords):
            return "⚠️ Medium Risk"
        else:
            if self.use_llm:
                prompt = (
                    "Rate the following legal clause as one of: Safe, Medium Risk, or High Risk.\n\n"
                    f"Clause: {clause}\n\n"
                    "Respond with only one of the following:\n"
                    "- ✅ Safe\n- ⚠️ Medium Risk\n- ❌ High Risk"
                )
                response = call_llm(prompt)
                if response:
                    return response.strip()

            return "✅ Safe"
