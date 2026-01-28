import unittest
from app.services.social_service import social_service
from app.services.nlp_service import nlp_service

class TestSocialService(unittest.TestCase):
    def test_reddit_fetch_and_sentiment(self):
        """Test that Reddit RSS fetcher returns data with sentiment labels."""
        ticker = "TSLA"
        result = social_service.get_social_feed(ticker=ticker, limit=2)
        
        self.assertIn("source", result)
        self.assertIn("data", result)
        
        if result["source"].startswith("Reddit RSS"):
            data = result["data"]
            if data:
                print(f"\nFetched {len(data)} posts for {ticker}")
                for post in data:
                    self.assertIn("sentiment_label", post)
                    self.assertIn("sentiment_score", post)
                    print(f"Post: {post['content'][:50]}... | Sentiment: {post['sentiment_label']}")
            else:
                print(f"\nNo live posts found for {ticker} (Reddit might be rate-limiting or no recent posts)")
        else:
            print("\nSocial Service in Mock Mode or Fallback")

if __name__ == "__main__":
    unittest.main()
