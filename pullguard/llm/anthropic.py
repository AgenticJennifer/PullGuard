from __future__ import annotations
import anthropic


class AnthropicClient:
    def __init__(self, model: str = "claude-sonnet-4-20250514", api_key: str | None = None, temperature: float = 0.3):
        self.model_name = model
        self.temperature = temperature
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def complete(self, prompt: str, system: str = "", temperature: float | None = None) -> str:
        kwargs = {
            "model": self.model_name,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature if temperature is not None else self.temperature,
        }
        if system:
            kwargs["system"] = system
        response = await self._client.messages.create(**kwargs)
        return response.content[0].text
