from fastapi import APIRouter, HTTPException
from app.schemas import InvestmentMemo, MarketData, SocialPost
from app.services.market_service import market_service
from app.services.social_service import social_service
from app.services.nlp_service import nlp_service
from app.services.database_service import database_service
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
    
    # 1. Market Logic (RSI)
    rsi = market.get("indicators", {}).get("rsi", 50)
    if rsi < 30: score += 1.5 # Oversold (Buy Weight)
    elif rsi > 70: score -= 1.5 # Overbought (Sell Weight)
    
    # 2. News Logic
    sent_label = sentiment.get("sentiment", {}).get("label", "neutral")
    sent_score = sentiment.get("sentiment", {}).get("score", 0.5)
    if sent_label == "positive" and sent_score > 0.8: score += 1
    elif sent_label == "negative" and sent_score > 0.8: score -= 1
    
    # 3. Social Logic (Aggregated)
    social_posts = social.get("data", [])
    if social_posts:
        pos_posts = len([p for p in social_posts if p.get("sentiment_label") == "positive"])
        neg_posts = len([p for p in social_posts if p.get("sentiment_label") == "negative"])
        if pos_posts > neg_posts: score += 0.5
        elif neg_posts > pos_posts: score -= 0.5
    
    # Result Synthesis
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
    
    # 2. Fetch Social Context (Live Reddit Data)
    social_data = social_service.get_social_feed(ticker=ticker, limit=3)
    
    # 3. Fetch & Analyze News (Simulated with Summarization)
    latest_news_content = _fetch_mock_news(ticker)
    sentiment_result = nlp_service.analyze_sentiment(latest_news_content)
    summary_result = nlp_service.summarize(latest_news_content)
    
    # 4. Generate Recommendation
    rec = _generate_recommendation(market_data, sentiment_result, social_data)
    
    # 5. Build Response Object
    memo = InvestmentMemo(
        ticker=ticker.upper(),
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        market_data=market_data,
        social_context=social_data, # Now passing the full dict/object
        news_sentiment={
            "headline_analyzed": latest_news_content,
            "analysis": sentiment_result,
            "summary": summary_result
        },
        recommendation=rec,
        analysis_summary=f"Analysis suggests {rec}. Market: RSI {market_data['indicators']['rsi']}. Social: {social_data['summary']}"
    )

    # 6. Async Persistence (Best effort)
    try:
        database_service.save_memo(memo)
    except Exception as e:
        logger.error(f"Persistence failed: {e}")

    return memo
