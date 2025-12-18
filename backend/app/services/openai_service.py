from typing import Any, Optional

from openai import AsyncOpenAI

from ..core.settings import settings


class OpenAIService:
    def __init__(self, *, api_key: Optional[str] = None):
        key = api_key or settings.OPENAI_API_KEY
        if not key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        self.client = AsyncOpenAI(api_key=key)

    async def generate(self, *, model: str, temperature: float, max_tokens: int, prompt: str) -> tuple[str, dict[str, Any]]:
        """
        Minimal ChatCompletions wrapper.
        """
        resp = await self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an Upwork proposal assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = resp.choices[0].message.content or ""
        usage = (resp.usage.model_dump() if resp.usage else {})  # type: ignore[attr-defined]
        meta = {"id": resp.id, "model": resp.model, "usage": usage}
        return text, meta


