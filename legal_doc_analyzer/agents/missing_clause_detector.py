# missing_clause_detector.py

from typing import List

class MissingClauseDetectorAgent:
    def __init__(self):
        # Standard clauses often expected in legal documents
        self.required_clauses = {
            "confidentiality",
            "termination",
            "governing law",
            "indemnity",
            "force majeure",
            "dispute resolution",
            "payment terms",
            "intellectual property",
        }

    def detect(self, clauses: List[str]) -> List[str]:
        found = set()

        for clause in clauses:
            for required in self.required_clauses:
                if required.lower() in clause.lower():
                    found.add(required)

        missing = self.required_clauses - found
        return sorted(missing)
