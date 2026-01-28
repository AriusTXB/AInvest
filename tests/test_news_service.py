import unittest
from unittest.mock import MagicMock, patch
from app.services.news_service import NewsService

class TestNewsService(unittest.TestCase):
    def setUp(self):
        self.service = NewsService()

    @patch('yfinance.Ticker')
    @patch('app.services.news_service.nlp_service')
    def test_get_ticker_news_success(self, mock_nlp, mock_ticker):
        """Test fetching and processing news with mocks."""
        # Mock yfinance news data
        mock_ticker.return_value.news = [
            {
                "title": "Test Headline",
                "link": "https://example.com",
                "publisher": "Test Publisher",
                "providerPublishTime": 123456789,
                "summary": "This is a summary."
            }
        ]

        # Mock NLP sentiment analysis
        mock_nlp.analyze_sentiment.return_value = {
            "sentiment": {"label": "positive", "score": 0.9}
        }

        result = self.service.get_ticker_news("AAPL", count=1)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Test Headline")
        self.assertEqual(result[0]["sentiment"]["label"], "positive")
        self.assertEqual(result[0]["publisher"], "Test Publisher")

    @patch('yfinance.Ticker')
    def test_get_ticker_news_empty(self, mock_ticker):
        """Test behavior when no news is found."""
        mock_ticker.return_value.news = []
        result = self.service.get_ticker_news("INVALID")
        self.assertEqual(len(result), 0)

if __name__ == "__main__":
    unittest.main()
