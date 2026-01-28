import sys
import os
sys.path.append(os.getcwd())

from app.services.market_service import market_service
import asyncio

def test_market():
    print("Fetching data for AAPL...")
    data = market_service.get_ticker_data("AAPL")
    if "error" in data:
        print(f"Error: {data['error']}")
    else:
        print(f"Success! {data['ticker']} Price: ${data['price']}")
        print(f"RSI: {data['indicators']['rsi']}")
        print(f"MACD: {data['indicators']['macd']}")

if __name__ == "__main__":
    test_market()
