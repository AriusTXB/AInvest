import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from app.services.market_service import MarketService

class TestMarketService(unittest.TestCase):
    def setUp(self):
        self.service = MarketService()

    @patch('yfinance.Ticker')
    def test_get_ticker_data_calculation(self, mock_ticker):
        """Test technical indicators (SMA, RSI, MACD) calculations."""
        # Create 200+ days of data to satisfy SMA_200 and RSI requirements
        dates = pd.date_range(start="2023-01-01", periods=250)
        # Create a price trend: first 100 days rising, then falling
        prices = [100 + i for i in range(150)] + [250 - i for i in range(100)]
        
        mock_df = pd.DataFrame({
            'Close': prices,
            'Volume': [1000] * 250
        }, index=dates)

        # Mock the history method
        mock_instance = mock_ticker.return_value
        mock_instance.history.return_value = mock_df
        mock_instance.info = {"longName": "Test Corp", "sector": "Tech", "longBusinessSummary": "Summary"}

        result = self.service.get_ticker_data("AAPL")

        # Basic Checks
        self.assertEqual(result["ticker"], "AAPL")
        self.assertEqual(result["company_name"], "Test Corp")
        
        # Indicator presence
        indicators = result["indicators"]
        self.assertIn("rsi", indicators)
        self.assertIn("sma_50", indicators)
        self.assertIn("sma_200", indicators)
        self.assertIn("macd", indicators)

        # Values should be within valid ranges
        self.assertTrue(0 <= indicators["rsi"] <= 100)
        self.assertNotEqual(indicators["sma_200"], 0)

    @patch('yfinance.Ticker')
    def test_empty_data_handling(self, mock_ticker):
        """Test behavior when yfinance returns no data."""
        mock_instance = mock_ticker.return_value
        mock_instance.history.return_value = pd.DataFrame()
        
        result = self.service.get_ticker_data("INVALID")
        self.assertIn("error", result)

if __name__ == "__main__":
    unittest.main()
