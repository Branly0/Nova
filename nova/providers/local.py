from __future__ import annotations

from typing import Iterator

from ..config import Settings
from .base import ChatProvider, Message


class LocalProvider(ChatProvider):
    def __init__(self, settings: Settings):
        self.s = settings
        self._llm = None

    def load(self) -> None:
        if self._llm is None:
            from llama_cpp import Llama  # imported here so other providers don't need it

            self._llm = Llama(
                model_path=str(self.s.model_path),
                n_ctx=self.s.n_ctx,
                n_threads=self.s.n_threads,
                n_gpu_layers=0,
                verbose=False,
            )

    def _count(self, messages: list[Message]) -> int:
        # +8 per message is a rough allowance for the chat-template tokens
        return sum(
            len(self._llm.tokenize(m["content"].encode("utf-8"), add_bos=False)) + 8
            for m in messages
        )

    def _fit(self, messages: list[Message]) -> list[Message]:
        """Drop the oldest user/assistant pair until the history fits the context."""
        budget = self.s.n_ctx - self.s.max_tokens
        msgs = list(messages)
        while len(msgs) > 2 and self._count(msgs) > budget:
            del msgs[1:3]
        return msgs

    def stream(self, messages: list[Message]) -> Iterator[str]:
        self.load()
        for chunk in self._llm.create_chat_completion(
            messages=self._fit(messages),
            temperature=self.s.temperature,
            max_tokens=self.s.max_tokens,
            stream=True,
        ):
            piece = chunk["choices"][0]["delta"].get("content")
            if piece:
                yield piece