# consolidator_agent.py

from typing import List, Dict

class ConsolidatorAgent:
    def consolidate(
        self,
        clauses_data: List[Dict],
        missing_clauses: List[str],
        obligations: List[str],
    ) -> Dict:
        return {
            "summary": {
                "total_clauses": len(clauses_data),
                "missing_clauses": missing_clauses,
                "total_obligations": len(obligations),
            },
            "details": clauses_data,
        }
