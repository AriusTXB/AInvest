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

class SocialPost(BaseModel):
    id: str
    author: str
    handle: str
    content: str
    timestamp: str
    sentiment_label: str
    sentiment_score: float # Added in Phase 2
    source: str # Added in Phase 2

class SocialContext(BaseModel):
    source: str
    data: List[SocialPost]
    summary: str

class InvestmentMemo(BaseModel):
    """
    The aggregated report for a specific ticker.
    """
    ticker: str
    generated_at: str
    market_data: Optional[MarketData] = None
    social_context: Optional[SocialContext] = None # Updated to structured object
    news_sentiment: Optional[Dict[str, Any]] = None
    vision_context: Optional[Dict[str, Any]] = None # New PDF/Image context
    recommendation: str = "HOLD" # AI-generated recommendation
    analysis_summary: str
