from __future__ import annotations

from typing import Iterator

from ..config import Settings
from ..confidence import summarize
from .base import ChatProvider, Message


def _extract_logprobs(lp) -> list[float]:
    """Pull the per-token log-probabilities out of one streamed chunk."""
    if not lp:
        return []
    if lp.get("content"):  # chat-style layout
        return [t["logprob"] for t in lp["content"] if t.get("logprob") is not None]
    if lp.get("token_logprobs"):  # completion-style layout
        return [x for x in lp["token_logprobs"] if x is not None]
    return []


class _ThinkStripper:
    """Removes <think>...</think> blocks from a stream, even if a tag is split across chunks."""

    OPEN, CLOSE = "<think>", "</think>"

    def __init__(self) -> None:
        self.buf = ""
        self.inside = False

    def feed(self, piece: str) -> str:
        self.buf += piece
        out: list[str] = []
        while True:
            tag = self.CLOSE if self.inside else self.OPEN
            i = self.buf.find(tag)
            if i != -1:
                if not self.inside:
                    out.append(self.buf[:i])
                self.buf = self.buf[i + len(tag):]
                self.inside = not self.inside
                continue
            # Hold back the end of the buffer if it could be the start of a tag.
            keep = 0
            for n in range(min(len(tag) - 1, len(self.buf)), 0, -1):
                if tag.startswith(self.buf[-n:]):
                    keep = n
                    break
            if not self.inside:
                out.append(self.buf[: len(self.buf) - keep])
            self.buf = self.buf[len(self.buf) - keep:]
            break
        return "".join(out)

    def flush(self) -> str:
        rest = "" if self.inside else self.buf
        self.buf = ""
        return rest


class LocalProvider(ChatProvider):
    def __init__(self, settings: Settings):
        self.s = settings
        self._llm = None
        self.last_confidence = None

    def load(self) -> None:
        if self._llm is None:
            from llama_cpp import Llama  # imported here so other providers don't need it

            self._llm = Llama(
                model_path=str(self.s.model_path),
                n_ctx=self.s.n_ctx,
                n_threads=self.s.n_threads,
                n_gpu_layers=0,
                logits_all=self.s.measure_confidence,
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

    def _prepare(self, messages: list[Message]) -> list[Message]:
        """Copy the history, adding the no-think switch to the system message if needed."""
        msgs = [dict(m) for m in messages]
        if not self.s.thinking and msgs and msgs[0]["role"] == "system":
            msgs[0]["content"] += "\n/no_think"
        return msgs

    def stream(self, messages: list[Message]) -> Iterator[str]:
        self.load()
        measure = self.s.measure_confidence
        self.last_confidence = None
        logprobs: list[float] = []
        stripper = None if self.s.thinking else _ThinkStripper()
        first = True

        # The library only returns logprobs if top_logprobs is also given (as far as I know).
        extra = {"logprobs": True, "top_logprobs": 1} if measure else {}

        for chunk in self._llm.create_chat_completion(
            messages=self._fit(self._prepare(messages)),
            temperature=self.s.temperature,
            max_tokens=self.s.max_tokens,
            stream=True,
            **extra,
        ):
            choice = chunk["choices"][0]
            piece = choice["delta"].get("content")
            if not piece:
                continue
            if stripper:
                piece = stripper.feed(piece)
                if first:
                    piece = piece.lstrip()  # drop the blank lines left after </think>
                if not piece:
                    continue
            first = False
            if measure:
                # Measured only for text we actually show, so hidden <think> tokens don't count.
                logprobs.extend(_extract_logprobs(choice.get("logprobs")))
            yield piece

        if stripper:
            tail = stripper.flush()
            if first:
                tail = tail.lstrip()
            if tail:
                yield tail

        if measure:
            self.last_confidence = summarize(logprobs)