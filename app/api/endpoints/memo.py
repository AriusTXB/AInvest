from fastapi import APIRouter, HTTPException
from app.schemas import InvestmentMemo, MarketData, SocialPost
from app.services.market_service import market_service
from app.services.social_service import social_service
from app.services.nlp_service import nlp_service
from app.services.news_service import news_service
from app.services.database_service import database_service
from datetime import datetime
import random

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def _generate_recommendation(market: dict, sentiment: dict, social: dict) -> str:
    """Simple logic to generate a BUY/SELL/HOLD signal."""
    score = 0
    
    # 1. Market Logic (RSI)
    rsi = market.get("indicators", {}).get("rsi", 50)
    if rsi < 30: score += 1.5 # Oversold (Buy Weight)
    elif rsi > 70: score -= 1.5 # Overbought (Sell Weight)
    
    # 2. News Logic (Aggregated)
    news_items = news.get("items", [])
    if news_items:
        avg_score = sum([n["sentiment"]["score"] for n in news_items]) / len(news_items)
        pos_count = len([n for n in news_items if n["sentiment"]["label"] == "positive"])
        neg_count = len([n for n in news_items if n["sentiment"]["label"] == "negative"])
        
        if pos_count > neg_count and avg_score > 0.6: score += 1
        elif neg_count > pos_count and avg_score > 0.6: score -= 1
    
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
    
    # 3. Fetch Live News Data
    news_data = news_service.get_ticker_news(ticker=ticker, count=5)
    
    # Calculate Overall News Sentiment for Context
    if news_data:
        avg_news_score = sum([n["sentiment"]["score"] for n in news_data]) / len(news_data)
        pos_news = len([n for n in news_data if n["sentiment"]["label"] == "positive"])
        neg_news = len([n for n in news_data if n["sentiment"]["label"] == "negative"])
        overall_news_sent = "positive" if pos_news > neg_news else ("negative" if neg_news > pos_news else "neutral")
    else:
        avg_news_score = 0.5
        overall_news_sent = "neutral"

    news_context = {
        "items": news_data,
        "overall_sentiment": overall_news_sent,
        "average_score": avg_news_score
    }
    
    # 4. Generate Recommendation
    rec = _generate_recommendation(market_data, news_context, social_data)
    
    # 5. Build Response Object
    memo = InvestmentMemo(
        ticker=ticker.upper(),
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        market_data=market_data,
        social_context=social_data,
        news_context=news_context,
        recommendation=rec,
        analysis_summary=f"Analysis suggests {rec}. Market: RSI {market_data['indicators']['rsi']}. News: {overall_news_sent.upper()}. Social: {social_data['summary']}"
    )

    # 6. Async Persistence (Best effort)
    try:
        database_service.save_memo(memo)
    except Exception as e:
        logger.error(f"Persistence failed: {e}")

    return memo
