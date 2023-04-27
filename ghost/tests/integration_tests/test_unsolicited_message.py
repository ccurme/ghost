from textwrap import dedent
import unittest

from langchain.input import print_text
from langchain.schema import AIMessage, HumanMessage

from agent_utils import initialize_agent
import unsolicited_message
from utils import load_settings


class TestUnsolicitedMessage(unittest.TestCase):
    def test_unsolicited_message(self):
        ai_settings, contacts = load_settings()
        contact_settings = contacts[0]
        agent = initialize_agent(ai_settings, contact_settings)
        _ = agent.run("Hi, how are you?")

        ai_prefix = ai_settings["name"]
        human_prefix = contact_settings["name"]
        prompt = unsolicited_message.get_unsolicited_message_prompt(
            ai_prefix, human_prefix
        )

        message = unsolicited_message.generate_unsolicited_message(
            prompt,
            agent,
            ai_settings,
            contact_settings,
        )
        self.assertEqual(3, len(agent.memory.chat_memory.messages))
        message_1, message_2, message_3 = agent.memory.chat_memory.messages
        self.assertIsInstance(message_1, HumanMessage)
        self.assertIsInstance(message_2, AIMessage)
        self.assertIsInstance(message_3, AIMessage)
        self.assertEqual(message, message_3.content)

        _ = agent.run("Sorry, can you repeat what you just said?")
        self.assertEqual(5, len(agent.memory.chat_memory.messages))

        prompt = dedent(
            f"""
        *{ai_prefix} then took the conversation in an entirely new direction with a random question:*

        {ai_prefix}:
        """
        )
        _ = unsolicited_message.generate_unsolicited_message(
            prompt,
            agent,
            ai_settings,
            contact_settings,
            temperature=0.7,
        )

        print_text(f"\n{agent.memory.buffer}", color="green")
