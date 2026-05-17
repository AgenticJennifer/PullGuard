from __future__ import annotations
from typing import Protocol


class LLMClient(Protocol):
    async def complete(self, prompt: str, system: str = "", temperature: float = 0.3) -> str: ...
