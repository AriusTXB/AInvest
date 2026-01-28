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

class NewsItem(BaseModel):
    title: str
    link: str
    publisher: str
    timestamp: int
    sentiment: Dict[str, Any]
    summary: str

class NewsContext(BaseModel):
    items: List[NewsItem]
    overall_sentiment: str
    average_score: float

class InvestmentMemo(BaseModel):
    """
    The aggregated report for a specific ticker.
    """
    ticker: str
    generated_at: str
    market_data: Optional[MarketData] = None
    social_context: Optional[SocialContext] = None 
    news_context: Optional[NewsContext] = None # Replacing news_sentiment
    vision_context: Optional[Dict[str, Any]] = None # New PDF/Image context
    recommendation: str = "HOLD" # AI-generated recommendation
    analysis_summary: str

class PortfolioItem(BaseModel):
    """
    Represents a tracked investment in the virtual portfolio.
    """
    id: Optional[str] = None
    ticker: str
    entry_price: float
    entry_date: str
    recommendation: str
    current_price: Optional[float] = None
    p_l_percent: Optional[float] = None
