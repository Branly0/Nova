from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Settings:
    provider: str
    model_path: Path
    n_ctx: int
    n_threads: int
    temperature: float
    max_tokens: int
    system_prompt: str


def _find_model(models_dir: Path) -> Path:
    found = sorted(models_dir.rglob("*.gguf"))
    if len(found) == 1:
        return found[0]
    if not found:
        raise FileNotFoundError(f"No .gguf file found in {models_dir}")
    names = "\n  ".join(str(p.relative_to(ROOT)) for p in found)
    raise FileNotFoundError(
        "Several .gguf files found. Set model_path in config.json to one of:\n  " + names
    )


def load_settings(path: Path = ROOT / "config.json") -> Settings:
    raw = json.loads(path.read_text(encoding="utf-8"))
    model = raw.get("model_path")
    model_path = (ROOT / model) if model else _find_model(ROOT / "models")
    threads = raw.get("n_threads") or max(1, (os.cpu_count() or 2) // 2)
    return Settings(
        provider=raw.get("provider", "local"),
        model_path=model_path,
        n_ctx=raw.get("n_ctx", 4096),
        n_threads=threads,
        temperature=raw.get("temperature", 0.7),
        max_tokens=raw.get("max_tokens", 512),
        system_prompt=raw.get("system_prompt", "You are a helpful assistant."),
    )