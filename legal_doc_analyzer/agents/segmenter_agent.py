import re

class ClauseSegmenterAgent:
    def process(self, text):
        # Example: split on numbered clauses like "1.", "2.", etc.
        clauses = re.split(r"\n\d+\.\s", text)
        return [clause.strip() for clause in clauses if clause.strip()]
