# risk_analyzer_agent.py
class RiskAnalyzerAgent:
    def __init__(self):
        # Simple list of risky keywords (expand later)
        self.risky_keywords = ["penalty", "termination", "liability", "indemnify"]

    def analyze(self, clause):
        lower_clause = clause.lower()
        for keyword in self.risky_keywords:
            if keyword in lower_clause:
                return "⚠️ Risky"
        return "✅ Safe"
