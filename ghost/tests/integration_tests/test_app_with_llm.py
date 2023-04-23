from typing import Callable
from unittest.mock import ANY, patch

from langchain.input import print_text

from tests.utils import TestApp


class TestAppWithLLM(TestApp):
    def _test_response(
        self,
        make_twilio_client: Callable,
        incoming_number: str,
        incoming_message: str,
        color: str = "green",
    ) -> str:
        print_text(f"\nReceived: {incoming_message}", color=color)
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
        print_text(f"\nSent: {message}", color=color)

        return message

    @patch("app._make_twilio_client")
    def test_base_case(self, make_twilio_client):
        incoming_number = "+18001234567"
        color = "green"
        print_text(f"\n{incoming_number}:", color=color)
        _ = self._test_response(
            make_twilio_client, incoming_number, "Hey Ghost", color=color
        )
        message = self._test_response(
            make_twilio_client, incoming_number, "Where are you right now?", color=color
        )
        self.assertIn("stuck in limbo", message.lower())
        message = self._test_response(
            make_twilio_client,
            incoming_number,
            "Can you remind me your favorite food?",
            color=color,
        )
        self.assertIn("shrimp", message.lower())
        print_text(f"\n")

        incoming_number = "+18005555555"
        color = "red"
        print_text(f"\n{incoming_number}:", color=color)
        message = self._test_response(
            make_twilio_client, incoming_number, "hey", color=color
        )
        self.assertIn("dear", message.lower())
        print_text(f"\n")

        incoming_number = "+18001234567"
        color = "green"
        print_text(f"\n{incoming_number}:", color=color)
        message = self._test_response(
            make_twilio_client,
            incoming_number,
            "read back what I just asked you",
            color=color,
        )
        self.assertIn("food", message.lower())
