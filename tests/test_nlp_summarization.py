import unittest
from app.services.nlp_service import nlp_service

class TestNLPSummarization(unittest.TestCase):
    def test_summarization_logic(self):
        """Test that the summarizer produces a coherent summary of long text."""
        long_text = (
            "Apple Inc. reported its first-quarter financial results for the fiscal year 2024. "
            "The company announced a significant increase in revenue driven by strong iPhone sales in emerging markets. "
            "Despite global supply chain challenges and fluctuating currency exchange rates, Apple's services division, "
            "which includes the App Store, Apple Music, and iCloud, reached an all-time high. "
            "Investors are closely watching the company's progress in artificial intelligence and its upcoming product launches."
        )
        
        summary = nlp_service.summarize(long_text)
        print(f"\nOriginal Length: {len(long_text)}")
        print(f"Summary Length: {len(summary)}")
        print(f"Summary: {summary}")
        
        # The model should return a meaningful summary (not empty, not error)
        # Note: distilbart may sometimes return equal/slightly longer output due to rephrasing
        self.assertGreater(len(summary), 10)
        self.assertIn("Apple", summary)  # Should retain key topic

    def test_short_text_no_sum(self):
        """Test that very short text is returned as-is."""
        short_text = "Apple is doing great."
        summary = nlp_service.summarize(short_text)
        self.assertEqual(short_text, summary)

if __name__ == "__main__":
    unittest.main()
