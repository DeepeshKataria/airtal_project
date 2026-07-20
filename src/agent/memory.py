"""
Lightweight in-process conversation memory for the Airtel B2B AI Sales Assistant.

Stores (role, content) pairs up to `max_turns` full conversation turns (human + AI each).
Intentionally simple so it can be swapped for LangChain memory later without changing callers.

Design decision: a plain deque with a max-length cap.
- No disk persistence (as required for Phase 4).
- maxlen=12 → keeps the last 6 full turns (6 human + 6 AI messages).
  This fits comfortably in the Groq context window while keeping costs low.
"""

from __future__ import annotations

from collections import deque
from typing import Literal

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

# 6 full turns = 12 messages (human + AI per turn)
DEFAULT_MAX_MESSAGES = 12


class ConversationMemory:
    """
    Thin wrapper around a fixed-length deque of LangChain message objects.

    Usage::

        mem = ConversationMemory()
        mem.add_human("Hello")
        mem.add_ai("Hi! How can I help?")
        msgs = mem.messages   # → [HumanMessage("Hello"), AIMessage("Hi! …")]
        mem.clear()
    """

    def __init__(self, max_messages: int = DEFAULT_MAX_MESSAGES):
        self._store: deque[BaseMessage] = deque(maxlen=max_messages)

    def add_human(self, text: str) -> None:
        self._store.append(HumanMessage(content=text))

    def add_ai(self, text: str) -> None:
        self._store.append(AIMessage(content=text))

    @property
    def messages(self) -> list[BaseMessage]:
        return list(self._store)

    def clear(self) -> None:
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)
