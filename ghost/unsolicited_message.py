from textwrap import dedent

from langchain import OpenAI
from langchain.agents.agent import AgentExecutor

from utils import format_prompt_components_without_tools


def generate_unsolicited_message(ai_settings: dict, contact_settings: dict, agent: AgentExecutor) -> str:
    """Generate AI message without message from user."""

    ai_prefix, human_prefix, prefix, suffix = format_prompt_components_without_tools(ai_settings, contact_settings)

    inspirational_thought = f"""
    *{ai_prefix} then drew on their past experiences and relationships with {human_prefix} and continued the conversation*

    {ai_prefix}:
    """
    inspirational_thought = dedent(inspirational_thought)

    prompt = "\n".join([prefix, suffix, inspirational_thought]).format(chat_history=agent.memory.buffer)
    llm = OpenAI(temperature=0)
    message = llm(prompt)

    agent.memory.chat_memory.add_ai_message(message)

    return message
