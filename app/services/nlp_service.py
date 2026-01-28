from transformers import pipeline
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        self.classifier = None
        self.summarizer = None
        self.mock_mode = False
        
        try:
            # Attempt to load Financial BERT model
            logger.info("Loading FinBERT and Summarization models... This might take a moment.")
            self.classifier = pipeline("sentiment-analysis", model="ProsusAI/finbert")
            self.summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
            logger.info("NLP models loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load NLP models: {e}")
            logger.warning("Activating NLP Mock Mode.")
            self.mock_mode = True

    def _mock_summarize(self, text: str) -> str:
        """Simple mock summarizer that handles common abbreviations."""
        # Avoid splitting on common abbreviations
        clean_text = text.replace("Inc.", "Inc").replace("Corp.", "Corp").replace("LTD.", "LTD")
        sentences = clean_text.split('.')
        if len(sentences) > 1:
            first_sentence = sentences[0].strip()
            # Restore abbreviation if it was the first word
            if "Inc" in first_sentence: first_sentence = first_sentence.replace("Inc", "Inc.")
            return first_sentence + "."
        return text[:100] + "..."

    def summarize(self, text: str, max_length: int = 60, min_length: int = 10) -> str:
        """
        Summarizes long financial text.
        """
        if not text or len(text) < 50:
            return text

        if self.mock_mode or not self.summarizer:
            return self._mock_summarize(text)

        try:
            # Summarize (truncate input to 1024 tokens to avoid crash)
            results = self.summarizer(text[:1024], max_length=max_length, min_length=min_length, do_sample=False)
            return results[0]['summary_text']
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return self._mock_summarize(text)

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
