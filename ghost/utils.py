import json
import os
from textwrap import dedent
from typing import List, Tuple

from langchain import OpenAI
from langchain.agents.agent import AgentExecutor
from langchain.agents.conversational.base import ConversationalAgent
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import Document
from langchain.tools.vectorstore.tool import VectorStoreQATool
from langchain.vectorstores import FAISS

from prompt import CONVERSATION_HISTORY, FORMAT_INSTRUCTIONS, INTRO_TO_CHAT_PARTNER, INTRO_TO_TOOLS, SUFFIX


def _stringify_list(input_list):
    """Represent list of strings as a list."""
    result = ", ".join(f'"{element}"' for element in input_list)

    return result


def _make_qa_tool(ai_name: str, documents: List[Document]):
    vector_store = FAISS.from_documents(documents, OpenAIEmbeddings())
    # TODO: `VectorDBQA` is deprecated - please use `from langchain.chains import RetrievalQA`
    # See https://discord.com/channels/1038097195422978059/1096563375460339793/1096564550825951313 for use as a tool.
    qa_tool = VectorStoreQATool(
        name=f"Look up personal facts",
        description=f"Retrieve personal facts about {ai_name}",
        vectorstore=vector_store,
        llm=OpenAI(temperature=0, verbose=False),
    )

    return qa_tool


def format_prompt_components_without_tools(ai_settings: dict, contact_settings: dict) -> Tuple[str]:
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
    suffix = CONVERSATION_HISTORY

    return ai_prefix, human_prefix, prefix, suffix


def format_prompt_components_with_tools(ai_settings: dict, contact_settings: dict) -> Tuple[str]:
    """Format prompt components for agent."""
    ai_prefix, human_prefix, prefix, suffix = format_prompt_components_without_tools(ai_settings, contact_settings)
    intro_to_tools = INTRO_TO_TOOLS.format(ai_prefix=ai_prefix)

    prefix = "\n".join([prefix, intro_to_tools])
    prefix = prefix.replace("\t", "").replace("    ", "")
    format_instructions = FORMAT_INSTRUCTIONS.format(
        ai_prefix=ai_prefix, human_prefix=human_prefix
    )
    suffix = "\n".join([CONVERSATION_HISTORY, SUFFIX.format(human_prefix=human_prefix)])

    return ai_prefix, human_prefix, prefix, suffix, format_instructions


def load_prompt_prefix() -> str:
    """Load prompt prefix."""
    doc_path = os.getenv("PROMPT_PREFIX_PATH", "settings/prompt_prefix.md")
    with open(doc_path, "r") as fp:
        prompt_prefix = fp.read()

    return prompt_prefix


def load_settings() -> dict:
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


def initialize_agent(ai_settings: dict, contact_settings: dict) -> AgentExecutor:
    """Make instance of AgentExecutor."""
    (
        ai_prefix,
        human_prefix,
        prefix,
        suffix,
        format_instructions,
    ) = format_prompt_components_with_tools(
        ai_settings,
        contact_settings,
    )
    verbose = False
    llm = OpenAI(temperature=0, verbose=verbose)
    memory = ConversationBufferMemory(
        memory_key="chat_history", human_prefix=human_prefix, ai_prefix=ai_prefix
    )
    qa_tool = _make_qa_tool(ai_prefix, ai_settings["facts"])
    tools = [qa_tool]

    agent = ConversationalAgent.from_llm_and_tools(
        llm,
        tools,
        callback_manager=None,
        memory=memory,
        verbose=verbose,
        human_prefix=human_prefix,
        ai_prefix=ai_prefix,
        prefix=prefix,
        suffix=suffix,
        format_instructions=format_instructions,
    )
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        callback_manager=None,
        memory=memory,
        verbose=verbose,
    )

    return agent_executor
