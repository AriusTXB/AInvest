import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class MarketService:
    def __init__(self):
        pass

    def get_ticker_data(self, ticker: str, period: str = "1y") -> Dict[str, Any]:
        """
        Fetches historical data and calculates technical indicators.
        """
        try:
            # Fetch data
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                return {"error": f"No data found for ticker {ticker}"}
            
            # Calculate Indicators
            # 1. SMA (Simple Moving Average)
            df['SMA_50'] = ta.sma(df['Close'], length=50)
            df['SMA_200'] = ta.sma(df['Close'], length=200)
            
            # 2. RSI (Relative Strength Index)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            
            # 3. MACD
            macd = ta.macd(df['Close'])
            df = pd.concat([df, macd], axis=1)
            
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
                    "rsi": round(latest['RSI_14'], 2) if not pd.isna(latest['RSI_14']) else 0,
                    "sma_50": round(latest['SMA_50'], 2) if not pd.isna(latest['SMA_50']) else 0,
                    "sma_200": round(latest['SMA_200'], 2) if not pd.isna(latest['SMA_200']) else 0,
                    "macd": round(latest['MACD_12_26_9'], 2) if not pd.isna(latest['MACD_12_26_9']) else 0,
                },
                "company_name": info.get('longName', 'Unknown'),
                "sector": info.get('sector', 'Unknown'),
                "summary": info.get('longBusinessSummary', 'No summary available.')
            }
            
        except Exception as e:
            return {"error": str(e)}

market_service = MarketService()
