import unittest
from unittest.mock import MagicMock, patch
from app.api.endpoints.portfolio import get_portfolio
from app.schemas import PortfolioItem

class TestPortfolioLogic(unittest.IsolatedAsyncioTestCase):
    
    @patch('app.api.endpoints.portfolio.database_service')
    @patch('app.api.endpoints.portfolio.market_service')
    async def test_portfolio_pl_calculation(self, mock_market, mock_db):
        """Test that P/L percentage is calculated correctly."""
        # Mock DB response
        mock_db.get_portfolio.return_value = [
            {
                "ticker": "TSLA",
                "entry_price": 200.0,
                "entry_date": "2023-01-01",
                "recommendation": "BUY"
            }
        ]
        
        # Mock Market response (Current Price = 220, so +10% gain)
        mock_market.get_ticker_data.return_value = {"price": 220.0}
        
        # Call the endpoint function directly
        result = await get_portfolio()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].ticker, "TSLA")
        self.assertEqual(result[0].p_l_percent, 10.0)
        self.assertEqual(result[0].current_price, 220.0)

if __name__ == "__main__":
    # Note: Running async tests in unittest requires a runner or manual loop
    # For simplicity in this environment, we'll use a synchronous-style check 
    # if possible, or just focus on the logic.
    pass
