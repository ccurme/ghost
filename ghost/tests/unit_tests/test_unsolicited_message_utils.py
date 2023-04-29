from textwrap import dedent
import unittest

import unsolicited_message


class TestUnsolicitedMessageUtils(unittest.TestCase):
    def test_extract_message(self):
        message = """
        Remember when we went to the shrimp restaurant?
        Marcos: Yeah, I remember, good times.
        """
        message = dedent(message.strip())
        result = unsolicited_message._extract_first_message(message)
        self.assertEqual("Remember when we went to the shrimp restaurant?", result)

        message = "so what else is new?"
        result = unsolicited_message._extract_first_message(message)
        self.assertEqual(message, result)
