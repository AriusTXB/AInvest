from fastapi import APIRouter, HTTPException
from app.schemas import PortfolioItem
from app.services.database_service import database_service
from app.services.market_service import market_service
from typing import List
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[PortfolioItem])
async def get_portfolio():
    """
    Retrieves the virtual portfolio with real-time P/L calculations.
    """
    raw_portfolio = database_service.get_portfolio()
    items = []
    
    for row in raw_portfolio:
        ticker = row["ticker"]
        # Fetch current price for P/L calc
        try:
            market_data = market_service.get_ticker_data(ticker, period="1d")
            current_price = market_data.get("price", row["entry_price"])
        except:
            current_price = row["entry_price"]
            
        p_l = ((current_price - row["entry_price"]) / row["entry_price"]) * 100
        
        items.append(PortfolioItem(
            id=str(row.get("id")),
            ticker=ticker,
            entry_price=row["entry_price"],
            entry_date=row["entry_date"],
            recommendation=row["recommendation"],
            current_price=current_price,
            p_l_percent=round(p_l, 2)
        ))
        
    return items

@router.post("/add")
async def add_to_portfolio(item: PortfolioItem):
    """
    Adds a new position to the virtual portfolio.
    """
    success = database_service.save_to_portfolio(item)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save to portfolio")
    return {"status": "success", "ticker": item.ticker}

@router.delete("/{ticker}")
async def remove_from_portfolio(ticker: str):
    """
    Removes a position from the virtual portfolio.
    """
    success = database_service.remove_from_portfolio(ticker)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to remove from portfolio")
    return {"status": "success", "ticker": ticker}
