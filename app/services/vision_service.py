import pytesseract
from pdf2image import convert_from_bytes
import pandas as pd
import io
import re
import os
import numpy as np
import cv2
from typing import Dict, Any, List, Union
import logging
import base64
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisionService:
    def __init__(self):
        self.tesseract_path = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        self.poppler_path = os.getenv("POPPLER_PATH", r"C:\poppler\Library\bin")
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        
        # DeepSeek Config
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        if self.deepseek_api_key:
            self.client = OpenAI(api_key=self.deepseek_api_key, base_url=self.deepseek_base_url)
        else:
            self.client = None

    def _check_binaries(self):
        """Internal check for Tesseract/Poppler presence."""
        if not os.path.exists(self.tesseract_path):
            logger.warning(f"Tesseract not found at {self.tesseract_path}. OCR will fail.")
            return False
        return True

    def _preprocess_image(self, image: Any) -> Any:
        """
        Enhance image quality for better OCR results.
        Grayscale -> Thresholding.
        """
        # Convert PIL image to OpenCV format
        open_cv_image = np.array(image.convert('RGB'))
        # Convert RGB to BGR
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        
        # 1. Grayscale
        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        
        # 2. Thresholding (Otsu's binarization)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh

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
        Handles currencies, negative numbers in parents, and dots.
        """
        lines = text.split('\n')
        data = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Improved regex:
            # 1. Capture Item name (starts line, ends before numbers)
            # 2. Capture two numeric blocks (allows $, %, (, ), -, , and .)
            pattern = r'^(.*?)\s+([\$€£]?\s*[\(\-]?[\d,.]+%?[\)]?)\s+([\$€£]?\s*[\(\-]?[\d,.]+%?[\)]?)$'
            match = re.search(pattern, line)
            
            if match:
                item = match.group(1).strip()
                val_curr = match.group(2).strip()
                val_prev = match.group(3).strip()
                
                # Cleaning: remove starting/trailing symbols from item
                item = re.sub(r'^[:\.\s\-_/]+|[:\.\s\-_/]+$', '', item)
                
                # Cleaning values: remove currency symbols and whitespace
                val_curr = re.sub(r'[\$€£\s]', '', val_curr)
                val_prev = re.sub(r'[\$€£\s]', '', val_prev)
                
                # Filter out garbage
                if item and len(item) > 2 and not item.isnumeric():
                    data.append({
                        "Item": item,
                        "Current": val_curr,
                        "Previous": val_prev
                    })
        return data

    def _process_deepseek(self, pdf_bytes: bytes) -> List[Dict[str, Any]]:
        """
        AI-powered extraction using DeepSeek.
        Sends a summary of the document for extraction or processes first few pages.
        Note: For a production app, we would rasterize images or use a vision-capable endpoint.
        """
        if not self.client:
            logger.warning("DeepSeek client not configured. Falling back to mock/tesseract.")
            return []

        try:
            # We rasterize the first page for the AI to analyze
            images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, poppler_path=self.poppler_path)
            if not images:
                return []
            
            # Simple simulation: Extracting text from first page via Tesseract as context
            # or in a real scenario, sending the image to a Vision model.
            # DeepSeek V3/R1 has great reasoning but we use text-based extraction context here.
            text_context = pytesseract.image_to_string(self._preprocess_image(images[0]))
            
            prompt = f"""
            Extract the following financial data from this document text into a JSON list of objects.
            Each object must have 'Item', 'Current', and 'Previous' keys.
            Only return the JSON list, nothing else.
            
            TEXT:
            {text_context[:4000]}
            """
            
            response = self.client.chat.completions.create(
                model=self.deepseek_model,
                messages=[
                    {"role": "system", "content": "You are a financial data extraction assistant. Return JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result_json = response.choices[0].message.content
            # The model should return {"data": [...]} if we asked for JSON list in some formats, 
            # or just the list if allowed. We'll handle both.
            import json
            extracted = json.loads(result_json)
            if isinstance(extracted, dict) and "data" in extracted:
                return extracted["data"]
            return extracted if isinstance(extracted, list) else []

        except Exception as e:
            logger.error(f"DeepSeek OCR failed: {e}")
            return []

    def extract_from_pdf(self, pdf_bytes: bytes, engine: str = "tesseract") -> Dict[str, Any]:
        """
        Converts PDF pages to images, then runs OCR to extract financial tables.
        Processes all pages using selected engine.
        """
        if engine == "deepseek":
            logger.info("Using DeepSeek for AI-powered extraction...")
            deep_data = self._process_deepseek(pdf_bytes)
            if deep_data:
                return {
                    "status": "success",
                    "data": deep_data,
                    "metadata": {"engine": "deepseek", "items_found": len(deep_data)}
                }
            logger.warning("DeepSeek failed or returned empty. Falling back to Tesseract.")

        try:
            # 1. Convert PDF to Images
            if engine == "tesseract":
                self._check_binaries()
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
                    # Apply image preprocessing for better OCR
                    processed_img = self._preprocess_image(image)
                    text = pytesseract.image_to_string(processed_img)
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
