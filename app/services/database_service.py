import os
import logging
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from app.schemas import InvestmentMemo, PortfolioItem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.client: Optional[Client] = None
        
        if self.url and self.key and self.url != "https://your-project.supabase.co":
            try:
                self.client = create_client(self.url, self.key)
                logger.info("Supabase client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
        else:
            logger.warning("Supabase credentials missing or default. Persistence disabled.")

    def save_memo(self, memo: InvestmentMemo) -> bool:
        """
        Saves an InvestmentMemo to the Supabase 'memos' table.
        """
        if not self.client:
            logger.warning("Database client not available. Skipping save.")
            return False

        try:
            # Convert memo to dict and handle nested objects for JSONB columns
            memo_data = memo.model_dump()
            
            # Prepare row for Supabase
            row = {
                "ticker": memo_data["ticker"],
                "generated_at": memo_data["generated_at"],
                "market_data": memo_data["market_data"],
                "social_context": memo_data["social_context"],
                "news_context": memo_data["news_context"],
                "recommendation": memo_data["recommendation"],
                "analysis_summary": memo_data["analysis_summary"]
            }
            
            # Insert into 'memos' table
            self.client.table("memos").insert(row).execute()
            logger.info(f"Saved memo for {memo.ticker} to database.")
            return True
        except Exception as e:
            logger.error(f"Failed to save memo: {e}")
            return False

    def get_all_memos(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieves recent investment memos.
        """
        if not self.client:
            return []

        try:
            response = self.client.table("memos").select("*").order("generated_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch memos: {e}")
            return []

    def save_to_portfolio(self, item: PortfolioItem) -> bool:
        """
        Saves a ticker to the 'portfolio' table.
        """
        if not self.client:
            return False
        try:
            row = {
                "ticker": item.ticker.upper(),
                "entry_price": item.entry_price,
                "entry_date": item.entry_date,
                "recommendation": item.recommendation
            }
            # UPSERT to allow updating existing positions
            self.client.table("portfolio").upsert(row, on_conflict="ticker").execute()
            logger.info(f"Ticker {item.ticker} saved to portfolio.")
            return True
        except Exception as e:
            logger.error(f"Failed to save to portfolio: {e}")
            return False

    def get_portfolio(self) -> List[Dict[str, Any]]:
        """
        Retrieves all items from the virtual portfolio.
        """
        if not self.client:
            return []
        try:
            response = self.client.table("portfolio").select("*").execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch portfolio: {e}")
            return []

    def remove_from_portfolio(self, ticker: str) -> bool:
        """
        Removes a ticker from the virtual portfolio.
        """
        if not self.client:
            return False
        try:
            self.client.table("portfolio").delete().eq("ticker", ticker.upper()).execute()
            logger.info(f"Ticker {ticker} removed from portfolio.")
            return True
        except Exception as e:
            logger.error(f"Failed to remove from portfolio: {e}")
            return False

database_service = DatabaseService()
