from __future__ import annotations

import re

from .commands import normalize

# Groups are checked in this order, and the first group with a match wins.
# Order matters: "what is the latest python version" is time-sensitive, not code.

TIME_SENSITIVE = [
    r"\b(latest|newest|current|currently|recent|recently|right now|today|tonight|tomorrow|yesterday)\b",
    r"\b(this (week|month|year)|last (week|month|year)|as of)\b",
    r"\b(news|weather|forecast|score|price|prices|stock|exchange rate|release date)\b",
    r"\bwho is (the )?(new )?(president|prime minister|ceo|minister|governor|mayor)\b",
]

CODE = [
    r"\b(python|javascript|typescript|bash|sql|html|css|regex)\b",
    r"\b(function|class|variable|bug|traceback|compile|stack trace)\b",
    r"\b(write|fix|debug|refactor) (a |the |this |my )?(code|script|program|function)\b",
]

FACT = [
    r"^(who|when|where|which|how many|how much|how old|how long|how far|how tall)\b",
    r"^what(s| is| are| was| were) (the|a|an)\b",
    r"\b(capital of|population of|founded|invented|discovered|born in|died in)\b",
    r"\b(is it true|true or false|fact check)\b",
]

ORDER = (("time_sensitive", TIME_SENSITIVE), ("code", CODE), ("fact", FACT))


def classify(text: str) -> str:
    """Return 'time_sensitive', 'code', 'fact' or 'chat' for a user message."""
    t = normalize(text)
    for label, patterns in ORDER:
        if any(re.search(p, t) for p in patterns):
            return label
    return "chat"