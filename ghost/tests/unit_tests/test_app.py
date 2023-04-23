from typing import Any, Dict
import unittest
from unittest.mock import MagicMock, patch

from twilio.rest import Client

from app import app, CONVERSATIONS


MESSAGE_SID = "abc123"


def _make_mock_twilio_client() -> Client:
    mock_client = MagicMock(spec=Client)
    mock_message = MagicMock()
    mock_message.sid = MESSAGE_SID
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
        cls.ai_phone_number = "+18008675309"

    @patch("app.initialize_agent")
    @patch("app._make_twilio_client")
    def test_agent_management(self, make_twilio_client, initialize_agent):
        mock_twilio_client = _make_mock_twilio_client()
        make_twilio_client.return_value = mock_twilio_client
        incoming_number = "+18001234567"
        data = {
            "Body": "Hey Ghost",
            "From": incoming_number,
        }
        reply = "Hi Marcos."
        initialize_agent.return_value = _make_mock_agent(reply)
        self.assertEqual(0, len(CONVERSATIONS))
        response = self.app.post("/sms", data=data, content_type="multipart/form-data")
        self.assertEqual(200, response.status_code)
        self.assertEqual(MESSAGE_SID, response.text)
        initialize_agent.assert_called_once()
        expected_call = {
            "body": reply,
            "from_": self.ai_phone_number,
            "to": incoming_number,
        }
        mock_twilio_client.messages.create.assert_called_once_with(**expected_call)
        self.assertEqual(1, len(CONVERSATIONS))

    @patch("app.initialize_agent")
    @patch("app._make_twilio_client")
    def test_unknown_number(self, make_twilio_client, initialize_agent):
        mock_twilio_client = _make_mock_twilio_client()
        make_twilio_client.return_value = mock_twilio_client
        incoming_number = "+18001111111"
        data = {
            "Body": "Hey Ghost",
            "From": incoming_number,
        }
        response = self.app.post("/sms", data=data, content_type="multipart/form-data")
        self.assertEqual(200, response.status_code)
        self.assertEqual("Unknown number.", response.text)
        initialize_agent.assert_not_called()
        mock_twilio_client.messages.create.assert_not_called()
