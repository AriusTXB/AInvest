from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class MarketData(BaseModel):
    ticker: str
    price: float
    change_percent: float
    volume: int
    indicators: Dict[str, float]
    company_name: str
    sector: str
    summary: str

class SentimentData(BaseModel):
    label: str
    score: float

class SocialPost(BaseModel):
    id: str
    author: str
    handle: str
    content: str
    timestamp: str
    sentiment_label: str

class InvestmentMemo(BaseModel):
    """
    The aggregated report for a specific ticker.
    """
    ticker: str
    generated_at: str
    market_data: Optional[MarketData] = None
    social_context: List[SocialPost] = []
    news_sentiment: Optional[Dict[str, Any]] = None
    recommendation: str = "HOLD" # AI-generated recommendation
    analysis_summary: str
