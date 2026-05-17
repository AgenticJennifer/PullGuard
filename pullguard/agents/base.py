from __future__ import annotations
from abc import ABC, abstractmethod
import google.generativeai as genai
from pullguard.config import PullGuardConfig


class BaseAgent(ABC):
    def __init__(self, config: PullGuardConfig):
        self.config = config
        api_key = config.llm.api_key
        if api_key:
            genai.configure(api_key=api_key)

    def _build_model(self):
        return genai.GenerativeModel(
            self.config.llm.model,
            generation_config={"temperature": self.config.llm.temperature},
        )

    @abstractmethod
    async def run(self, **kwargs) -> object:
        ...
