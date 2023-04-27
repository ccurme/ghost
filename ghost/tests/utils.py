from typing import Callable
import unittest
from unittest.mock import MagicMock, patch

from twilio.request_validator import RequestValidator
from twilio.rest import Client

from app import app

MESSAGE_SID = "abc123"


def make_mock_twilio_client() -> Client:
    mock_client = MagicMock(spec=Client)
    mock_message = MagicMock()
    mock_message.sid = MESSAGE_SID
    mock_client.messages.create.return_value = mock_message

    return mock_client


def make_mock_request_validator(valid) -> RequestValidator:
    mock_validator = MagicMock(spec=RequestValidator)
    mock_validator.validate.return_value = valid

    return mock_validator


class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.ai_phone_number = "+18008675309"

    @patch("app.RequestValidator")
    def _post_sms(
        self,
        make_twilio_client: Callable,
        incoming_number: str,
        incoming_message: str,
        make_request_validator: Callable,
    ):
        mock_request_validator = make_mock_request_validator(True)
        make_request_validator.return_value = mock_request_validator
        mock_twilio_client = make_mock_twilio_client()
        make_twilio_client.return_value = mock_twilio_client
        data = {
            "Body": incoming_message,
            "From": incoming_number,
        }
        response = self.app.post("/sms", data=data, content_type="multipart/form-data")

        return response, mock_twilio_client
    
    def _post_unsolicited_message(
        self,
        make_twilio_client: Callable,
        outgoing_number: str,
        prompt: str,
    ):
        mock_twilio_client = make_mock_twilio_client()
        make_twilio_client.return_value = mock_twilio_client
        data = {"to": outgoing_number, "prompt": prompt}
        response = self.app.post("/unsolicited_message", data=data, content_type="multipart/form-data")

        return response, mock_twilio_client
