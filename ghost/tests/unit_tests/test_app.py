from typing import Any
import unittest
from unittest.mock import MagicMock, patch

from twilio.rest import Client

from app import app


def _make_mock_twilio_client() -> Client:
    mock_client = MagicMock(spec=Client)
    mock_message = MagicMock()
    mock_message.sid = "abc123"
    mock_client.messages.create.return_value = mock_message

    return mock_client


def _make_mock_agent(response: str) -> Any:
    """Make mock Chain for unit tests."""
    mock_agent = MagicMock()
    mock_agent.run.return_value = response
    mock_agent.agent.llm_chain.verbose = True

    return mock_agent


class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()

    @patch("app.initialize_agent")
    @patch("app._make_twilio_client")
    def test_basic_use(self, make_twilio_client, initialize_agent):
        make_twilio_client.return_value = _make_mock_twilio_client()
        initialize_agent.return_value = _make_mock_agent("Hi Marcos.")
        data = {
            "Body": "Hey Ghost",
            "From": "+18001234567",
        }
        response = self.app.post("/sms", data=data, content_type="multipart/form-data")
        self.assertEqual(200, response.status_code)
