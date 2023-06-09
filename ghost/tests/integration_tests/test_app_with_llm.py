from unittest.mock import ANY

from flask import Response
from langchain.input import print_text
from twilio.rest import Client

from tests.utils import TestApp
from unsolicited_message import get_unsolicited_message_prompt
from utils import load_settings


class TestAppWithLLM(TestApp):
    def _test_response(
        self,
        response: Response,
        mock_twilio_client: Client,
        chat_partner_phone_number: str,
        color: str = "green",
    ) -> str:
        self.assertEqual(200, response.status_code)
        expected_call = {
            "body": ANY,
            "from_": self.ai_phone_number,
            "to": chat_partner_phone_number,
        }
        mock_twilio_client.messages.create.assert_called_once_with(**expected_call)
        message = mock_twilio_client.messages.create.call_args.kwargs["body"]
        print_text(f"\nSent: {message}", color=color)

        return message

    def test_llm_reply(self):
        incoming_number = "+18001234567"
        color = "green"
        print_text(f"\n{incoming_number}:", color=color)
        incoming_message = "Hey Ghost"
        print_text(f"\nReceived: {incoming_message}", color=color)
        response, mock_twilio_client = self._post_llm_reply(
            incoming_number,
            incoming_message,
        )
        _ = self._test_response(
            response, mock_twilio_client, incoming_number, color=color
        )

        incoming_message = "Where are you right now?"
        print_text(f"\nReceived: {incoming_message}", color=color)
        response, mock_twilio_client = self._post_llm_reply(
            incoming_number,
            incoming_message,
        )
        message = self._test_response(
            response, mock_twilio_client, incoming_number, color=color
        )
        self.assertIn("stuck in limbo", message.lower())

        incoming_message = "Can you remind me your favorite food?"
        print_text(f"\nReceived: {incoming_message}", color=color)
        response, mock_twilio_client = self._post_llm_reply(
            incoming_number,
            incoming_message,
        )
        message = self._test_response(
            response, mock_twilio_client, incoming_number, color=color
        )
        self.assertIn("shrimp", message.lower())
        print_text(f"\n")

        incoming_number = "+18005555555"
        color = "red"
        print_text(f"\n{incoming_number}:", color=color)
        incoming_message = "hey"
        print_text(f"\nReceived: {incoming_message}", color=color)
        response, mock_twilio_client = self._post_llm_reply(
            incoming_number,
            incoming_message,
        )
        message = self._test_response(
            response, mock_twilio_client, incoming_number, color=color
        )
        self.assertIn("dear", message.lower())
        print_text(f"\n")

        incoming_number = "+18001234567"
        color = "green"
        print_text(f"\n{incoming_number}:", color=color)
        incoming_message = "read back what I just asked you"
        print_text(f"\nReceived: {incoming_message}", color=color)
        response, mock_twilio_client = self._post_llm_reply(
            incoming_number,
            incoming_message,
        )
        message = self._test_response(
            response, mock_twilio_client, incoming_number, color=color
        )
        self.assertIn("food", message.lower())

        # Unsolicited message
        ai_settings, contacts = load_settings()
        contact_settings = [
            contact
            for contact in contacts
            if contact["phone_number"] == incoming_number
        ][0]
        prompt = get_unsolicited_message_prompt(
            ai_settings["name"], contact_settings["name"]
        )
        response, mock_twilio_client = self._post_unsolicited_message(
            incoming_number,
            prompt,
        )
        _ = self._test_response(
            response, mock_twilio_client, incoming_number, color=color
        )
