from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialService:
    def __init__(self):
        self.mock_mode = True 
        # In a real scenario, we might toggle this based on env vars
        # self.mock_mode = os.getenv("USE_MOCK_SOCIAL", "true").lower() == "true"

    def _get_mock_tweets(self) -> List[Dict[str, Any]]:
        """Returns curated tweets for the demo context."""
        
        # Dynamic dates to make the demo look fresh
        now = datetime.now()
        
        return [
            {
                "id": "1",
                "author": "Michael Burry Archive",
                "handle": "@BurryArchive",
                "content": "Inflation is sticky. The Fed is cornered. Sell.",
                "timestamp": (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
                "sentiment_score": -0.8, # Pre-calculated for mock
                "sentiment_label": "negative"
            },
            {
                "id": "2",
                "author": "Bill Ackman",
                "handle": "@BillAckman",
                "content": "The underlying fundamentals of the US economy remain strong despite the noise.",
                "timestamp": (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
                "sentiment_score": 0.6,
                "sentiment_label": "positive"
            },
            {
                "id": "3",
                "author": "Jim Cramer",
                "handle": "@jimcramer",
                "content": "Tech stocks are a SCREAMING BUY right now! Don't miss the boat!",
                "timestamp": (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),
                "sentiment_score": 0.9, 
                "sentiment_label": "positive" 
                # Note: Experienced traders might interpret Cramer Inverse, but NLP sees positive
            },
             {
                "id": "4",
                "author": "Unusual Whales",
                "handle": "@unusual_whales",
                "content": "Massive bearish flow detected on SPY puts expiring next week.",
                "timestamp": (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
                "sentiment_score": -0.7,
                "sentiment_label": "negative"
            }
        ]

    def get_social_feed(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get latest social context from smart money investors.
        """
        if self.mock_mode:
            tweets = self._get_mock_tweets()
            return {
                "source": "Mock Data (Smart Money Context)",
                "data": tweets[:limit],
                "summary": "Market sentiment is mixed. Burry is bearish on inflation, while Ackman remains optimistic on fundamentals. High option volatility detected."
            }
        else:
            # Placeholder for real scraping logic 
            # (Selenium/Twitter API would go here)
            return {"error": "Real scraping not implemented yet"}

social_service = SocialService()
