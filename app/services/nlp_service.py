from transformers import pipeline
import logging
from typing import Dict, Any, List, Optional
from app.services.news_scraper_service import news_scraper_service

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
            
            # Use text-generation or text2text-generation if summarization is missing in v5.0.0
            try:
                self.summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
            except Exception:
                logger.warning("Summarization task not found, trying text-generation fallback.")
                self.summarizer = pipeline("text-generation", model="sshleifer/distilbart-cnn-12-6")
            
            logger.info("NLP models loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load NLP models: {e}")
            logger.warning("Activating NLP Mock Mode.")
            self.mock_mode = True

    def _chunk_text(self, text: str, max_chunk_size: int = 1000) -> List[str]:
        """
        Splits text into chunks of approximately max_chunk_size, without breaking sentences.
        """
        # Simple sentence-based chunking
        # In a production app, we might use NLTK or Spacy for more robust sentence splitting
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip() + ". "
            if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    def _mock_summarize(self, text: str) -> str:
        """Enhanced mock summarizer that takes key parts of multiple chunks."""
        chunks = self._chunk_text(text, max_chunk_size=500)
        summary_parts = []
        for chunk in chunks[:3]: # Take first part of up to 3 chunks
            clean_text = chunk.replace("Inc.", "Inc").replace("Corp.", "Corp").replace("LTD.", "LTD")
            sentences = clean_text.split('.')
            if sentences:
                summary_parts.append(sentences[0].strip() + ".")
        
        return " ".join(summary_parts)

    def summarize(self, text: str, max_length: int = 80, min_length: int = 20) -> str:
        """
        Summarizes long financial text using a map-reduce style chunking approach.
        """
        if not text or len(text) < 150:
            return text

        if self.mock_mode or not self.summarizer:
            return self._mock_summarize(text)

        try:
            # Chunk the text (FinBERT/BART usually have 1024 token limits)
            # We use 1800 chars as a safe limit for DistilBART
            chunks = self._chunk_text(text, max_chunk_size=1800)
            
            chunk_summaries = []
            for chunk in chunks:
                # Summarize each chunk
                res = self.summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
                # Handle both 'summary_text' (summarization task) and 'generated_text' (text-generation task)
                summary_chunk = res[0].get('summary_text') or res[0].get('generated_text')
                chunk_summaries.append(summary_chunk)
            
            # Combine summaries
            combined_summary = " ".join(chunk_summaries)
            
            # If the result is still very long, summarize the summary
            if len(chunks) > 1 and len(combined_summary) > 500:
                final_res = self.summarizer(combined_summary[:2000], max_length=150, min_length=50, do_sample=False)
                return final_res[0].get('summary_text') or final_res[0].get('generated_text')
            
            return combined_summary

        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return self._mock_summarize(text)

    def summarize_article(self, url: str) -> Dict[str, Any]:
        """
        Scrapes an article from a URL and returns a summary.
        """
        logger.info(f"Summarizing article from URL: {url}")
        text = news_scraper_service.scrape_article(url)
        
        if not text:
            logger.warning(f"Could not extract text from {url}")
            return {
                "url": url,
                "summary": None,
                "status": "error",
                "message": "Could not extract content from the provided URL. The site might be blocking or uses unsupported dynamic content."
            }
            
        summary = self.summarize(text)
        
        return {
            "url": url,
            "summary": summary,
            "status": "success",
            "length_extracted": len(text),
            "summary_length": len(summary)
        }

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
