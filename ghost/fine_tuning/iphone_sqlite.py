import sqlite3

import pandas as pd


def pull_messages_for_contact_number(
    connection: sqlite3.Connection, contact_number: str
) -> pd.DataFrame:
    """Pull text messages from iPhone sqlite backup for a particular phone number."""
    query = """
    SELECT
        datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_datetime,
        message.text,
        message.is_from_me,
        chat.chat_identifier
    FROM
        chat
        JOIN chat_message_join ON chat."ROWID" = chat_message_join.chat_id
        JOIN message ON chat_message_join.message_id = message."ROWID"
    WHERE message.text IS NOT NULL
        AND chat.chat_identifier = ?
    ORDER BY
        chat_identifier ASC,
        message_date ASC
    """
    df = pd.read_sql(query, connection, params=(contact_number,))
    df = df[
        ~df["text"].isin(
            ["Laughed at an image", "Loved an image", "Emphasized an image"]
        )
    ].reset_index(drop=True)

    return df
