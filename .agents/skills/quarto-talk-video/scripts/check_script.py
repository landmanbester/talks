#!/usr/bin/env python3
"""Check a narration script's length against the submission spec.

Reads `script/narration.md`, which has one `## slide-NN — title (NNs)` heading
per frame followed by the prose to read. Reports, per frame, the budget you
wrote down against the time the words will actually take, and totals both
against the spec.

Speaking rate defaults to 140 wpm, which is right for technical material with
equations -- noticeably slower than conversational speech. A block whose text
overruns its own budget is not necessarily wrong; a *total* that overruns
max_duration_s is a rejected submission.

Usage:
    check_script.py _video/<slug>/script/narration.md [_video/<slug>/spec.json]
    check_script.py ... --wpm 130
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HEADING = re.compile(r"^##\s+(slide-\d+)\s*(?:[—-]\s*(.*?))?\s*\((\d+)s\)\s*$")


def mmss(seconds: float) -> str:
    return f"{int(seconds // 60)}:{seconds % 60:04.1f}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script", type=Path)
    ap.add_argument("spec", type=Path, nargs="?")
    ap.add_argument("--wpm", type=float, default=140.0)
    ap.add_argument("--frames", type=Path,
                    help="frames.json, to check every frame has a block")
    args = ap.parse_args()

    if not args.script.is_file():
        sys.exit(f"error: no such file: {args.script}")

    blocks: list[tuple[str, str, int, list[str]]] = []
    current = None
    for line in args.script.read_text(encoding="utf-8").splitlines():
        m = HEADING.match(line)
        if m:
            current = (m.group(1), (m.group(2) or "").strip(), int(m.group(3)), [])
            blocks.append(current)
        elif current is not None and line.strip() and not line.startswith("#"):
            current[3].append(line.strip())

    if not blocks:
        sys.exit("error: no '## slide-NN — title (NNs)' headings found")

    budget_total = spoken_total = 0.0
    over = []
    for name, title, budget, lines in blocks:
        words = len(" ".join(lines).split())
        spoken = words / args.wpm * 60
        budget_total += budget
        spoken_total += spoken
        flag = ""
        if spoken > budget * 1.25 and spoken - budget > 3:
            flag = "  <-- text overruns its budget"
            over.append(name)
        elif not words:
            flag = "  <-- NO TEXT"
            over.append(name)
        print(f"  {name}  budget {budget:>3}s   spoken ~{spoken:5.1f}s "
              f"({words:>3} words){flag}   {title[:38]}")

    print(f"\n  {len(blocks)} blocks")
    print(f"  budgeted   {mmss(budget_total)}")
    print(f"  spoken@{args.wpm:.0f}wpm  {mmss(spoken_total)}")

    if args.frames and args.frames.is_file():
        frames = [f["frame"].removesuffix(".png")
                  for f in json.loads(args.frames.read_text())]
        named = {b[0] for b in blocks}
        missing = [f for f in frames if f not in named]
        extra = [n for n in named if n not in frames]
        if missing:
            print(f"\n  MISSING a block: {', '.join(missing)}")
        if extra:
            print(f"  block with no frame: {', '.join(extra)}")
        if missing or extra:
            return 1
        print(f"  every one of {len(frames)} frames has a block")

    if args.spec and args.spec.is_file():
        spec = json.loads(args.spec.read_text())
        limit = spec["max_duration_s"]
        target = spec.get("target_duration_s", limit * 0.9)
        print(f"\n  limit  {mmss(limit)}   target {mmss(target)}")
        # Judge on spoken time: the budgets are an intention, the words are what
        # will actually be read.
        if spoken_total > limit:
            print(f"  OVER THE LIMIT by {mmss(spoken_total - limit)} -- cut before recording.")
            return 1
        if spoken_total > target:
            print(f"  Over target by {mmss(spoken_total - target)}, still inside the limit. "
                  "Thin it now; re-records only ever add time.")
        else:
            print(f"  {mmss(target - spoken_total)} of headroom against target.")

    if over:
        print(f"\n  {len(over)} block(s) whose text does not match the budget written for them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
