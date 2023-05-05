"""Script to sample records for a given contact."""
import argparse
import json
import os
import sqlite3
import sys
from typing import List

import pandas as pd

sys.path.append("..")
from fine_tuning.iphone_sqlite import pull_messages_for_contact_number
from fine_tuning.sampling_utils import (
    collect_samples,
    conversation_to_prompt,
    load_jsonl,
)
from utils import format_prompt_components_without_tools, load_settings


RANDOM_STATE = 0  # seed for numpy


def _get_contact_settings_from_contacts(
    contacts: List[dict], contact_number: str
) -> dict:
    """Get contact settings from list of contacts."""
    contacts_path = os.getenv("CONTACTS_PATH", "settings/contacts.json")
    contact_settings = [
        contact for contact in contacts if contact["phone_number"] == contact_number
    ]
    if not contact_settings:
        raise ValueError(f"{contact_number} not in contacts at {contacts_path}.")
    elif len(contact_settings) > 1:
        raise ValueError(
            f"{contact_number} has duplicate records in contacts at {contacts_path}."
        )
    else:
        return contact_settings[0]


def _touch(file_path: str) -> None:
    """Raise error if path exists, else create empty file."""
    if os.path.exists(file_path):
        raise ValueError(f"Path exists: {file_path}.")
    else:
        with open(file_path, "w") as fp:
            pass


def _read_records_and_write_training_data(
    ai_settings: dict,
    contact_settings: dict,
    path_to_read_records: str,
    path_to_output_train_data: str,
):
    """Load in conversation records and format prompts and completions for fine-tuning."""
    ai_prefix, human_prefix, prefix, suffix = format_prompt_components_without_tools(
        ai_settings,
        contact_settings,
        fine_tune=True,
    )
    prompt_template = "\n".join([prefix, suffix, "", f"{ai_prefix}:"])
    conversations = load_jsonl(path_to_read_records)
    for conversation in conversations:
        conversation_df = pd.DataFrame.from_dict(conversation)
        prompt, completion = conversation_to_prompt(
            prompt_template, conversation_df, ai_prefix, human_prefix
        )

        record = {"prompt": prompt, "completion": completion}
        with open(path_to_output_train_data, "a") as fp:
            fp.write(f"{json.dumps(record)}\n")


def main(
    path_to_sqlite_db: str,
    contact_number: str,
    path_to_output_records: str,
    path_to_output_train_data: str,
) -> None:
    """Sample records for a contact."""
    # Fail fast if there's a configuration issue.
    ai_settings, contacts = load_settings()
    contact_settings = _get_contact_settings_from_contacts(contacts, contact_number)
    _touch(path_to_output_records)
    connection = sqlite3.connect(path_to_sqlite_db)
    message_df = pull_messages_for_contact_number(connection, contact_number)

    # Collect samples
    with open(path_to_output_records, "a") as fp:
        collect_samples(message_df, fp, random_state=RANDOM_STATE)

    _read_records_and_write_training_data(
        ai_settings, contact_settings, path_to_output_records, path_to_output_train_data
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate and preview sample records for a contact."
    )
    parser.add_argument("--path_to_sqlite_db")
    parser.add_argument("--contact_number")
    parser.add_argument("--path_to_output_records")
    parser.add_argument("--path_to_output_train_data")
    args = parser.parse_args()
    main(
        args.path_to_sqlite_db,
        args.contact_number,
        args.path_to_output_records,
        args.path_to_output_train_data,
    )
