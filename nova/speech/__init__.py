from ..config import STTSettings
from .base import SpeechToText


def create_stt(cfg: STTSettings) -> SpeechToText:
    if cfg.engine == "faster-whisper":
        from .faster_whisper_stt import FasterWhisperSTT

        return FasterWhisperSTT(cfg)
    raise ValueError(f"Unknown STT engine: {cfg.engine}")