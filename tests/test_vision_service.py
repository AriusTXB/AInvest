import unittest
from app.services.vision_service import VisionService
import os

class TestVisionService(unittest.TestCase):
    def setUp(self):
        self.service = VisionService()

    def test_parse_text_simple_table(self):
        """Test the heuristic parser with a clear table-like string."""
        sample_text = """
        Balance Sheet
        Cash and Cash Equivalents 1,200.00 900.00
        Total Assets $ 12,345.00 11,000.00
        Long Term Debt 5,000 4,800
        """
        results = self.service._parse_text(sample_text)
        
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["Item"], "Cash and Cash Equivalents")
        self.assertEqual(results[0]["Current"], "1,200.00")
        self.assertEqual(results[0]["Previous"], "900.00")
        
        self.assertEqual(results[1]["Item"], "Total Assets")
        self.assertEqual(results[1]["Current"], "12,345.00")
        self.assertEqual(results[1]["Previous"], "11,000.00")

    def test_mock_fallback(self):
        """Test that mock data is returned when extraction fails due to missing dependencies."""
        # Providing null bytes should trigger an error in convert_from_bytes
        # even if dependencies are met, but here we check the response structure
        result = self.service.extract_from_pdf(b"not a pdf")
        self.assertIn("status", result)
        self.assertIn("data", result)
        
    def test_regex_cleaning(self):
        """Test that regex cleaning handles dots and spaces."""
        sample_text = "...Total Assets... 100 50"
        results = self.service._parse_text(sample_text)
        self.assertEqual(results[0]["Item"], "Total Assets")

if __name__ == "__main__":
    unittest.main()
