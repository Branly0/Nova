from __future__ import annotations

import sys
import time

from .config import load_settings
from .providers import create_provider


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    settings = load_settings()
    provider = create_provider(settings)

    print("Loading model...", flush=True)
    t0 = time.time()
    provider.load()
    print(f"Ready in {time.time() - t0:.1f}s. Commands: /reset, /exit\n")

    history = [{"role": "system", "content": settings.system_prompt}]

    while True:
        try:
            text = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text == "/exit":
            break
        if text == "/reset":
            history = history[:1]
            print("History cleared.\n")
            continue

        history.append({"role": "user", "content": text})
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
            continue

        elapsed = max(time.time() - start, 1e-6)
        print(f"\n({len(reply)} tokens, {len(reply) / elapsed:.1f} tok/s)\n")
        history.append({"role": "assistant", "content": "".join(reply)})


if __name__ == "__main__":
    main()