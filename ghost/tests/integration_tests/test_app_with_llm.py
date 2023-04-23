from unittest.mock import patch

from app import app, CONVERSATIONS
from tests.utils import TestApp


class TestAppWithLLM(TestApp):
    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.ai_phone_number = "+18008675309"

    @patch("app.initialize_agent")
    @patch("app._make_twilio_client")
    def test_agent_management(self, make_twilio_client, initialize_agent):
        self.assertEqual(0, len(CONVERSATIONS))
        reply = "Hello"
        initialize_agent.return_value = _make_mock_agent(reply)
        self._test_response(
            make_twilio_client,
            "+18001234567",
            "Hey Ghost",
            reply,
        )
        initialize_agent.assert_called_once()
