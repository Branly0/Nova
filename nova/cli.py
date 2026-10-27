from __future__ import annotations

import sys
import time

from .commands import CommandRouter, is_phrase
from .triage import classify
from .config import load_settings
from .providers import create_provider
from .speech import create_stt
from .speech.recorder import Recorder

VOICE_ON = ["casual voice chat", "voice mode"]
VOICE_OFF = ["exit voice chat", "stop voice chat", "text mode"]


def listen(stt, recorder) -> str | None:
    """Record and transcribe once. '' = nothing heard, None = hard error."""
    try:
        if not stt.is_loaded:
            print("  Loading speech model (the first run downloads it)...", flush=True)
            stt.load()
        print("  Listening... press Enter when you finish speaking.", flush=True)
        audio = recorder.record()
        if audio is None:
            return ""
        print("  Transcribing...", end="", flush=True)
        start = time.time()
        text = stt.transcribe(audio)
        print(f" done in {time.time() - start:.1f}s")
        if not text:
            print("  Didn't catch anything.")
        return text
    except Exception as exc:
        print(f"\n  [voice error] {exc}")
        return None


def run_turn(text: str, history: list, provider, router: CommandRouter) -> None:
    history.append({"role": "user", "content": text})

    answer = router.try_run(text)
    if answer is not None:
        print(f"nova> {answer}\n")
        history.append({"role": "assistant", "content": answer})
        return

    print(f"[triage: {classify(text)}]")
    reply: list[str] = []
    print("nova> ", end="", flush=True)
    start = time.time()
    try:
        for piece in provider.stream(history):
            reply.append(piece)
            print(piece, end="", flush=True)
    except KeyboardInterrupt:
        print("\n[stopped]", end="")

    if not reply:
        history.pop()
        print("\n")
        return

    elapsed = max(time.time() - start, 1e-6)
    print(f"\n({len(reply)} tokens, {len(reply) / elapsed:.1f} tok/s)")
    if provider.last_confidence:
        print(f"[confidence: {provider.last_confidence}]")
    print()
    history.append({"role": "assistant", "content": "".join(reply)})


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    settings = load_settings()
    provider = create_provider(settings)
    router = CommandRouter(settings.apps)
    stt = create_stt(settings.stt)
    recorder = Recorder()

    print("Starting Nova...", flush=True)
    provider.load()
    print(f"\nHello, {settings.address_as}. Nova is up and running.")
    print("Try: 'what time is it', 'system status', 'open notepad'")
    print("Commands: /talk (speak once), /voice, /reset, /exit\n")

    history = [{"role": "system", "content": settings.system_prompt}]
    mode = "text"

    while True:
        try:
            if mode == "voice":
                text = listen(stt, recorder)
                if text is None:
                    mode = "text"
                    print("Back to text mode.\n")
                    continue
                if not text:
                    continue
                print(f"you (heard)> {text}")
            else:
                text = input("you> ").strip()
                if not text:
                    continue
                if text == "/talk":
                    text = listen(stt, recorder)
                    if not text:
                        continue
                    print(f"you (heard)> {text}")
        except (EOFError, KeyboardInterrupt):
            print()
            if mode == "voice":
                mode = "text"
                print("Back to text mode.\n")
                continue
            break

        if text == "/exit":
            break
        if text == "/reset":
            history = history[:1]
            print("History cleared.\n")
            continue
        if is_phrase(text, VOICE_OFF):
            mode = "text"
            print("Back to text mode.\n")
            continue
        if text == "/voice" or is_phrase(text, VOICE_ON):
            mode = "voice"
            print("Voice mode on. Say 'exit voice chat' or press Ctrl+C to leave.\n")
            continue

        run_turn(text, history, provider, router)


if __name__ == "__main__":
    main()