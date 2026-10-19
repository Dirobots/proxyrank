"""Extracts pairwise outcomes from the RoboArena data dump into a small CSV.

    uv run --with pyyaml python casestudies/roboarena_extract.py /path/to/DataDump_07-17-2026

Download only the metadata first (no videos):
    hf download RoboArena/DataDump_07-17-2026 --repo-type dataset --include "*.yaml" --local-dir <dir>

Evaluator names, emails and free-text feedback are left out.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

import yaml

DATA = Path(__file__).parent / "data"
OUT = DATA / "roboarena_pairs.csv"
EPISODES = DATA / "roboarena_episodes.csv"


def main(root):
    rows, episodes, skipped = [], [], Counter()
    for f in sorted(Path(root, "evaluation_sessions").glob("*/metadata.yaml")):
        meta = yaml.safe_load(f.read_text())
        pol = meta.get("policies") or {}
        pref = str(meta.get("preference", "")).upper()
        for label, p in pol.items():
            if p.get("binary_success") in (0, 1):
                episodes.append({"session": f.parent.name, "policy": p["policy_name"], "success": p["binary_success"]})
        # sessions with more than two policies still record the A-vs-B preference
        if not {"A", "B"} <= set(pol):
            skipped[f"policies={sorted(pol)}"] += 1
            continue
        if pref not in {"A", "B", "TIE"}:
            skipped[f"preference={pref}"] += 1
            continue
        rows.append({
            "session": f.parent.name,
            "location": meta.get("evaluation_location", ""),
            "policy_a": pol["A"]["policy_name"],
            "policy_b": pol["B"]["policy_name"],
            "preference": pref,
            "success_a": pol["A"].get("binary_success", ""),
            "success_b": pol["B"].get("binary_success", ""),
        })
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(EPISODES, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["session", "policy", "success"])
        w.writeheader()
        w.writerows(episodes)
    print(f"{len(rows)} sessions -> {OUT}; {len(episodes)} episodes -> {EPISODES}; skipped {dict(skipped)}")


if __name__ == "__main__":
    main(sys.argv[1])
