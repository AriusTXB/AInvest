import requests
from bs4 import BeautifulSoup
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class NewsScraperService:
    """
    Service to extract main body text from news article URLs.
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }

    def scrape_article(self, url: str) -> Optional[str]:
        """
        Fetches and cleans main text from a URL.
        """
        if not url:
            return None

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove non-content elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
            
            # Heuristic: Find the main article body
            # Common tags for article content
            article = soup.find("article")
            if not article:
                # Fallback to common class names/ids or the body if article tag missing
                article = soup.find("div", class_="caas-body") or soup.find("div", id="article-body") or soup.find("body")
            
            if not article:
                return None
                
            # Get text and clean whitespace
            text = article.get_text(separator="\n")
            lines = (line.strip() for line in text.splitlines())
            # Drop blank lines and filter out very short lines (likely nav remnants)
            clean_text = "\n".join(line for line in lines if len(line) > 30)
            
            return clean_text.strip() if clean_text else None

        except Exception as e:
            logger.error(f"Failed to scrape {url}: {str(e)}")
            return None

news_scraper_service = NewsScraperService()
