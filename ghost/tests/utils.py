from typing import Callable
import unittest
from unittest.mock import MagicMock

from twilio.rest import Client

from app import app


MESSAGE_SID = "abc123"


def make_mock_twilio_client() -> Client:
    mock_client = MagicMock(spec=Client)
    mock_message = MagicMock()
    mock_message.sid = MESSAGE_SID
    mock_client.messages.create.return_value = mock_message

    return mock_client


class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.ai_phone_number = "+18008675309"

    def _test_response(
        self,
        make_twilio_client: Callable,
        incoming_number: str,
        incoming_message: str,
        reply: str,
    ):
        mock_twilio_client = make_mock_twilio_client()
        make_twilio_client.return_value = mock_twilio_client
        data = {
            "Body": incoming_message,
            "From": incoming_number,
        }
        reply = "Hello"
        response = self.app.post("/sms", data=data, content_type="multipart/form-data")
        self.assertEqual(200, response.status_code)
        self.assertEqual(MESSAGE_SID, response.text)
        expected_call = {
            "body": reply,
            "from_": self.ai_phone_number,
            "to": incoming_number,
        }
        mock_twilio_client.messages.create.assert_called_once_with(**expected_call)
