#!/usr/bin/env python3
"""Build an SRT from the narration script and the per-slide audio durations.

The alternative is transcribing the finished MP4 with whisper. Prefer this when
the narration was read from `script/narration.md` more or less as written, which
is the normal case for a per-slide recording: the text is then already exact,
and ASR only introduces errors -- reliably in the domain terms this repo's decks
are full of (MeerKAT, uv-coverage, Stokes, SARA, prox), which are the words a
reader most needs the captions to get right.

What whisper does better is word-level timing inside a slide. Here, cue times
come from each slide's audio duration -- so every cue is correct to its slide
boundary, and within a slide the split is proportional to text length. Drift is
bounded by one slide's length and resets at every boundary.

Use whisper instead if the delivery departed from the script (heavy ad-libbing),
since then the script is no longer a transcript of what was said.

Usage:
    captions_from_script.py <build> [-o out.srt] [--pad 0.2] [--cps 17]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HEADING = re.compile(r"^##\s+(slide-\d+)\s*(?:[—-]\s*(.*?))?\s*\((\d+)s\)\s*$")
MAX_LINE = 42          # characters per caption line, the usual broadcast limit
MAX_LINES = 2
MIN_CUE_S = 1.2
MAX_CUE_S = 6.0


def die(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    sys.exit(f"error: {msg}")


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        die(f"could not read duration of {path}")


def load_blocks(script: Path) -> dict[str, str]:
    blocks: dict[str, str] = {}
    key = None
    for line in script.read_text(encoding="utf-8").splitlines():
        m = HEADING.match(line)
        if m:
            key = m.group(1)
            blocks[key] = ""
        elif key and line.strip() and not line.startswith("#"):
            blocks[key] = (blocks[key] + " " + line.strip()).strip()
    return blocks


def plain(text: str) -> str:
    """Strip the markdown the script is written in. `pfb-imaging` is code in a
    source file and a word out loud; a literal backtick on screen is neither."""
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)   # [label](url) -> label
    text = re.sub(r"`([^`]*)`", r"\1", text)               # `code` -> code
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)         # **bold** -> bold
    text = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", r"\1", text)  # *em* -> em
    text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def sentences(text: str) -> list[str]:
    """Split on sentence enders, keeping the punctuation. Abbreviations like
    'e.g.' would over-split, so require the following char to be a space+capital."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", text)
    return [p.strip() for p in parts if p.strip()]


def fit_lines(text: str) -> list[str] | None:
    """Pack text into at most MAX_LINES lines, ignoring sentence structure.
    Returns None if it will not fit. Used to test a merge: `chunk` always ends a
    cue at a sentence boundary, so it can never answer "do these two fit
    together" -- it would just hand the same two cues back.
    """
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > MAX_LINE:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    if cur:
        lines.append(cur)
    return lines if len(lines) <= MAX_LINES else None


def chunk(text: str) -> list[str]:
    """Lay text out as cues of at most MAX_LINES lines of at most MAX_LINE chars.

    Packing into *lines* rather than into a flat character budget is what keeps
    the guarantee: a cue built from a budget can still fail to wrap into two
    lines at word boundaries, and then something has to give -- silently, as an
    over-long line that the player truncates or overflows.
    """
    cues: list[str] = []
    lines: list[str] = []
    cur = ""

    def end_line() -> None:
        nonlocal cur
        if cur:
            lines.append(cur)
            cur = ""

    def end_cue() -> None:
        nonlocal lines
        end_line()
        if lines:
            cues.append("\n".join(lines))
            lines = []

    for sent in sentences(text):
        for word in sent.split():
            if cur and len(cur) + 1 + len(word) > MAX_LINE:
                end_line()
                if len(lines) == MAX_LINES:
                    end_cue()
            # A single word wider than MAX_LINE gets its own line and overflows;
            # breaking mid-word is worse than a slightly long line.
            cur = f"{cur} {word}".strip() if cur else word
        end_line()
        if len(lines) >= MAX_LINES:
            end_cue()
        elif lines:
            # Sentence boundaries are the best place to cut a cue, so take it
            # rather than running the next sentence onto this one's spare line.
            end_cue()
    end_cue()
    return cues


