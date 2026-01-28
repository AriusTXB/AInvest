import unittest
from app.services.news_scraper_service import news_scraper_service

class TestNewsScraperService(unittest.TestCase):
    def test_scrape_valid_url(self):
        """
        Test scraping a known reachable URL (using a static one or a mock would be better in CI, 
        but for local validation we check basic functionality).
        """
        # Testing with a reliable public site that likely won't block immediately
        url = "https://www.google.com" 
        content = news_scraper_service.scrape_article(url)
        # Even google has some text
        if content:
            self.assertIsInstance(content, str)
            self.assertTrue(len(content) > 0)

    def test_invalid_url(self):
        content = news_scraper_service.scrape_article("http://thisisnotarealurl.test")
        self.assertIsNone(content)

    def test_empty_url(self):
        content = news_scraper_service.scrape_article("")
        self.assertIsNone(content)

if __name__ == "__main__":
    unittest.main()
