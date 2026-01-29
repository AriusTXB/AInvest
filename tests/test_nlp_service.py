import unittest
from unittest.mock import MagicMock, patch
from app.services.nlp_service import NLPService

class TestNLPService(unittest.TestCase):
    def setUp(self):
        # We patch the pipeline at the module level before instantiation
        with patch('app.services.nlp_service.pipeline') as mock_pipeline:
            self.service = NLPService()
            self.mock_pipeline = mock_pipeline

    def test_analyze_sentiment_success(self):
        """Test sentiment analysis with a successful model response."""
        mock_classifier = MagicMock()
        mock_classifier.return_value = [{'label': 'positive', 'score': 0.95}]
        self.service.classifier = mock_classifier
        self.service.mock_mode = False

        result = self.service.analyze_sentiment("Stock is going up!")
        self.assertEqual(result["sentiment"]["label"], "positive")
        self.assertFalse(result["is_mock"])

    def test_summarize_success(self):
        """Test summarization with a successful model response."""
        mock_summarizer = MagicMock()
        mock_summarizer.return_value = [{'summary_text': 'Short summary.'}]
        self.service.summarizer = mock_summarizer
        self.service.mock_mode = False

        # Input must be > 150 chars to bypass early return guard in summarize()
        long_input = (
            "This is a very long financial text that needs to be summarized into something shorter. "
            "The company reported strong earnings growth in the second quarter driven by increased demand."
        )
        result = self.service.summarize(long_input)
        self.assertEqual(result, "Short summary.")

    def test_mock_fallback_on_failure(self):
        """Test that mock-mode handles analysis if model fails."""
        self.service.mock_mode = True
        result = self.service.analyze_sentiment("Great profit growth")
        self.assertTrue(result["is_mock"])
        self.assertEqual(result["sentiment"]["label"], "positive")

    def test_summarize_edge_cases(self):
        """Test summarization with very short text."""
        short_text = "Too short."
        result = self.service.summarize(short_text)
        self.assertEqual(result, short_text)

if __name__ == "__main__":
    unittest.main()
