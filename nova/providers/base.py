from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator

Message = dict[str, str]


class ChatProvider(ABC):
    """Anything that can turn a message history into a streamed reply."""

    def load(self) -> None:
        """Optional warm-up (e.g. load a model into memory)."""

    @abstractmethod
    def stream(self, messages: list[Message]) -> Iterator[str]:
        """Yield the reply piece by piece."""