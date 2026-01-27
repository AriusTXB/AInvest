import pytesseract
from pdf2image import convert_from_bytes
import pandas as pd
import io
import re
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisionService:
    def __init__(self):
        # Configuration for Tesseract path if on Windows (Standard install location)
        # You might need to update this path based on your installation
        self.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        try:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        except:
            logger.warning("Tesseract path configuration failed. OCR might not work.")

    def _mock_balance_sheet(self) -> List[Dict[str, Any]]:
        """Returns a dummy balance sheet for demonstration if OCR fails."""
        return [
            {"Item": "Cash and Cash Equivalents", "2023": "1,200", "2022": "900"},
            {"Item": "Accounts Receivable", "2023": "3,400", "2022": "3,100"},
            {"Item": "Inventory", "2023": "2,100", "2022": "2,000"},
            {"Item": "Total Current Assets", "2023": "6,700", "2022": "6,000"},
            {"Item": "Property, Plant & Equipment", "2023": "5,000", "2022": "4,800"},
            {"Item": "Total Assets", "2023": "11,700", "2022": "10,800"},
        ]

    def extract_from_pdf(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Converts PDF to image, then runs OCR to extract financial tables.
        """
        try:
            # 1. Convert PDF to Image
            # Note: poppler_path needs to be configured if not in PATH
            try:
                images = convert_from_bytes(pdf_bytes)
            except Exception as e:
                logger.error(f"Poppler not found or PDF error: {e}")
                logger.info("Falling back to Mock Data due to missing Poppler dependency.")
                return {"status": "mock", "data": self._mock_balance_sheet(), "message": "Poppler not installed. Returning Mock Data."}

            if not images:
                return {"error": "No images converted from PDF"}

            # Take the first page for the demo
            first_page = images[0]
            
            # 2. Run OCR
            try:
                text = pytesseract.image_to_string(first_page)
            except Exception as e:
                logger.error(f"Tesseract error: {e}")
                return {"status": "mock", "data": self._mock_balance_sheet(), "message": "Tesseract not installed. Returning Mock Data."}

            # 3. Process Text (Simple parsing logic)
            # This is a heuristic parser for demo purposes
            lines = text.split('\n')
            data = []
            for line in lines:
                # Look for lines that end with numbers (financial rows)
                if re.search(r'\d+$', line.strip()):
                    parts = line.split()
                    # simplistic assumption: Text... Number Number
                    if len(parts) > 2:
                        item = " ".join(parts[:-2])
                        val_curr = parts[-2]
                        val_prev = parts[-1]
                        data.append({"Item": item, "Current": val_curr, "Previous": val_prev})
            
            if not data:
                return {"status": "warning", "data": [], "message": "OCR ran but found no structured table data."}

            return {"status": "success", "data": data}

        except Exception as e:
            logger.error(f"Vision Service Error: {e}")
            return {"error": str(e)}

vision_service = VisionService()
