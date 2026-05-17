from __future__ import annotations
from abc import ABC, abstractmethod
from pullguard.config import PullGuardConfig
from pullguard.llm import build_client, LLMClient


class BaseAgent(ABC):
    def __init__(self, config: PullGuardConfig):
        self.config = config
        self.client = build_client(config.llm)

    def _build_model(self, temperature: float | None = None):
        return self.client

    @abstractmethod
    async def run(self, **kwargs) -> object: ...
