import os
import shutil
import unittest
from unittest.mock import patch
import uuid

import pandas as pd

from fine_tuning import sample_records
from fine_tuning.sampling_utils import load_jsonl


MESSAGE_DF = pd.DataFrame.from_records(
    [
        {"text": "hi Ghost", "is_from_me": 0},
        {"text": "hi", "is_from_me": 1},
        {"text": "what is your social security number?", "is_from_me": 0},
        {"text": "it's 000-11-2222", "is_from_me": 1},
        {"text": "thank you.", "is_from_me": 0},
        {"text": "what are you doing?", "is_from_me": 0},
        {"text": "peeling a banana", "is_from_me": 1},
        {"text": "wbu?", "is_from_me": 1},
    ]
)


class TestSampleRecords(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output_folder = os.path.join("/tmp", str(uuid.uuid4()))
        cls.contact_number = "+18001234567"
        cls.sqlite_db = ":memory:"
        cls.path_to_output_records = os.path.join(cls.output_folder, "records.jsonl")
        cls.path_to_output_train_data = os.path.join(
            cls.output_folder, "train_records.jsonl"
        )
        os.mkdir(cls.output_folder)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.output_folder)

    def _reset(self):
        self.tearDownClass()
        self.setUpClass()

    @patch("fine_tuning.sampling_utils.input")
    @patch("fine_tuning.sample_records.pull_messages_for_contact_number")
    def test_sample_records(self, pull_messages, user_input):
        pull_messages.return_value = MESSAGE_DF.copy()
        user_input.side_effect = ["n", "n", "q"]
        sample_records.main(
            self.sqlite_db,
            self.contact_number,
            self.path_to_output_records,
            self.path_to_output_train_data,
        )
        self.assertEqual(1, len(os.listdir(self.output_folder)))
        records = load_jsonl(self.path_to_output_records)
        self.assertEqual([], records)

        # Test that we raise before overwriting.
        with self.assertRaises(ValueError):
            sample_records.main(
                self.sqlite_db,
                self.contact_number,
                self.path_to_output_records,
                self.path_to_output_train_data,
            )

        # Test records are as expected
        self._reset()
        user_input.side_effect = ["n", "y", "y", "q"]
        sample_records.main(
            self.sqlite_db,
            self.contact_number,
            self.path_to_output_records,
            self.path_to_output_train_data,
        )
        self.assertEqual(2, len(os.listdir(self.output_folder)))
        self.assertTrue(os.path.exists(self.path_to_output_records))
        self.assertTrue(os.path.exists(self.path_to_output_train_data))

        records = load_jsonl(self.path_to_output_records)
        self.assertEqual(2, len(records))
        self.assertEqual(set(["text", "is_from_me"]), set(records[0].keys()))

        train_data = load_jsonl(self.path_to_output_train_data)
        self.assertEqual(2, len(train_data))
        self.assertEqual(set(["prompt", "completion"]), set(train_data[0].keys()))

        # Test on small data
        self._reset()
        pull_messages.return_value = MESSAGE_DF.iloc[:3].copy()
        user_input.side_effect = ["n", "n", "q"]
        sample_records.main(
            self.sqlite_db,
            self.contact_number,
            self.path_to_output_records,
            self.path_to_output_train_data,
        )

        # Test unknown number
        self._reset()
        user_input.side_effect = ["q"]
        with self.assertRaises(ValueError):
            sample_records.main(
                self.sqlite_db,
                "+18008675309",
                self.path_to_output_records,
                self.path_to_output_train_data,
            )
