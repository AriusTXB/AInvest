import unittest
from unittest.mock import MagicMock, patch
from app.services.vision_service import VisionService

class TestVisionDeepSeek(unittest.TestCase):
    def setUp(self):
        self.vision_service = VisionService()

    @patch('app.services.vision_service.OpenAI')
    @patch('app.services.vision_service.convert_from_bytes')
    @patch('app.services.vision_service.pytesseract.image_to_string')
    @patch.object(VisionService, '_preprocess_image')
    def test_deepseek_extraction_flow(self, mock_preprocess, mock_tesseract, mock_convert, mock_openai):
        """Test the full DeepSeek extraction flow with mocks."""
        # 1. Mock OpenAI response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        self.vision_service.client = mock_client
        
        mock_choice = MagicMock()
        mock_choice.message.content = '{"data": [{"Item": "AI Test", "Current": "100", "Previous": "50"}]}'
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        # 2. Mock Image conversion and Tesseract
        mock_convert.return_value = [MagicMock()]
        mock_preprocess.return_value = MagicMock()
        mock_tesseract.return_value = "Mocked PDF Content"

        # 3. Execute
        result = self.vision_service.extract_from_pdf(b"dummy pdf", engine="deepseek")

        # 4. Assertions
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["metadata"]["engine"], "deepseek")
        self.assertEqual(result["data"][0]["Item"], "AI Test")
        self.assertEqual(len(result["data"]), 1)

    def test_deepseek_fallback_to_tesseract(self):
        """Test that if DeepSeek is not configured, it falls back to Tesseract logic."""
        self.vision_service.client = None
        
        with patch.object(VisionService, '_process_deepseek', return_value=[]):
            # We don't want to run full Tesseract in unit test if possible, 
            # but we want to see it moving past the DeepSeek check.
            with patch('app.services.vision_service.convert_from_bytes', side_effect=Exception("Stop here")):
                result = self.vision_service.extract_from_pdf(b"dummy pdf", engine="deepseek")
                # Should hit the conversion error in the main block instead of returning deep_data
                self.assertEqual(result["status"], "mock")

if __name__ == "__main__":
    unittest.main()
