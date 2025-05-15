# obligation_extractor.py

import re
from typing import List

from legal_doc_analyzer.utils.llm_utils import call_llm  # if using LLM fallback

class ObligationExtractorAgent:
    def __init__(self, use_llm_fallback: bool = False):
        self.use_llm = use_llm_fallback
        self.patterns = [
            r"\bshall\b[^.]*\.",
            r"\bmust\b[^.]*\.",
            r"\bagrees to\b[^.]*\.",
            r"\bis required to\b[^.]*\.",
            r"\bis obligated to\b[^.]*\.",
            r"\bwill\b[^.]*\.",
        ]

    def extract(self, clause: str) -> List[str]:
        obligations = []

        # Run regex patterns
        for pattern in self.patterns:
            matches = re.findall(pattern, clause, flags=re.IGNORECASE)
            obligations.extend(matches)

        # Optional: Use LLM for fallback
        if self.use_llm and not obligations:
            prompt = f"Extract all obligations (duties, responsibilities) from the following clause:\n\n{clause}"
            llm_response = call_llm(prompt)
            if llm_response:
                obligations.append(llm_response.strip())

        return obligations
