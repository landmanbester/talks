#!/usr/bin/env python3
"""Remove the keyboard transient at the ends of narration takes.

Recording with a keypress to start and stop puts the key click *inside* the
take: a 10-30 ms burst at the very end of the file, and occasionally one at the
very start. Silence trimming does not touch it, because a click is loud -- it
is the trim's stopping point, not something the trim removes.

Level cannot distinguish a click from speech here (measured peaks overlap
almost exactly, roughly -22 to -50 dB for both). Two things do:

  duration  -- a key click is 10-30 ms; a spoken syllable is hundreds
  isolation -- the click sits after a clear gap, at the very edge of the file

So this cuts the last run above the noise floor only when it is short, isolated,
and touching the end of the file, and it verifies that what it removed contained
no sustained sound before writing anything. The threshold is taken relative to
each file's own noise floor: a fixed one misses the quieter clicks.

Usage:
    declick_takes.py <indir> <outdir> [--dry-run] [--verbose]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 48000
WIN_S = 0.005            # envelope resolution
FLOOR_PCTL = 20          # percentile of the envelope taken as room tone
THR_OVER_FLOOR = 10      # dB above the floor that counts as "sound"
MERGE_GAP_MS = 30        # fragments closer than this are one burst
MAX_CLICK_MS = 120       # longer than this is speech, not a key
MIN_GAP_MS = 80          # silence that must separate it from the speech
EDGE_TOL_MS = 20         # how close to the file edge the burst must sit
MARGIN_MS = 20           # extra removed before the burst
FADE_MS = 15             # fade applied at the new edge, so the cut is silent


def die(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    sys.exit(f"error: {msg}")


def load(path: Path) -> np.ndarray:
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path),
                        "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                       capture_output=True)
    if p.returncode != 0:
        die(f"could not decode {path}: {p.stderr.decode()[:200]}")
    return np.frombuffer(p.stdout, dtype=np.float32).copy()


def envelope(x: np.ndarray) -> np.ndarray:
    """RMS envelope in dB, one value per WIN_S.

    The trailing partial window is measured too. Dropping it -- the obvious
    `x[:n*w].reshape(...)` -- discards up to WIN_S at the end of the file, which
    is precisely where a stop-key click sits: the click then does not exist as
    far as detection is concerned.
    """
    w = int(WIN_S * SR)
    n = len(x) // w
    out = []
    if n:
        frames = x[:n * w].reshape(n, w).astype(np.float64)
        out.append(np.sqrt(np.mean(frames ** 2, axis=1)))
    rest = x[n * w:]
    if len(rest):
        out.append(np.array([np.sqrt(np.mean(rest.astype(np.float64) ** 2))]))
    if not out:
        return np.array([])
    return 20 * np.log10(np.maximum(np.concatenate(out), 1e-9))


def runs_above(env: np.ndarray, thr: float) -> list[tuple[int, int]]:
    """Contiguous runs above thr, with near-touching runs merged.

    A click is a decaying transient, so its envelope dips below threshold for a
    window or two mid-burst and splits into fragments. Unmerged, the burst then
    looks like several 5 ms events 5 ms apart -- and the isolation test measures
    the gap to its own fragment instead of to the speech, so a real click reads
    as "not isolated" and survives.
    """
    idx = np.where(env > thr)[0]
    if not len(idx):
        return []
    merge = max(1, int(MERGE_GAP_MS / (WIN_S * 1000)))
    out, start, prev = [], idx[0], idx[0]
    for i in idx[1:]:
        if i > prev + merge:
            out.append((start, prev))
            start = i
        prev = i
    out.append((start, prev))
    return out


def find_edge_click(env: np.ndarray, thr: float, at_end: bool) -> tuple[int, int] | None:
    """Return the (start, end) window indices of an edge click, or None."""
    runs = runs_above(env, thr)
    if not runs:
        return None
    per = WIN_S * 1000
    edge_tol = max(1, int(EDGE_TOL_MS / per))

    if at_end:
        a, b = runs[-1]
        if b < len(env) - 1 - edge_tol:          # not touching the end
            return None
        gap = (a - runs[-2][1] - 1) * per if len(runs) > 1 else float("inf")
    else:
        a, b = runs[0]
        if a > edge_tol:                          # not touching the start
            return None
        gap = (runs[1][0] - b - 1) * per if len(runs) > 1 else float("inf")

    if (b - a + 1) * per > MAX_CLICK_MS or gap < MIN_GAP_MS:
        return None
    return a, b


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("indir", type=Path)
    ap.add_argument("outdir", type=Path)
    ap.add_argument("--dry-run", action="store_true", help="report, write nothing")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    files = sorted(args.indir.glob("*.wav"))
    if not files:
        die(f"no .wav files in {args.indir}")
    if not args.dry_run:
        args.outdir.mkdir(parents=True, exist_ok=True)

    per = WIN_S * 1000
    n_head = n_tail = 0
    removed_total = 0.0
    refused: list[str] = []

    for f in files:
        x = load(f)
        env = envelope(x)
        if not len(env):
            refused.append(f"{f.stem}: too short to analyse")
            continue
        floor = float(np.percentile(env, FLOOR_PCTL))
        thr = floor + THR_OVER_FLOOR

        lo, hi = 0, len(x)
        head_ms = tail_ms = 0.0

        tail = find_edge_click(env, thr, at_end=True)
        if tail:
            a, _ = tail
            cut = int((a * WIN_S - MARGIN_MS / 1000) * SR)
            if cut > lo:
                tail_ms = (hi - cut) / SR * 1000
                hi = cut
                n_tail += 1

        head = find_edge_click(env, thr, at_end=False)
        if head:
            _, b = head
            cut = int(((b + 1) * WIN_S + MARGIN_MS / 1000) * SR)
            if cut < hi:
                head_ms = (cut - lo) / SR * 1000
                lo = cut
                n_head += 1

        # Refuse to write if what we are about to drop contains anything
        # sustained. Removing a click must never be able to remove a word.
        for name, seg in (("head", x[:lo]), ("tail", x[hi:])):
            if not len(seg):
                continue
            e = envelope(seg)
            if len(e) and any((b - a + 1) * per > MAX_CLICK_MS
                              for a, b in runs_above(e, thr)):
                refused.append(f"{f.stem}: {name} cut would remove sustained audio — left alone")
                lo, hi = 0, len(x)
                head_ms = tail_ms = 0.0
                if name == "tail":
                    n_tail -= 1
                else:
                    n_head -= 1
                break

        y = x[lo:hi].copy()
        fade = min(int(FADE_MS / 1000 * SR), len(y))
        if fade:
            y[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)
            if head_ms:
                y[:fade] *= np.linspace(0.0, 1.0, fade, dtype=np.float32)

        removed_total += (head_ms + tail_ms) / 1000
        if args.verbose or head_ms or tail_ms:
            print(f"  {f.stem:<10} floor {floor:6.1f} dB   "
                  f"head -{head_ms:5.1f} ms   tail -{tail_ms:6.1f} ms")

        if not args.dry_run:
            p = subprocess.run(
                ["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR),
                 "-ac", "1", "-i", "pipe:0", "-c:a", "pcm_s24le",
                 str(args.outdir / f.name)],
                input=y.astype(np.float32).tobytes(), capture_output=True)
            if p.returncode != 0:
                die(f"could not write {f.name}: {p.stderr.decode()[:200]}")

    print(f"\n  {len(files)} file(s): removed a trailing click from {n_tail}, "
          f"a leading click from {n_head}")
    print(f"  {removed_total:.2f}s removed in total")
    for r in refused:
        print(f"  SKIPPED {r}")
    if args.dry_run:
        print("  (dry run — nothing written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
