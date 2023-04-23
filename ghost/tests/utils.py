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

    def _post_request(
        self,
        make_twilio_client: Callable,
        incoming_number: str,
        incoming_message: str,
    ):
        mock_twilio_client = make_mock_twilio_client()
        make_twilio_client.return_value = mock_twilio_client
        data = {
            "Body": incoming_message,
            "From": incoming_number,
        }
        response = self.app.post("/sms", data=data, content_type="multipart/form-data")

        return response, mock_twilio_client
