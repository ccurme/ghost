import json
import os
from typing import Tuple

from langchain.text_splitter import Document

from prompt import (
    CONVERSATION_HISTORY,
    FINE_TUNE_CONVERSATION_HISTORY,
    INTRO_TO_CHAT_PARTNER,
)


def _stringify_list(input_list):
    """Represent list of strings as a list."""
    result = ", ".join(f'"{element}"' for element in input_list)

    return result


def format_prompt_components_without_tools(
    ai_settings: dict,
    contact_settings: dict,
    fine_tune: bool = False,
) -> Tuple[str]:
    """Format prompt components but for tools."""
    ai_prefix = ai_settings["name"]
    human_prefix = contact_settings["name"]
    chat_partner_description = f"""
    {contact_settings["relation"]}
    {ai_prefix} might refer to {human_prefix} by {_stringify_list(contact_settings["aliases"])}.

    Example:
    {contact_settings["example"]}
    """
    intro_to_chat_partner = INTRO_TO_CHAT_PARTNER.format(
        ai_prefix=ai_prefix,
        human_prefix=human_prefix,
        chat_partner_description=chat_partner_description,
    )
    prefix = f"""{ai_settings["prompt_prefix"]}
    {intro_to_chat_partner}
    """
    prefix = prefix.replace("\t", "").replace("    ", "")
    if fine_tune:
        suffix = FINE_TUNE_CONVERSATION_HISTORY
    else:
        suffix = CONVERSATION_HISTORY

    return ai_prefix, human_prefix, prefix, suffix


def load_prompt_prefix() -> str:
    """Load prompt prefix."""
    doc_path = os.getenv("PROMPT_PREFIX_PATH", "settings/prompt_prefix.md")
    with open(doc_path, "r") as fp:
        prompt_prefix = fp.read()

    return prompt_prefix


def load_settings() -> Tuple[dict, list]:
    """Load AI settings and contacts."""
    # TODO: impose structure on this dict via named tuple or dataclass
    # TODO: use loader abstractions from langchain
    # TODO: generalize this to map facts to additional chat partners
    doc_path = os.getenv("CONTACTS_PATH", "settings/contacts.json")
    with open(doc_path, "r") as fp:
        ai_settings, contacts = json.load(fp)

    ai_settings["facts"] = [
        Document(page_content=text, metadata={"source": doc_path})
        for text in ai_settings["facts"]
    ]

    ai_settings["prompt_prefix"] = load_prompt_prefix()

    return ai_settings, contacts
