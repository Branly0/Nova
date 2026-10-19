from __future__ import annotations

import datetime as dt
import difflib
import re
import subprocess

import psutil


def normalize(text: str) -> str:
    text = text.lower().replace("'", "").replace("\u2019", "")
    text = re.sub(r"[^\w ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def is_phrase(text: str, phrases: list[str], threshold: float = 0.8, max_words: int = 6) -> bool:
    """True if a short utterance matches (or nearly matches) one of the phrases."""
    t = normalize(text)
    if not t or len(t.split()) > max_words:
        return False
    return any(
        p in t or difflib.SequenceMatcher(None, t, p).ratio() >= threshold for p in phrases
    )


def _time() -> str:
    return "It is " + dt.datetime.now().strftime("%H:%M") + "."


def _date() -> str:
    return "Today is " + dt.datetime.now().strftime("%A, %d %B %Y") + "."


def _status() -> str:
    mem = psutil.virtual_memory()
    parts = [
        f"CPU {psutil.cpu_percent(interval=0.5):.0f}%",
        f"RAM {mem.percent:.0f}% used ({mem.used / 1e9:.1f} of {mem.total / 1e9:.1f} GB)",
    ]
    battery = psutil.sensors_battery()
    if battery:
        parts.append(
            f"battery {battery.percent:.0f}%" + (" (charging)" if battery.power_plugged else "")
        )
    return "System status: " + ", ".join(parts) + "."


class CommandRouter:
    """Fast-path commands that run in plain code, without the language model."""

    def __init__(self, apps: dict[str, str]):
        self.apps = {normalize(name): exe for name, exe in apps.items()}

    def try_run(self, text: str) -> str | None:
        t = normalize(text)
        if re.search(r"\b(what time is it|whats the time|what is the time|current time)\b", t):
            return _time()
        if re.search(r"\b(whats the date|what is the date|todays date|what day is it)\b", t):
            return _date()
        if re.search(r"\b(system status|pc status|computer status|battery status)\b", t):
            return _status()
        match = re.fullmatch(r"(?:open|launch|start) (?:the )?(.+)", t)
        if match and len(match.group(1).split()) <= 3:
            return self._open(match.group(1))
        return None

    def _open(self, app: str) -> str:
        exe = self.apps.get(app)
        if exe is None:
            allowed = ", ".join(sorted(self.apps)) or "none configured"
            return f"I'm not set up to open '{app}'. Allowed apps: {allowed}."
        try:
            subprocess.Popen([exe])  # no shell, and only executables from the config
        except OSError as exc:
            return f"Couldn't open {app}: {exc}"
        return f"Opening {app}."