import os
from typing import Any, List, Mapping, Optional

from langchain import LLMChain, PromptTemplate
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.memory import ConversationBufferMemory
import openai

from fine_tuning.sampling_utils import STOP_SEQUENCE
from utils import format_prompt_components_without_tools


openai.api_key = os.getenv("OPENAI_API_KEY")


class FineTunedLLM(LLM):

    model_name: str
        
    @property
    def _llm_type(self) -> str:
        return "Fine tuned LLM."
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        if stop is None:
            stop = [STOP_SEQUENCE]

        result = openai.Completion.create(
            model=self.model_name, prompt=prompt, max_tokens=50, temperature=0, stop=stop
        )
        if not result.choices:
            raise AssertionError("Invalid result from OpenAI API request.")
        response = result.choices[0]["text"].strip()
        return response

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"model_name": self.model_name}


def initialize_chain(ai_settings: dict, contact_settings: dict) -> LLMChain:
    """Initialize LLMChain with memory. using FineTunedLLM."""
    llm = FineTunedLLM(model_name=ai_settings["fine_tuned_model_name"])
    ai_prefix, human_prefix, prefix, suffix = format_prompt_components_without_tools(
        ai_settings, contact_settings, fine_tune=True,
    )
    template = "\n".join([prefix, suffix, f"{human_prefix}: {{human_input}}", "", f"{ai_prefix}:"])
    prompt = PromptTemplate(
        input_variables=["chat_history", "human_input"],
        template=template
    )
    memory = ConversationBufferMemory(memory_key="chat_history", human_prefix=human_prefix, ai_prefix=ai_prefix)

    return LLMChain(llm=llm, prompt=prompt, memory=memory)
