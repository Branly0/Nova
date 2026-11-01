from __future__ import annotations

import argparse
import csv
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

from .config import ROOT, load_settings, match_model
from .providers import create_provider

CAL_DIR = ROOT / "calibration"

# Phrases that suggest the model declined to answer or rejected the question.
ABSTAIN_HINTS = (
    "i don't", "i do not", "not sure", "no record", "not aware", "cannot", "can't",
    "unable", "no information", "fictional", "doesn't exist", "does not exist",
    "no one", "has not", "hasn't", "didn't", "did not",
    "not widely", "does not appear", "not documented", "not a known", "not a recognized",
    "not recognized", "no such", "there is no", "there's no",
)

THRESHOLDS = {
    "min": (0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60),
    "avg": (0.50, 0.60, 0.70, 0.80, 0.90, 0.95),
}


def load_questions(path: Path) -> list[dict]:
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2 or parts[0] not in ("answerable", "unanswerable"):
            raise ValueError(
                f"{path.name} line {n}: use 'answerable | question | expected' "
                "or 'unanswerable | question'"
            )
        rows.append(
            {"group": parts[0], "question": parts[1], "expected": parts[2] if len(parts) > 2 else ""}
        )
    return rows


def judge(row: dict, answer: str) -> str:
    """Rough, keyword-based verdict: right / wrong / abstained / invented."""
    a = answer.lower().replace("\u2019", "'")
    if row["group"] == "answerable":
        options = [o.strip().lower() for o in row["expected"].split("/") if o.strip()]
        return "right" if any(o in a for o in options) else "wrong"
    return "abstained" if any(h in a for h in ABSTAIN_HINTS) else "invented"


def ask(provider, settings, question: str):
    messages = [
        {"role": "system", "content": settings.system_prompt},
        {"role": "user", "content": question},
    ]
    start = time.time()
    answer = "".join(provider.stream(messages)).strip()
    return answer, provider.last_confidence, time.time() - start


def report(results: list[dict]) -> None:
    print("\nMedian measures by outcome")
    print(f"  {'outcome':<10}{'n':>3}{'min':>7}{'avg':>7}{'shaky':>7}")
    for outcome in ("right", "wrong", "abstained", "invented"):
        rs = [r for r in results if r["outcome"] == outcome]
        if rs:
            med = lambda k: statistics.median(r[k] for r in rs)
            print(f"  {outcome:<10}{len(rs):>3}{med('min'):>7.2f}{med('avg'):>7.2f}{med('shaky'):>7.0%}")

    good = [r for r in results if r["outcome"] == "right"]
    bad = [r for r in results if r["outcome"] in ("wrong", "invented")]
    if not good or not bad:
        print("\nNeed both right answers and bad answers to compare thresholds.")
        return

    for key, cuts in THRESHOLDS.items():
        print(f"\nFlag as doubtful when '{key}' is below the threshold:")
        print(f"  {'threshold':>9}  {'bad answers caught':>19}  {'right answers flagged':>22}")
        for t in cuts:
            caught = sum(r[key] < t for r in bad)
            flagged = sum(r[key] < t for r in good)
            print(f"  {t:>9.2f}  {f'{caught}/{len(bad)}':>19}  {f'{flagged}/{len(good)}':>22}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="nova.calibrate")
    parser.add_argument("--model", help="part of a model file name")
    parser.add_argument("--questions", default=str(CAL_DIR / "questions.txt"))
    parser.add_argument("--temp", type=float, help="override the temperature")
    args = parser.parse_args()

    try:
        rows = load_questions(Path(args.questions))
        override = match_model(args.model) if args.model else None
    except (ValueError, OSError) as exc:
        sys.exit(str(exc))

    settings = load_settings(model_override=override)
    settings.measure_confidence = True                    # always on for calibration
    settings.max_tokens = min(settings.max_tokens, 120)   # short factual answers only
    if args.temp is not None:
        settings.temperature = args.temp

    print(
        f"Model: {settings.model_path.name} | temperature {settings.temperature} "
        f"| thinking {'on' if settings.thinking else 'off'}"
    )
    provider = create_provider(settings)
    print("Loading model...", flush=True)
    provider.load()

    results: list[dict] = []
    try:
        for i, row in enumerate(rows, 1):
            answer, conf, seconds = ask(provider, settings, row["question"])
            if conf is None or conf.tokens == 0:
                sys.exit("No confidence data came back. Check that logprobs are returned.")
            outcome = judge(row, answer)
            results.append(
                {
                    **row,
                    "outcome": outcome,
                    "min": conf.min_prob,
                    "avg": conf.avg_prob,
                    "shaky": conf.shaky,
                    "tokens": conf.tokens,
                    "seconds": round(seconds, 1),
                    "answer": answer,
                }
            )
            print(
                f"[{i}/{len(rows)}] {outcome:<9} min {conf.min_prob:.2f} "
                f"avg {conf.avg_prob:.2f} | {row['question'][:55]}"
            )
    except KeyboardInterrupt:
        print("\nStopped early; reporting what we have.")

    if not results:
        return

    out_dir = CAL_DIR / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = out_dir / f"{settings.model_path.stem}_t{settings.temperature}_{stamp}.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)

    report(results)
    print(f"\nFull answers saved to {out}")


if __name__ == "__main__":
    main()