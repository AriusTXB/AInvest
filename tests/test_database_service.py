"""
Unit tests for DatabaseService.

Tests cover:
- Initialization with/without Supabase credentials
- CRUD operations for memos and portfolio
- Error handling and edge cases
"""
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime
from app.services.database_service import DatabaseService
from app.schemas import InvestmentMemo, PortfolioItem, MarketData, SocialContext, NewsContext


class TestDatabaseServiceInit(unittest.TestCase):
    """Test DatabaseService initialization scenarios."""

    @patch.dict('os.environ', {'SUPABASE_URL': '', 'SUPABASE_SERVICE_ROLE_KEY': ''})
    def test_init_without_credentials(self):
        """Test initialization without Supabase credentials disables client."""
        with patch('app.services.database_service.create_client') as mock_create:
            service = DatabaseService()
            mock_create.assert_not_called()
            self.assertIsNone(service.client)

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://your-project.supabase.co',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-key'
    })
    def test_init_with_default_url(self):
        """Test initialization with default placeholder URL disables client."""
        with patch('app.services.database_service.create_client') as mock_create:
            service = DatabaseService()
            mock_create.assert_not_called()
            self.assertIsNone(service.client)

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://real-project.supabase.co',
        'SUPABASE_SERVICE_ROLE_KEY': 'real-key'
    })
    def test_init_with_valid_credentials(self):
        """Test initialization with valid credentials creates client."""
        with patch('app.services.database_service.create_client') as mock_create:
            mock_create.return_value = MagicMock()
            service = DatabaseService()
            mock_create.assert_called_once_with(
                'https://real-project.supabase.co',
                'real-key'
            )
            self.assertIsNotNone(service.client)

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://real-project.supabase.co',
        'SUPABASE_SERVICE_ROLE_KEY': 'real-key'
    })
    def test_init_handles_create_client_exception(self):
        """Test initialization handles create_client exceptions gracefully."""
        with patch('app.services.database_service.create_client') as mock_create:
            mock_create.side_effect = Exception("Connection failed")
            service = DatabaseService()
            self.assertIsNone(service.client)