def ts(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("build", type=Path, help="_video/<slug>")
    ap.add_argument("-o", "--output", type=Path, help="default <build>/out/talk.srt")
    ap.add_argument("--audio", default="audio/normalized",
                    help="audio dir the video was built from")
    ap.add_argument("--pad", type=float, default=0.2,
                    help="seconds of trimmed silence to inset at each slide edge")
    ap.add_argument("--cps", type=float, default=17.0,
                    help="reading speed used only to sanity-check cue lengths")
    args = ap.parse_args()

    frames_json = args.build / "frames.json"
    script = args.build / "script" / "narration.md"
    audio = args.build / args.audio
    for p in (frames_json, script):
        if not p.is_file():
            die(f"no such file: {p}")
    if not audio.is_dir():
        die(f"no such directory: {audio}")

    frames = json.loads(frames_json.read_text(encoding="utf-8"))
    blocks = load_blocks(script)

    out = args.output or (args.build / "out" / "talk.srt")
    out.parent.mkdir(parents=True, exist_ok=True)

    cues: list[tuple[float, float, str]] = []
    clock = 0.0
    empty: list[str] = []

    for f in frames:
        stem = Path(f["frame"]).stem
        wav = audio / f"{stem}.wav"
        if not wav.is_file():
            die(f"missing audio for {stem}: {wav}")
        span = duration(wav)
        start, end = clock, clock + span
        clock = end

        text = plain(blocks.get(stem, ""))
        if not text:
            empty.append(stem)
            continue

        # Speech sits inside the trimmed silence, so inset both edges.
        a, b = start + args.pad, max(start + args.pad + 0.1, end - args.pad)
        pieces = chunk(text)
        weights = [max(len(p.replace("\n", " ")), 1) for p in pieces]
        total = sum(weights)
        t = a
        for piece, w in zip(pieces, weights):
            d = (b - a) * (w / total)
            cues.append((t, t + d, piece))
            t += d

    # Roll up cues too short to read. Only ever merge cues that are adjacent in
    # time, which confines a merge to one slide and keeps every cue inside the
    # window of the audio it belongs to.
    merged: list[tuple[float, float, str]] = []
    for c in cues:
        if merged and c[1] - c[0] < MIN_CUE_S and abs(merged[-1][1] - c[0]) < 1e-6:
            joined = merged[-1][2].replace("\n", " ") + " " + c[2].replace("\n", " ")
            relaid = fit_lines(joined)
            if relaid is not None:
                merged[-1] = (merged[-1][0], c[1], "\n".join(relaid))
                continue
        merged.append(c)

    # A short cue that opens a slide has no predecessor to roll into, so roll it
    # forward. "Hello." on its own for 0.4s is unreadable in either direction.
    i = 0
    while i < len(merged) - 1:
        a, b, text = merged[i]
        if b - a < MIN_CUE_S and abs(b - merged[i + 1][0]) < 1e-6:
            joined = text.replace("\n", " ") + " " + merged[i + 1][2].replace("\n", " ")
            relaid = fit_lines(joined)
            if relaid is not None:
                merged[i:i + 2] = [(a, merged[i + 1][1], "\n".join(relaid))]
                continue
        i += 1

    # Some cues are still too brief to read -- a sentence tail whose neighbour is
    # already two full lines has nothing to merge with. Give it time instead of
    # text: absorb the silence that follows, then borrow from the next cue only
    # to the extent that the next cue can spare it.
    for i, (a, b, text) in enumerate(merged):
        if b - a >= MIN_CUE_S:
            continue
        need = MIN_CUE_S - (b - a)
        nxt_start = merged[i + 1][0] if i + 1 < len(merged) else b + need
        take = min(need, max(0.0, nxt_start - b))
        b += take
        need -= take
        if need > 0 and i + 1 < len(merged):
            na, nb, nt = merged[i + 1]
            give = min(need, max(0.0, (nb - na) - MIN_CUE_S))
            if give > 0:
                b += give
                merged[i + 1] = (na + give, nb, nt)
        merged[i] = (a, b, text)

    with out.open("w", encoding="utf-8") as fh:
        for i, (a, b, text) in enumerate(merged, 1):
            fh.write(f"{i}\n{ts(a)} --> {ts(b)}\n{text}\n\n")

    long = [c for c in merged if c[1] - c[0] > MAX_CUE_S]
    fast = [c for c in merged
            if len(c[2].replace("\n", " ")) / max(c[1] - c[0], 0.01) > args.cps * 1.6]

    print(f"Wrote {out}")
    print(f"  {len(merged)} cues over {ts(merged[-1][1]) if merged else '0'}")
    if empty:
        print(f"  {len(empty)} frame(s) with no narration text: {', '.join(empty[:6])}")
    if long:
        print(f"  {len(long)} cue(s) longer than {MAX_CUE_S}s (a slide with little text)")
    if fast:
        print(f"  {len(fast)} cue(s) above {args.cps * 1.6:.0f} char/s -- dense, still readable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
