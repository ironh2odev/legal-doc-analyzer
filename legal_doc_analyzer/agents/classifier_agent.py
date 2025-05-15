# legal_doc_analyzer/agents/classifier_agent.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os
import logging

logger = logging.getLogger(__name__)

class ClauseClassifierAgent:
    def __init__(self):
        try:
            model_name = "nlpaueb/legal-bert-base-uncased"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                num_labels=len(self.get_label_map()),
            )
            self.label_map = self.get_label_map()
            self.use_transformer = True
            logger.info("✅ LegalBERT loaded successfully.")
        except Exception as e:
            logger.warning("⚠️ LegalBERT not available. Falling back to heuristics.")
            self.use_transformer = False

    def classify(self, clause_text: str) -> str:
        if self.use_transformer:
            return self._classify_with_model(clause_text)
        else:
            return self._classify_with_heuristics(clause_text)

    def _classify_with_model(self, clause_text: str) -> str:
        inputs = self.tokenizer(clause_text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            logits = self.model(**inputs).logits
            predicted_label = torch.argmax(logits, dim=1).item()
            return self.label_map.get(predicted_label, "unknown")

    def _classify_with_heuristics(self, clause_text: str) -> str:
        clause_text = clause_text.lower()
        if "termination" in clause_text:
            return "termination"
        elif "confidential" in clause_text or "nondisclosure" in clause_text:
            return "confidentiality"
        elif "indemnify" in clause_text or "liability" in clause_text:
            return "indemnity"
        elif "governing law" in clause_text or "jurisdiction" in clause_text:
            return "governing law"
        elif "force majeure" in clause_text:
            return "force majeure"
        elif "payment" in clause_text:
            return "payment terms"
        elif "dispute" in clause_text or "arbitration" in clause_text:
            return "dispute resolution"
        else:
            return "unknown"

    def get_label_map(self):
        # You can customize this as needed
        return {
            0: "termination",
            1: "confidentiality",
            2: "indemnity",
            3: "governing law",
            4: "force majeure",
            5: "payment terms",
            6: "dispute resolution",
        }
