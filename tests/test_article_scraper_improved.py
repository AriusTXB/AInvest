import unittest
from unittest.mock import patch, MagicMock
from app.services.news_scraper_service import NewsScraperService

class TestArticleScraperImproved(unittest.TestCase):
    def setUp(self):
        self.service = NewsScraperService()

    @patch('requests.get')
    def test_scrape_with_article_tag(self, mock_get):
        """Verify extraction from standard <article> tag."""
        mock_html = """
        <html>
            <body>
                <header>Navigation</header>
                <article>
                    <p>This is a very long paragraph that should definitely be included in the output because it exceeds thirty characters in length.</p>
                    <p>Another valid paragraph that is also quite long and should be preserved by the scraper logic.</p>
                </article>
                <footer>Footer content</footer>
            </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        content = self.service.scrape_article("http://example.com")
        
        self.assertIn("This is a very long paragraph", content)
        self.assertIn("Another valid paragraph", content)
        self.assertNotIn("Navigation", content)
        self.assertNotIn("Footer content", content)

    @patch('requests.get')
    def test_scrape_with_fallback_id(self, mock_get):
        """Verify extraction from id="article-body" when <article> is missing."""
        mock_html = """
        <html>
            <body>
                <div id="article-body">
                    <p>This paragraph is part of the article body identified by an ID tag instead of a semantic article tag.</p>
                </div>
            </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        content = self.service.scrape_article("http://example.com")
        self.assertIn("This paragraph is part of the article body", content)

    @patch('requests.get')
    def test_scrape_content_removal(self, mock_get):
        """Verify that script and style tags are removed."""
        mock_html = """
        <html>
            <body>
                <article>
                    <script>console.log('remove me');</script>
                    <style>.css { color: red; }</style>
                    <p>Main content that should be kept in the final scraped output text.</p>
                </article>
            </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        content = self.service.scrape_article("http://example.com")
        self.assertIn("Main content that should be kept", content)
        self.assertNotIn("console.log", content)
        self.assertNotIn("color: red", content)

    @patch('requests.get')
    def test_scrape_short_line_filtering(self, mock_get):
        """Verify that lines with <= 30 characters are filtered out."""
        mock_html = """
        <html>
            <body>
                <article>
                    <p>Short line.</p>
                    <p>This is a sufficiently long line that will not be filtered by the scraper's minimum length logic.</p>
                    <p>Too brief.</p>
                </article>
            </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        content = self.service.scrape_article("http://example.com")
        self.assertIn("This is a sufficiently long line", content)
        self.assertNotIn("Short line", content)
        self.assertNotIn("Too brief", content)

    @patch('requests.get')
    def test_scrape_http_error(self, mock_get):
        """Verify that HTTP errors return None."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_get.return_value = mock_response

        content = self.service.scrape_article("http://example.com/bad")
        self.assertIsNone(content)

if __name__ == "__main__":
    unittest.main()
