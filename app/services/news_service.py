import yfinance as yf
import logging
from typing import List, Dict, Any
from app.services.nlp_service import nlp_service

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        pass

    def get_ticker_news(self, ticker: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches live headlines for a ticker from yfinance and analyzes sentiment.
        """
        try:
            stock = yf.Ticker(ticker)
            news_data = stock.news
            
            if not news_data:
                logger.warning(f"No news found for ticker {ticker}")
                return []

            processed_news = []
            for item in news_data[:count]:
                headline = item.get("title", "")
                link = item.get("link", "")
                publisher = item.get("publisher", "Unknown")
                provider_publish_time = item.get("providerPublishTime", 0)

                # Analyze sentiment of the headline
                sentiment_result = nlp_service.analyze_sentiment(headline)
                
                processed_news.append({
                    "title": headline,
                    "link": link,
                    "publisher": publisher,
                    "timestamp": provider_publish_time,
                    "sentiment": sentiment_result.get("sentiment", {"label": "neutral", "score": 0.5}),
                    "summary": item.get("summary", headline) # yfinance news often has a 'summary' field
                })
            
            return processed_news

        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {str(e)}")
            return []

news_service = NewsService()
