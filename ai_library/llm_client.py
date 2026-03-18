# ai_library/llm_client.py
from openai import OpenAI
from ai_library.config import Config


class LLMClient:
    def __init__(self, api_key=None, model=None, temperature=None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        self.temperature = Config.TEMPERATURE if temperature is None else temperature

        if not self.api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable")

        self.client = OpenAI(api_key=self.api_key)

    def ask(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""
