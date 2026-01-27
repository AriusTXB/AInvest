import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class MarketService:
    def __init__(self):
        pass

    def get_ticker_data(self, ticker: str, period: str = "1y") -> Dict[str, Any]:
        """
        Fetches historical data and calculates technical indicators using pandas.
        """
        try:
            # Fetch data
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                return {"error": f"No data found for ticker {ticker}"}
            
            # Close prices
            close = df['Close']

            # 1. SMA (Simple Moving Average)
            df['SMA_50'] = close.rolling(window=50).mean()
            df['SMA_200'] = close.rolling(window=200).mean()
            
            # 2. RSI (Relative Strength Index)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # 3. MACD
            exp1 = close.ewm(span=12, adjust=False).mean()
            exp2 = close.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            df['MACD'] = macd
            
            # Get latest values for the dashboard
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Basic Info
            info = stock.info
            
            return {
                "ticker": ticker.upper(),
                "price": round(latest['Close'], 2),
                "change_percent": round((latest['Close'] - prev['Close']) / prev['Close'] * 100, 2),
                "volume": int(latest['Volume']),
                "indicators": {
                    "rsi": round(latest['RSI'], 2) if not pd.isna(latest['RSI']) else 0,
                    "sma_50": round(latest['SMA_50'], 2) if not pd.isna(latest['SMA_50']) else 0,
                    "sma_200": round(latest['SMA_200'], 2) if not pd.isna(latest['SMA_200']) else 0,
                    "macd": round(latest['MACD'], 2) if not pd.isna(latest['MACD']) else 0,
                },
                "company_name": info.get('longName', 'Unknown'),
                "sector": info.get('sector', 'Unknown'),
                "summary": info.get('longBusinessSummary', 'No summary available.')
            }
            
        except Exception as e:
            return {"error": str(e)}

market_service = MarketService()
