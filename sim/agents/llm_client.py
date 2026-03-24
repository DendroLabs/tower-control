"""Thin wrapper around Claude API for agent decision-making.

Swappable for local models later. All agent-specific prompt logic
lives in the agent modules, not here.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    model: str
    input_tokens: int
    output_tokens: int


class LLMClient:
    """Claude API client for agent decision-making."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client = None

    def _get_client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic()
        return self._client

    def complete(self, system: str, user: str) -> LLMResponse:
        """Single-turn completion. Returns structured response."""
        client = self._get_client()
        response = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

    def complete_json(self, system: str, user: str) -> dict:
        """Completion that parses JSON from the response."""
        resp = self.complete(system, user)
        # Extract JSON from response (may be wrapped in markdown code block)
        text = resp.content.strip()
        if text.startswith("```"):
            # Strip markdown code fences
            lines = text.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            text = "\n".join(lines).strip()
        return json.loads(text)
