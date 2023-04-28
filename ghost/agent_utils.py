from typing import List, Tuple

from langchain import OpenAI
from langchain.agents.agent import AgentExecutor
from langchain.agents.conversational.base import ConversationalAgent
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import Document
from langchain.tools.vectorstore.tool import VectorStoreQATool
from langchain.vectorstores import FAISS

from prompt import CONVERSATION_HISTORY, FORMAT_INSTRUCTIONS, INTRO_TO_TOOLS, SUFFIX
from utils import format_prompt_components_without_tools


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


def format_prompt_components_with_tools(
    ai_settings: dict, contact_settings: dict
) -> Tuple[str]:
    """Format prompt components for agent."""
    ai_prefix, human_prefix, prefix, suffix = format_prompt_components_without_tools(
        ai_settings, contact_settings
    )
    intro_to_tools = INTRO_TO_TOOLS.format(ai_prefix=ai_prefix)

    prefix = "\n".join([prefix, intro_to_tools])
    prefix = prefix.replace("\t", "").replace("    ", "")
    format_instructions = FORMAT_INSTRUCTIONS.format(
        ai_prefix=ai_prefix, human_prefix=human_prefix
    )
    suffix = "\n".join([CONVERSATION_HISTORY, SUFFIX.format(human_prefix=human_prefix)])

    return ai_prefix, human_prefix, prefix, suffix, format_instructions


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
