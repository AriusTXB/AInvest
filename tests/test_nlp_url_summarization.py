import unittest
from app.services.nlp_service import nlp_service

class TestNLPURLSummarization(unittest.TestCase):
    def test_url_summarization_success(self):
        """Test that a valid URL is successfully summarized using mocks."""
        from unittest.mock import patch
        
        url = "https://example.com/finance-news"
        mock_text = "Apple Inc. announced record earnings today. The stock rose 5% in after-hours trading. CEO Tim Cook expressed optimism about the future growth in Services."
        
        with patch('app.services.nlp_service.news_scraper_service.scrape_article') as mock_scrape:
            mock_scrape.return_value = mock_text
            result = nlp_service.summarize_article(url)
            
            self.assertEqual(result['status'], 'success')
            self.assertIsNotNone(result['summary'])
            # Since we are likely in mock mode or using a small model, just check it exists
            print(f"\nMock Summary: {result['summary']}")

    def test_invalid_url(self):
        """Test handling of invalid URLs."""
        url = "http://invalid-url-that-does-not-exist.com/article"
        result = nlp_service.summarize_article(url)
        self.assertEqual(result['status'], 'error')

if __name__ == "__main__":
    unittest.main()
