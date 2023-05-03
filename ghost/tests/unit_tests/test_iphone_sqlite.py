from datetime import datetime
import sqlite3
import unittest

import pandas as pd

from fine_tuning import iphone_sqlite


class TestIPhoneSqlite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection = sqlite3.connect(":memory:")
        cls.chat = pd.DataFrame(
            [
                {"ROWID": 1, "chat_identifier": "+18001234567"},
                {"ROWID": 2, "chat_identifier": "+18005555555"},
            ]
        )
        cls.chat.to_sql(name="chat", con=cls.connection)

        cls.chat_message_join = pd.DataFrame(
            [
                {"message_id": 1, "chat_id": 1},
                {"message_id": 2, "chat_id": 2},
                {"message_id": 3, "chat_id": 1},
                {"message_id": 4, "chat_id": 2},
            ]
        )
        cls.chat_message_join.to_sql(name="chat_message_join", con=cls.connection)

        cls.message = pd.DataFrame(
            [
                {
                    "ROWID": 1,
                    "date": 232694003000000000,
                    "message_date": 232694003000000000,
                    "text": "hi Ghost",
                    "is_from_me": 0,
                },
                {
                    "ROWID": 2,
                    "date": 232730035000000000,
                    "message_date": 232730035000000000,
                    "text": "hey",
                    "is_from_me": 0,
                },
                {
                    "ROWID": 3,
                    "date": 232731000000000000,
                    "message_date": 232731000000000000,
                    "text": "hey dude",
                    "is_from_me": 1,
                },
                {
                    "ROWID": 4,
                    "date": 232732551000000000,
                    "message_date": 232732551000000000,
                    "text": "hi dear",
                    "is_from_me": 1,
                },
            ]
        )
        cls.message.to_sql(name="message", con=cls.connection)

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def test_pull_messages_for_contact_number(self):
        result = iphone_sqlite.pull_messages_for_contact_number(
            self.connection, "+18001234567"
        )
        _ = result["message_datetime"].apply(datetime.fromisoformat)  # check iso-format
        self.assertEqual(["hi Ghost", "hey dude"], result["text"].to_list())
        self.assertEqual([0, 1], result["is_from_me"].to_list())
        self.assertEqual(
            ["+18001234567", "+18001234567"], result["chat_identifier"].to_list()
        )

        result = iphone_sqlite.pull_messages_for_contact_number(
            self.connection, "+18005555555"
        )
        _ = result["message_datetime"].apply(datetime.fromisoformat)
        self.assertEqual(["hey", "hi dear"], result["text"].to_list())
        self.assertEqual([0, 1], result["is_from_me"].to_list())
        self.assertEqual(
            ["+18005555555", "+18005555555"], result["chat_identifier"].to_list()
        )
