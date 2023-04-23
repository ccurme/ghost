from typing import Any
from unittest.mock import MagicMock, patch

import app
from tests.utils import make_mock_twilio_client, TestApp


def _make_mock_agent(response: str) -> Any:
    """Make mock Chain for unit tests."""
    mock_agent = MagicMock()
    mock_agent.run.return_value = response
    mock_agent.agent.llm_chain.verbose = True

    return mock_agent


class TestAppUnits(TestApp):

    @patch("app.initialize_agent")
    @patch("app._make_twilio_client")
    def test_agent_management(self, make_twilio_client, initialize_agent):
        self.assertEqual(0, len(app.AGENT_CACHE))
        reply = "Hello"
        initialize_agent.return_value = _make_mock_agent(reply)
        self._test_response(
            make_twilio_client,
            "+18001234567",
            "Hey Ghost",
            reply,
        )
        initialize_agent.assert_called_once()
        self.assertEqual(1, len(app.AGENT_CACHE))
        self._test_response(
            make_twilio_client,
            "+18001234567",
            "How are you?",
            reply,
        )
        initialize_agent.assert_called_once()
        self.assertEqual(1, len(app.AGENT_CACHE))
        self._test_response(
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
        mock_twilio_client = make_mock_twilio_client()
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
