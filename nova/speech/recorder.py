from __future__ import annotations

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000
MIN_SECONDS = 0.3
SILENCE_PEAK = 0.01


class Recorder:
    """Records from the default microphone until the user presses Enter."""

    def record(self) -> np.ndarray | None:
        chunks: list[np.ndarray] = []

        def on_audio(indata, frames, time_info, status):
            chunks.append(indata.copy())

        with sd.InputStream(
            samplerate=SAMPLE_RATE, channels=1, dtype="float32", callback=on_audio
        ):
            input()  # blocks until Enter; the mic stays open meanwhile

        if not chunks:
            return None
        audio = np.concatenate(chunks).reshape(-1)
        if audio.size < SAMPLE_RATE * MIN_SECONDS:
            print("  Too short, nothing recorded.")
            return None
        if float(np.max(np.abs(audio))) < SILENCE_PEAK:
            print("  No sound picked up. Check your microphone.")
            return None
        return audio