from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import random
import requests
import re
import xml.etree.ElementTree as ET
from app.services.nlp_service import nlp_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialService:
    def __init__(self):
        # We can still have a fallback mode
        self.use_live_data = True 
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://stocktwits.com/",
            "Origin": "https://stocktwits.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        }

    def _fetch_reddit_rss(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Fetches RSS feed from Reddit (WallStreetBets and Stocks) for a given ticker.
        """
        posts = []
        # Searching across related subreddits
        subreddits = ["wallstreetbets", "stocks", "investing"]
        
        for sub in subreddits:
            try:
                # Reddit RSS search URL
                url = f"https://www.reddit.com/r/{sub}/search.rss?q={ticker}&sort=new&restrict_sr=on"
                headers = self.headers
                
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch Reddit RSS for r/{sub}: {response.status_code}")
                    continue

                # Parse XML
                root = ET.fromstring(response.content)
                # RSS namespaces
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                for entry in root.findall('atom:entry', ns):
                    title = entry.find('atom:title', ns).text
                    author_elem = entry.find('atom:author/atom:name', ns)
                    author = author_elem.text if author_elem is not None else "u/unknown"
                    
                    # Sentiment Analysis
                    sentiment = nlp_service.analyze_sentiment(title)
                    
                    posts.append({
                        "id": entry.find('atom:id', ns).text.split('/')[-1],
                        "author": author,
                        "handle": author, # No real handle in RSS, using username
                        "content": title,
                        "timestamp": entry.find('atom:updated', ns).text,
                        "sentiment_score": sentiment["sentiment"]["score"],
                        "sentiment_label": sentiment["sentiment"]["label"],
                        "source": f"r/{sub}"
                    })
                    
                    if len(posts) >= 10: break # Limit per search

            except Exception as e:
                logger.error(f"Error fetching Reddit RSS for r/{sub}: {e}")
                
        return sorted(posts, key=lambda x: x['timestamp'], reverse=True)

    def _fetch_stocktwits(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Fetches public streams from Stocktwits for a given ticker.
        """
        posts = []
        try:
            url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
            headers = self.headers
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch Stocktwits for ${ticker}: {response.status_code}")
                return []

            data = response.json()
            messages = data.get("messages", [])
            
            for msg in messages:
                content = msg.get("body", "")
                user = msg.get("user", {})
                
                # Sentiment Analysis
                sentiment = nlp_service.analyze_sentiment(content)
                
                posts.append({
                    "id": str(msg.get("id")),
                    "author": user.get("username", "unknown"),
                    "handle": f"@{user.get('username', 'unknown')}",
                    "content": content,
                    "timestamp": msg.get("created_at"),
                    "sentiment_score": sentiment["sentiment"]["score"],
                    "sentiment_label": sentiment["sentiment"]["label"],
                    "source": "Stocktwits"
                })
        except Exception as e:
            logger.error(f"Error fetching Stocktwits for ${ticker}: {e}")
            
        return posts

    def _get_mock_tweets(self) -> List[Dict[str, Any]]:
        """Fallback mock data."""
        return [
            {
                "id": "mock_1",
                "author": "Smart Money Bot",
                "handle": "@smartmoney",
                "content": "Market flow looks consolidate. Waiting for confirmation.",
                "timestamp": datetime.now().isoformat(),
                "sentiment_score": 0.0,
                "sentiment_label": "neutral"
            }
        ]

    def get_social_feed(self, ticker: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
        """
        Get latest social context for a ticker from multiple sources.
        """
        if self.use_live_data and ticker:
            logger.info(f"Fetching live social data for {ticker}...")
            
            reddit_posts = self._fetch_reddit_rss(ticker)
            st_posts = self._fetch_stocktwits(ticker)
            
            all_posts = reddit_posts + st_posts
            
            # Sort by timestamp (both are ISO or similar string-sortable formats)
            all_posts = sorted(all_posts, key=lambda x: str(x['timestamp']), reverse=True)
            
            if not all_posts:
                return {
                    "source": "Aggregated (Empty Result)",
                    "data": self._get_mock_tweets()[:limit],
                    "summary": f"No recent social activity found for ${ticker}. Using fallback signals."
                }
                
            return {
                "source": "Aggregated (Reddit + Stocktwits)",
                "data": all_posts[:limit],
                "summary": f"Analyzed {len(all_posts[:limit])} recent signals for ${ticker} from Reddit and Stocktwits."
            }
        else:
            return {
                "source": "Mock Data",
                "data": self._get_mock_tweets()[:limit],
                "summary": "Mock signals active."
            }

social_service = SocialService()
