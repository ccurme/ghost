import unittest
from unittest.mock import MagicMock, patch

from fine_tuning import inference
from utils import load_settings


class TestInference(unittest.TestCase):

    @patch("fine_tuning.inference.openai.Completion.create")
    def test_inference(self, create):
        mock_response = MagicMock()
        mock_response.choices = [{"text": "test response"}]
        create.return_value = mock_response
        ai_settings, contacts = load_settings()
        ai_settings["fine_tuned_model_name"] = "curie:ft-personal:test-2023-04-30-15-32-03"
        contact_settings = [
            contact
            for contact in contacts
            if contact["phone_number"] == "+18001234567"
        ][0]
        chain = inference.initialize_chain(ai_settings, contact_settings)
        response = chain.run("hi")
        expected_response = "test response"
        self.assertEqual(expected_response, response)
