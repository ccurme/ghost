from typing import Any, Callable
from unittest.mock import MagicMock, patch

import app
from tests.utils import make_mock_twilio_client, MESSAGE_SID, TestApp


def _make_mock_agent(response: str) -> Any:
    """Make mock Chain for unit tests."""
    mock_agent = MagicMock()
    mock_agent.run.return_value = response
    mock_agent.agent.llm_chain.verbose = True

    return mock_agent


class TestAppUnits(TestApp):

    def _post_request_and_test(
        self,
        make_twilio_client: Callable,
        incoming_number: str,
        incoming_message: str,
        reply: str,
    ):
        response, mock_twilio_client = self._post_request(make_twilio_client, incoming_number, incoming_message)
        self.assertEqual(200, response.status_code)
        self.assertEqual(MESSAGE_SID, response.text)
        expected_call = {
            "body": reply,
            "from_": self.ai_phone_number,
            "to": incoming_number,
        }
        mock_twilio_client.messages.create.assert_called_once_with(**expected_call)

    @patch("app.initialize_agent")
    @patch("app._make_twilio_client")
    def test_agent_management(self, make_twilio_client, initialize_agent):
        self.assertEqual(0, len(app.AGENT_CACHE))
        reply = "Hello"
        initialize_agent.return_value = _make_mock_agent(reply)
        self._post_request_and_test(
            make_twilio_client,
            "+18001234567",
            "Hey Ghost",
            reply,
        )
        initialize_agent.assert_called_once()
        self.assertEqual(1, len(app.AGENT_CACHE))
        self._post_request_and_test(
            make_twilio_client,
            "+18001234567",
            "How are you?",
            reply,
        )
        initialize_agent.assert_called_once()
        self.assertEqual(1, len(app.AGENT_CACHE))
        self._post_request_and_test(
            make_twilio_client,
            "+18005555555",
            "Hi",
            reply,
        )
        self.assertEqual(2, initialize_agent.call_count)
        self.assertEqual(2, len(app.AGENT_CACHE))

    @patch("app.initialize_agent")
    @patch("app._make_twilio_client")
    def test_unknown_number(self, make_twilio_client, initialize_agent):
        response, mock_twilio_client = self._post_request(make_twilio_client, "+18001111111", "Hi")
        self.assertEqual(200, response.status_code)
        self.assertEqual("Unknown number.", response.text)
        initialize_agent.assert_not_called()
        mock_twilio_client.messages.create.assert_not_called()
