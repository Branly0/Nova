from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator

Message = dict[str, str]


class ChatProvider(ABC):
    """Anything that can turn a message history into a streamed reply."""

    # Optional: providers that can measure confidence set this when stream() finishes.
    last_confidence = None

    def load(self) -> None:
        """Optional warm-up (e.g. nova is up and ready)."""

    @abstractmethod
    def stream(self, messages: list[Message]) -> Iterator[str]:
        """Yield the reply piece by piece."""