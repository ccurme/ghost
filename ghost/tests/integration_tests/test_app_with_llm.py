from typing import Callable
from unittest.mock import ANY, patch

from langchain.input import print_text

from tests.utils import TestApp


class TestAppWithLLM(TestApp):
    output_color = "green"

    def _test_response(
        self, make_twilio_client: Callable, incoming_number: str, incoming_message: str
    ) -> str:
        print_text(f"\nReceived: {incoming_message}", color=self.output_color)
        response, mock_twilio_client = self._post_request(
            make_twilio_client,
            incoming_number,
            incoming_message,
        )
        self.assertEqual(200, response.status_code)
        expected_call = {
            "body": ANY,
            "from_": self.ai_phone_number,
            "to": incoming_number,
        }
        mock_twilio_client.messages.create.assert_called_once_with(**expected_call)
        message = mock_twilio_client.messages.create.call_args.kwargs["body"]
        print_text(f"\nSent: {message}", color=self.output_color)

    @patch("app._make_twilio_client")
    def test_base_case(self, make_twilio_client):
        incoming_number = "+18001234567"
        print_text(f"\n{incoming_number}:", color=self.output_color)
        self._test_response(make_twilio_client, incoming_number, "Hey Ghost")
        self._test_response(
            make_twilio_client, incoming_number, "What is your favorite food?"
        )
