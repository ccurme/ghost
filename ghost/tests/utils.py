from typing import Callable
import unittest
from unittest.mock import MagicMock, patch

from flask_jwt_extended import create_access_token
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
    @patch("app._make_twilio_client")
    def _post_llm_reply(
        self,
        incoming_number: str,
        incoming_message: str,
        make_twilio_client: Callable,
        make_request_validator: Callable,
        valid_request: bool = True,
    ):
        mock_request_validator = make_mock_request_validator(valid_request)
        make_request_validator.return_value = mock_request_validator
        mock_twilio_client = make_mock_twilio_client()
        make_twilio_client.return_value = mock_twilio_client
        data = {
            "Body": incoming_message,
            "From": incoming_number,
        }
        response = self.app.post("/llm_reply", data=data, content_type="multipart/form-data")

        return response, mock_twilio_client

    @patch("app._make_twilio_client")
    def _post_unsolicited_message(
        self,
        outgoing_number: str,
        prompt: str,
        make_twilio_client: Callable,
    ):
        mock_twilio_client = make_mock_twilio_client()
        make_twilio_client.return_value = mock_twilio_client
        data = {"to": outgoing_number, "prompt": prompt}
        with app.test_request_context():
            app.config["SECRET_KEY"] = "secret"
            access_token = create_access_token(identity=123)
        headers = {"Authorization": f"Bearer {access_token}"}
        response = self.app.post(
            "/llm_send",
            data=data,
            content_type="multipart/form-data",
            headers=headers,
        )

        return response, mock_twilio_client
