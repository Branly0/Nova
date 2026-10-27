from __future__ import annotations

import math
from dataclasses import dataclass

SHAKY_BELOW = 0.5  # a token the model gave less than 50% probability counts as "shaky"


@dataclass
class Confidence:
    tokens: int       # how many tokens were measured
    avg_prob: float   # typical probability of the tokens it chose
    min_prob: float   # probability of its least likely token
    shaky: float      # share of tokens below SHAKY_BELOW

    def __str__(self) -> str:
        if self.tokens == 0:
            return "no data (no logprobs came back from llama-cpp-python)"
        return (
            f"avg {self.avg_prob:.2f}, min {self.min_prob:.2f}, "
            f"shaky {self.shaky:.0%} of {self.tokens} tokens"
        )


def summarize(logprobs: list[float]) -> Confidence:
    """Turn per-token log-probabilities into three simple numbers."""
    if not logprobs:
        return Confidence(0, 0.0, 0.0, 0.0)
    n = len(logprobs)
    avg = math.exp(sum(logprobs) / n)   # geometric mean of the probabilities
    lowest = math.exp(min(logprobs))
    shaky = sum(1 for lp in logprobs if math.exp(lp) < SHAKY_BELOW) / n
    return Confidence(n, avg, lowest, shaky)