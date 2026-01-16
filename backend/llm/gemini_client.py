"""
Shrestha Capital - Unified Gemini Client

All LLM interactions go through this client.
Supports:
- gemini-2.5-pro: Heavy reasoning (analysis, thesis, PM decisions)
- gemini-2.0-flash: Fast tasks (screening, parsing)
- gemini-2.0-flash + Grounding: Web search (prices, news, data)
"""

from google import genai
from google.genai import types
from enum import Enum
from typing import Optional
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import get_settings


class GeminiModel(Enum):
    """Available Gemini models"""
    PRO = "gemini-2.0-flash"  # Using flash for now due to quota; switch to gemini-1.5-pro or gemini-2.5-pro when available
    FLASH = "gemini-2.0-flash"


class GeminiClient:
    """
    Unified Gemini client for Shrestha Capital.

    Usage:
        client = GeminiClient()

        # Heavy reasoning (no web search)
        result = await client.think("Analyze this company's moat...")

        # Fast tasks
        result = await client.quick("Parse this into JSON...")

        # With web search (for current data)
        result = await client.search("What is TSLA stock price today?")
    """

    def __init__(self):
        settings = get_settings()

        # Initialize the client with API key
        self.client = genai.Client(api_key=settings.google_api_key)
        self.settings = settings

    async def think(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: GeminiModel = GeminiModel.PRO,
        temperature: float = 0.7
    ) -> str:
        """
        Generate response WITHOUT web search.
        Use for reasoning, analysis, synthesis tasks.

        Args:
            prompt: The user prompt
            system: Optional system instructions
            model: PRO (default) or FLASH
            temperature: Creativity (0.0-1.0)

        Returns:
            Generated text response
        """
        model_id = model.value

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=self.settings.max_output_tokens,
            system_instruction=system if system else None
        )

        response = await self.client.aio.models.generate_content(
            model=model_id,
            contents=prompt,
            config=config
        )

        return response.text

    async def search(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7
    ) -> dict:
        """
        Generate response WITH Google Search grounding.
        Use for current prices, news, market data.

        Args:
            prompt: The search/query prompt
            system: Optional system instructions
            temperature: Creativity (0.0-1.0)

        Returns:
            Dict with 'text' and 'sources' keys
        """
        # Use Google Search tool for grounding
        google_search_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=self.settings.max_output_tokens,
            system_instruction=system if system else None,
            tools=[google_search_tool]
        )

        response = await self.client.aio.models.generate_content(
            model=GeminiModel.FLASH.value,
            contents=prompt,
            config=config
        )

        # Extract grounding sources from metadata
        sources = []
        if response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                metadata = candidate.grounding_metadata
                if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
                    for chunk in metadata.grounding_chunks:
                        if hasattr(chunk, 'web') and chunk.web:
                            sources.append({
                                "title": chunk.web.title if chunk.web.title else "Unknown",
                                "url": chunk.web.uri if chunk.web.uri else ""
                            })

        return {
            "text": response.text,
            "sources": sources
        }

    async def quick(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.5
    ) -> str:
        """
        Fast response using Flash model.
        Use for simple parsing, classification, quick calculations.

        Args:
            prompt: The prompt
            system: Optional system instructions
            temperature: Lower default for more deterministic output

        Returns:
            Generated text response
        """
        return await self.think(prompt, system, GeminiModel.FLASH, temperature)


# Singleton instance for easy import
_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create the singleton Gemini client"""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client


# Convenience alias
gemini = get_gemini_client
