import pytesseract
from pdf2image import convert_from_bytes
import pandas as pd
import io
import re
import os
from typing import Dict, Any, List
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisionService:
    def __init__(self):
        # Configuration for Tesseract path from environment or standard location
        self.tesseract_cmd = os.getenv('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
        self.poppler_path = os.getenv('POPPLER_PATH', None)
        
        try:
            if os.path.exists(self.tesseract_cmd):
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
            else:
                logger.warning(f"Tesseract not found at {self.tesseract_cmd}. OCR may fail.")
        except Exception as e:
            logger.warning(f"Tesseract configuration failed: {e}")

    def _mock_balance_sheet(self) -> List[Dict[str, Any]]:
        """Returns a dummy balance sheet for demonstration if OCR fails."""
        return [
            {"Item": "Cash and Cash Equivalents", "Current": "1,200", "Previous": "900"},
            {"Item": "Accounts Receivable", "Current": "3,400", "Previous": "3,100"},
            {"Item": "Inventory", "Current": "2,100", "Previous": "2,000"},
            {"Item": "Total Current Assets", "Current": "6,700", "Previous": "6,000"},
            {"Item": "Property, Plant & Equipment", "Current": "5,000", "Previous": "4,800"},
            {"Item": "Total Assets", "Current": "11,700", "Previous": "10,800"},
        ]

    def _parse_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Improved heuristic parser for financial data.
        """
        lines = text.split('\n')
        data = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Regex to find lines ending with two numeric values (Current, Previous)
            # Handles commas, dots, and common currency symbols
            # Example: "Total Assets $ 12,345.00 11,000.00"
            match = re.search(r'^(.*?)\s+[\$€£]?\s*([\d,.]+)\s+[\$€£]?\s*([\d,.]+)$', line)
            
            if match:
                item = match.group(1).strip()
                val_curr = match.group(2).strip()
                val_prev = match.group(3).strip()
                
                # Basic cleaning: remove starting/trailing punctuation and dots from item
                item = re.sub(r'^[:\.\s\-_]+|[:\.\s\-_]+$', '', item)
                
                if item and len(item) > 3:
                    data.append({
                        "Item": item,
                        "Current": val_curr,
                        "Previous": val_prev
                    })
        return data

    def extract_from_pdf(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Converts PDF pages to images, then runs OCR to extract financial tables.
        Processes all pages.
        """
        try:
            # 1. Convert PDF to Images
            try:
                images = convert_from_bytes(pdf_bytes, poppler_path=self.poppler_path)
            except Exception as e:
                logger.error(f"Poppler error: {e}")
                return {
                    "status": "mock", 
                    "data": self._mock_balance_sheet(), 
                    "message": f"Poppler error: {str(e)}. Using fallback data."
                }

            if not images:
                return {"error": "No pages found in PDF"}

            all_extracted_data = []
            page_count = len(images)
            
            # 2. Process each page
            for i, image in enumerate(images):
                logger.info(f"Processing page {i+1}/{page_count}...")
                try:
                    text = pytesseract.image_to_string(image)
                    page_data = self._parse_text(text)
                    if page_data:
                        for entry in page_data:
                            entry["Page"] = i + 1
                        all_extracted_data.extend(page_data)
                except Exception as e:
                    logger.error(f"OCR failed on page {i+1}: {e}")

            if not all_extracted_data:
                return {
                    "status": "warning", 
                    "data": [], 
                    "message": "OCR ran but found no structured financial data across all pages.",
                    "pages_processed": page_count
                }

            return {
                "status": "success", 
                "data": all_extracted_data,
                "metadata": {
                    "pages_processed": page_count,
                    "items_found": len(all_extracted_data)
                }
            }

        except Exception as e:
            logger.error(f"Vision Service Critical Error: {e}")
            return {"error": str(e)}

vision_service = VisionService()
