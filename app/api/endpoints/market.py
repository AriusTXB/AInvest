from fastapi import APIRouter, HTTPException
from app.services.market_service import market_service

router = APIRouter()

@router.get("/{ticker}")
async def get_market_data(ticker: str):
    """
    Get real-time price and technical indicators for a ticker.
    """
    data = market_service.get_ticker_data(ticker)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data
