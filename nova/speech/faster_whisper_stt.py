from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import numpy as np

from ..config import STTSettings
from .base import SpeechToText


def _add_cuda_dll_dirs() -> None:
    """Make the pip-installed CUDA libraries (cuBLAS, cuDNN) findable on Windows."""
    if sys.platform != "win32":
        return
    for name in ("nvidia.cublas", "nvidia.cudnn"):
        try:
            spec = importlib.util.find_spec(name)
        except ModuleNotFoundError:
            continue
        if not spec or not spec.submodule_search_locations:
            continue
        for location in spec.submodule_search_locations:
            bin_dir = Path(location) / "bin"
            if bin_dir.is_dir():
                os.add_dll_directory(str(bin_dir))
                os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ.get("PATH", "")


class FasterWhisperSTT(SpeechToText):
    def __init__(self, cfg: STTSettings):
        self.cfg = cfg
        self._model = None

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def _build(self, device: str, compute_type: str):
        from faster_whisper import WhisperModel

        model = WhisperModel(self.cfg.model, device=device, compute_type=compute_type)
        # Warm-up on one second of silence. Missing GPU libraries often only
        # fail at the first real run, so we want that failure here, not mid-chat.
        segments, _ = model.transcribe(np.zeros(16000, dtype=np.float32))
        list(segments)
        return model

    def load(self) -> None:
        if self._model is not None:
            return
        if self.cfg.device == "cuda":
            _add_cuda_dll_dirs()
        try:
            self._model = self._build(self.cfg.device, self.cfg.compute_type)
        except Exception as exc:
            if self.cfg.device == "cpu":
                raise
            print(f"  [stt] GPU start failed ({exc}). Falling back to CPU.")
            self._model = self._build("cpu", "int8")

    def transcribe(self, audio: np.ndarray) -> str:
        self.load()
        segments, _ = self._model.transcribe(
            audio,
            language=self.cfg.language,
            beam_size=1,
            vad_filter=True,
            condition_on_previous_text=False,
        )
        return " ".join(s.text.strip() for s in segments).strip()