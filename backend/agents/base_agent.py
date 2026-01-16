"""
Shrestha Capital - Base Agent Class

All agents inherit from this base class.
Provides common functionality for:
- LLM interaction (think/search)
- JSON parsing
- Error handling with retries
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.gemini_client import get_gemini_client, GeminiModel


class BaseAgent(ABC):
    """
    Base class for all Shrestha Capital agents.

    Subclasses must implement:
    - system_prompt: Agent's personality and instructions
    - _build_prompt(): How to construct the prompt from task + context

    Optional overrides:
    - needs_search: Set to True for agents that need web data
    - model: Change from PRO to FLASH for fast tasks
    """

    def __init__(
        self,
        name: str,
        model: GeminiModel = GeminiModel.PRO,
        temperature: float = 0.7
    ):
        self.name = name
        self.model = model
        self.temperature = temperature
        self.client = get_gemini_client()

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """
        Agent's system instructions.
        Define the agent's role, personality, and output format.
        """
        pass

    @property
    def needs_search(self) -> bool:
        """
        Override to True for agents that need real-time web data.
        (e.g., price data, news, analyst ratings)
        """
        return False

    async def run(self, task: str, context: Optional[dict] = None) -> dict:
        """
        Execute the agent on a task.

        Args:
            task: What the agent should do (e.g., "Analyze TSLA fundamentals")
            context: Additional context (e.g., {"ticker": "TSLA", "data": {...}})

        Returns:
            Parsed JSON response from the agent
        """
        prompt = self._build_prompt(task, context or {})

        if self.needs_search:
            response = await self.client.search(
                prompt,
                system=self.system_prompt,
                temperature=self.temperature
            )
            result = self._parse_json(response["text"])
            result["_sources"] = response["sources"]
            return result
        else:
            response = await self.client.think(
                prompt,
                system=self.system_prompt,
                model=self.model,
                temperature=self.temperature
            )
            return self._parse_json(response)

    @abstractmethod
    def _build_prompt(self, task: str, context: dict) -> str:
        """
        Build the prompt from task and context.

        Args:
            task: The task description
            context: Additional context dict

        Returns:
            The full prompt string to send to the LLM
        """
        pass

    def _parse_json(self, text: str) -> dict:
        """
        Parse JSON from LLM response.
        Handles markdown code blocks and common formatting issues.
        """
        try:
            # Try to extract JSON from markdown code blocks
            clean = text

            # Handle ```json ... ``` blocks
            if "```json" in clean:
                match = re.search(r'```json\s*([\s\S]*?)\s*```', clean)
                if match:
                    clean = match.group(1)
            # Handle ``` ... ``` blocks
            elif "```" in clean:
                match = re.search(r'```\s*([\s\S]*?)\s*```', clean)
                if match:
                    clean = match.group(1)

            # Try to parse
            return json.loads(clean.strip())

        except json.JSONDecodeError:
            # Try to find any JSON object in the text
            try:
                match = re.search(r'\{[\s\S]*\}', text)
                if match:
                    return json.loads(match.group())
            except:
                pass

            # Return raw text if parsing fails
            return {
                "_raw": text,
                "_parse_error": True,
                "_error_message": "Failed to parse JSON from response"
            }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', model={self.model.name})>"