class TestDatabaseServiceMemos(unittest.TestCase):
    """Test memo-related database operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MagicMock()
        self.service = DatabaseService.__new__(DatabaseService)
        self.service.client = self.mock_client
        self.service.url = "https://test.supabase.co"
        self.service.key = "test-key"

        # Sample memo for testing
        self.sample_memo = InvestmentMemo(
            ticker="AAPL",
            generated_at=datetime.now().isoformat(),
            market_data=MarketData(
                ticker="AAPL",
                price=150.0,
                change_percent=1.5,
                volume=1000000,
                indicators={"rsi": 55.0, "sma_50": 145.0},
                company_name="Apple Inc",
                sector="Technology",
                summary="Leading tech company"
            ),
            social_context=None,
            news_context=None,
            recommendation="BUY",
            analysis_summary="Strong buy signal based on technicals"
        )

    def test_save_memo_success(self):
        """Test successful memo save."""
        mock_table = MagicMock()
        self.mock_client.table.return_value = mock_table
        mock_table.insert.return_value = mock_table
        mock_table.execute.return_value = MagicMock()

        result = self.service.save_memo(self.sample_memo)

        self.assertTrue(result)
        self.mock_client.table.assert_called_once_with("memos")
        mock_table.insert.assert_called_once()

    def test_save_memo_no_client(self):
        """Test save_memo returns False when client is None."""
        self.service.client = None
        result = self.service.save_memo(self.sample_memo)
        self.assertFalse(result)

    def test_save_memo_handles_exception(self):
        """Test save_memo handles database exceptions."""
        self.mock_client.table.side_effect = Exception("DB Error")
        result = self.service.save_memo(self.sample_memo)
        self.assertFalse(result)

    def test_get_all_memos_success(self):
        """Test successful retrieval of memos."""
        mock_table = MagicMock()
        self.mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = MagicMock(data=[
            {"ticker": "AAPL", "recommendation": "BUY"},
            {"ticker": "GOOGL", "recommendation": "HOLD"}
        ])

        result = self.service.get_all_memos(limit=10)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["ticker"], "AAPL")
        mock_table.limit.assert_called_once_with(10)

    def test_get_all_memos_no_client(self):
        """Test get_all_memos returns empty list when no client."""
        self.service.client = None
        result = self.service.get_all_memos()
        self.assertEqual(result, [])

    def test_get_all_memos_handles_exception(self):
        """Test get_all_memos handles exceptions gracefully."""
        self.mock_client.table.side_effect = Exception("Query failed")
        result = self.service.get_all_memos()
        self.assertEqual(result, [])


class TestDatabaseServicePortfolio(unittest.TestCase):
    """Test portfolio-related database operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MagicMock()
        self.service = DatabaseService.__new__(DatabaseService)
        self.service.client = self.mock_client
        self.service.url = "https://test.supabase.co"
        self.service.key = "test-key"

        # Sample portfolio item
        self.sample_item = PortfolioItem(
            ticker="MSFT",
            entry_price=350.0,
            entry_date="2026-01-15",
            recommendation="BUY"
        )

    def test_save_to_portfolio_success(self):
        """Test successful portfolio item save with upsert."""
        mock_table = MagicMock()
        self.mock_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_table
        mock_table.execute.return_value = MagicMock()

        result = self.service.save_to_portfolio(self.sample_item)

        self.assertTrue(result)
        self.mock_client.table.assert_called_once_with("portfolio")
        mock_table.upsert.assert_called_once()
        # Verify ticker is uppercased
        call_args = mock_table.upsert.call_args[0][0]
        self.assertEqual(call_args["ticker"], "MSFT")

    def test_save_to_portfolio_lowercases_ticker(self):
        """Test that lowercase tickers are uppercased."""
        mock_table = MagicMock()
        self.mock_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_table
        mock_table.execute.return_value = MagicMock()

        lowercase_item = PortfolioItem(
            ticker="aapl",
            entry_price=150.0,
            entry_date="2026-01-15",
            recommendation="HOLD"
        )
        self.service.save_to_portfolio(lowercase_item)

        call_args = mock_table.upsert.call_args[0][0]
        self.assertEqual(call_args["ticker"], "AAPL")

    def test_save_to_portfolio_no_client(self):
        """Test save_to_portfolio returns False when no client."""
        self.service.client = None
        result = self.service.save_to_portfolio(self.sample_item)
        self.assertFalse(result)

    def test_save_to_portfolio_handles_exception(self):
        """Test save_to_portfolio handles exceptions."""
        self.mock_client.table.side_effect = Exception("Upsert failed")
        result = self.service.save_to_portfolio(self.sample_item)
        self.assertFalse(result)

    def test_get_portfolio_success(self):
        """Test successful portfolio retrieval."""
        mock_table = MagicMock()
        self.mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.execute.return_value = MagicMock(data=[
            {"ticker": "AAPL", "entry_price": 150.0, "p_l_percent": 5.2},
            {"ticker": "GOOGL", "entry_price": 120.0, "p_l_percent": -2.1}
        ])

        result = self.service.get_portfolio()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["ticker"], "AAPL")
        self.mock_client.table.assert_called_once_with("portfolio")

    def test_get_portfolio_no_client(self):
        """Test get_portfolio returns empty list when no client."""
        self.service.client = None
        result = self.service.get_portfolio()
        self.assertEqual(result, [])

    def test_get_portfolio_handles_exception(self):
        """Test get_portfolio handles exceptions."""
        self.mock_client.table.side_effect = Exception("Select failed")
        result = self.service.get_portfolio()
        self.assertEqual(result, [])

    def test_remove_from_portfolio_success(self):
        """Test successful removal of portfolio item."""
        mock_table = MagicMock()
        self.mock_client.table.return_value = mock_table
        mock_table.delete.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = MagicMock()

        result = self.service.remove_from_portfolio("aapl")

        self.assertTrue(result)
        self.mock_client.table.assert_called_once_with("portfolio")
        mock_table.eq.assert_called_once_with("ticker", "AAPL")

    def test_remove_from_portfolio_no_client(self):
        """Test remove_from_portfolio returns False when no client."""
        self.service.client = None
        result = self.service.remove_from_portfolio("AAPL")
        self.assertFalse(result)

    def test_remove_from_portfolio_handles_exception(self):
        """Test remove_from_portfolio handles exceptions."""
        self.mock_client.table.side_effect = Exception("Delete failed")
        result = self.service.remove_from_portfolio("AAPL")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
