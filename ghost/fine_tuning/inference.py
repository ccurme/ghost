import os
from typing import Any, List, Mapping, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
import openai

from fine_tuning.sampling_utils import STOP_SEQUENCE


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
