from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class SpeechToText(ABC):
    """Turns mono 16 kHz float32 audio into text."""

    @property
    def is_loaded(self) -> bool:
        return True

    def load(self) -> None:
        """Optional warm-up (e.g. load a model into memory)."""

    @abstractmethod
    def transcribe(self, audio: np.ndarray) -> str:
        """Return the spoken text, or an empty string if nothing was said."""