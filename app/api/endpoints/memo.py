from fastapi import APIRouter, HTTPException
from app.schemas import InvestmentMemo, MarketData, SocialPost
from app.services.market_service import market_service
from app.services.social_service import social_service
from app.services.nlp_service import nlp_service
from datetime import datetime
import random

router = APIRouter()

def _fetch_mock_news(ticker: str) -> str:
    """Simulates fetching latest news for a ticker."""
    templates = [
        f"{ticker} reports strong Q3 earnings, beating expectations by 15%.",
        f"Analysts downgrade {ticker} due to supply chain concerns.",
        f"CEO of {ticker} announces new strategic partnership with major competitor.",
        f"Regulatory scrutiny increases for {ticker} in the EU market.",
        f"{ticker} unveils breakthrough technology at annual conference."
    ]
    return random.choice(templates)

def _generate_recommendation(market: dict, sentiment: dict, social: dict) -> str:
    """Simple logic to generate a BUY/SELL/HOLD signal."""
    score = 0
    
    # Market Logic
    rsi = market.get("indicators", {}).get("rsi", 50)
    if rsi < 30: score += 1 # Oversold
    elif rsi > 70: score -= 1 # Overbought
    
    # NLP Logic
    sent_label = sentiment.get("sentiment", {}).get("label", "neutral")
    if sent_label == "positive": score += 1
    elif sent_label == "negative": score -= 1
    
    # Result
    if score >= 1: return "BUY"
    if score <= -1: return "SELL"
    return "HOLD"

@router.get("/{ticker}", response_model=InvestmentMemo)
async def get_investment_memo(ticker: str):
    """
    Generates a full Investment Memo for a given ticker.
    Aggregates Market Data, Social Signals, and NLP analysis.
    """
    # 1. Fetch Market Data
    market_data = market_service.get_ticker_data(ticker)
    if "error" in market_data:
        # If real data fails, we might mock it or raise error. 
        # For this demo, let's raise error to show we tried real data.
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found: {market_data['error']}")
    
    # 2. Fetch Social Context (Generic for MVP, but attached)
    social_data = social_service.get_social_feed(limit=3)
    
    # 3. Fetch & Analyze News (Simulated)
    latest_news_headline = _fetch_mock_news(ticker)
    sentiment_result = nlp_service.analyze_sentiment(latest_news_headline)
    
    # 4. Generate Recommendation
    rec = _generate_recommendation(market_data, sentiment_result, social_data)
    
    # 5. Build Response
    return InvestmentMemo(
        ticker=ticker.upper(),
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        market_data=market_data,
        social_context=social_data["data"],
        news_sentiment={
            "headline_analyzed": latest_news_headline,
            "analysis": sentiment_result
        },
        recommendation=rec,
        analysis_summary=f"Market indicators suggest {rec}. Analyzed headline: '{latest_news_headline}'."
    )
