from __future__ import annotations
import google.generativeai as genai


class GeminiClient:
    def __init__(self, model: str = "gemini-2.0-flash", api_key: str | None = None, temperature: float = 0.3):
        self.model_name = model
        self.temperature = temperature
        if api_key:
            genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(
            self.model_name,
            generation_config={"temperature": self.temperature},
        )

    async def complete(self, prompt: str, system: str = "", temperature: float | None = None) -> str:
        temp = temperature if temperature is not None else self.temperature
        model = self._model
        if system:
            model = genai.GenerativeModel(
                self.model_name,
                generation_config={"temperature": temp},
                system_instruction=system,
            )
        response = await model.generate_content_async(prompt)
        return response.text
