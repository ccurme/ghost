from textwrap import dedent

from langchain import OpenAI
from langchain.agents.agent import AgentExecutor

from utils import format_prompt_components_without_tools


def get_unsolicited_message_prompt(ai_prefix: str, human_prefix: str) -> str:
    """Get prompt for unsolicited message."""
    inspirational_thought = f"""
    *{ai_prefix} then drew on their past experiences and relationships with {human_prefix} and continued the conversation*

    {ai_prefix}:
    """

    return dedent(inspirational_thought)


def generate_unsolicited_message(
    prompt: str, agent: AgentExecutor, ai_settings: dict, contact_settings: dict, temperature: int = 0,
) -> str:
    """Generate AI message without message from user."""

    _, _, prefix, suffix = format_prompt_components_without_tools(
        ai_settings, contact_settings
    )

    prompt = "\n".join([prefix, suffix, prompt]).format(
        chat_history=agent.memory.buffer
    )
    llm = OpenAI(temperature=temperature)
    message = llm(prompt)

    agent.memory.chat_memory.add_ai_message(message)

    return message
