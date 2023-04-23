import json
import os
from typing import List

from langchain import OpenAI
from langchain.agents.agent import AgentExecutor
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import Document
from langchain.tools.vectorstore.tool import VectorStoreQATool
from langchain.vectorstores import FAISS

from base import ConversationalAgent


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
    ai_prefix = ai_settings["name"]
    human_prefix = contact_settings["name"]
    chat_partner_description = f"""
    {contact_settings["relation"]}
    {ai_prefix} might refer to {human_prefix} by {_stringify_list(contact_settings["aliases"])}.

    Example:
    {contact_settings["example"]}
    """
    verbose = False
    llm = OpenAI(temperature=0, verbose=verbose)
    memory = ConversationBufferMemory(
        memory_key="chat_history", human_prefix=human_prefix, ai_prefix=ai_prefix
    )
    qa_tool = _make_qa_tool(ai_prefix, ai_settings["facts"])
    tools = [qa_tool]

    callback_manager = None
    agent_kwargs = None
    agent_cls = ConversationalAgent
    agent_kwargs = agent_kwargs or {}
    agent_obj = agent_cls.from_llm_and_tools(
        llm,
        tools,
        callback_manager=callback_manager,  # **agent_kwargs
        memory=memory,
        verbose=verbose,
        human_prefix=human_prefix,
        ai_prefix=ai_prefix,
        chat_partner_description=chat_partner_description,
        prefix=ai_settings["prompt_prefix"],
    )
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent_obj,
        tools=tools,
        callback_manager=callback_manager,
        memory=memory,
        verbose=verbose,
    )

    return agent_executor
