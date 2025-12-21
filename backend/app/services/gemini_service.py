from typing import Any, Optional
import asyncio
import google.generativeai as genai

from ..core.settings import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class GeminiService:
    def __init__(self, *, api_key: Optional[str] = None):
        key = api_key or settings.GEMINI_API_KEY
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel('gemini-pro')

    async def generate(self, *, model: str, temperature: float, max_tokens: int, prompt: str) -> tuple[str, dict[str, Any]]:
        """
        Generate text using Google Gemini API.
        Note: Gemini SDK is synchronous, so we run it in a thread pool.
        """
        try:
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            # Combine system message and user prompt
            full_prompt = f"You are an Upwork proposal assistant.\n\n{prompt}"
            
            # Run synchronous Gemini call in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    full_prompt,
                    generation_config=generation_config,
                )
            )
            
            text = response.text or ""
            
            # Extract usage info if available
            usage = {}
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'completion_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0),
                }
            
            # Get candidate finish reason
            finish_reason = "unknown"
            if response.candidates and len(response.candidates) > 0:
                finish_reason = str(response.candidates[0].finish_reason)
            
            meta = {
                "id": finish_reason,
                "model": "gemini-pro",
                "usage": usage,
            }
            
            return text, meta
        except Exception as e:
            logger.error(f"Gemini API error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to generate with Gemini: {str(e)}")

