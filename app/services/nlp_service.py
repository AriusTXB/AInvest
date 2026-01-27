from transformers import pipeline
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        self.classifier = None
        self.mock_mode = False
        
        try:
            # Attempt to load Financial BERT model
            # This might fail if no internet or low resources
            logger.info("Loading FinBERT model... This might take a moment.")
            self.classifier = pipeline("sentiment-analysis", model="ProsusAI/finbert")
            logger.info("FinBERT loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load FinBERT: {e}")
            logger.warning("Activating NLP Mock Mode.")
            self.mock_mode = True

    def _mock_analyze(self, text: str) -> Dict[str, Any]:
        """Simple keyword-based mock analysis."""
        text_lower = text.lower()
        if any(w in text_lower for w in ["rise", "growth", "profit", "up", "bull", "high"]):
            return {"label": "positive", "score": 0.85}
        elif any(w in text_lower for w in ["fall", "loss", "down", "bear", "low", "risk"]):
            return {"label": "negative", "score": 0.92}
        else:
            return {"label": "neutral", "score": 0.50}

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyzes text for financial sentiment (Positive, Negative, Neutral).
        """
        if not text:
            return {"error": "No text provided"}

        if self.mock_mode or not self.classifier:
            return {
                "sentiment": self._mock_analyze(text),
                "is_mock": True,
                "model": "KeywordHeuristic"
            }

        try:
            # Run model
            # Truncate text to 512 tokens approx to avoid model crash
            results = self.classifier(text[:512])
            # Result format: [{'label': 'positive', 'score': 0.9}]
            top_result = results[0]
            
            return {
                "sentiment": top_result,
                "is_mock": False,
                "model": "ProsusAI/finbert"
            }
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return {
                "sentiment": self._mock_analyze(text),
                "is_mock": True,
                "error_fallback": str(e)
            }

nlp_service = NLPService()
