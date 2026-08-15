#!/usr/bin/env python3
"""Record one narration take per frame, keeping filenames in lockstep.

Reads `frames.json` and `script/narration.md`, shows you one block at a time,
and writes the take to `audio/raw/slide-NN.wav` under the frame number it
belongs to. That mapping is the entire point: a take saved under the wrong
number desyncs every frame after it, and you do not find out until the muxed
video is wrong.

Records mono / 48 kHz / 24-bit, which is what the rest of the pipeline expects.
Prefers pw-record when PipeWire is running, else arecord.

Usage:
    record_narration.py _video/<slug>              # resume at first unrecorded
    record_narration.py _video/<slug> --status     # what is done, what is not
    record_narration.py _video/<slug> --level      # mic level check, records nothing
    record_narration.py _video/<slug> --from 12    # start at a frame
    record_narration.py _video/<slug> --only 7 19  # re-record specific frames

Per frame: Enter starts, Enter stops, then keep / redo / play. Nothing is
overwritten until you keep a take.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import signal
import subprocess
import sys
import textwrap
from pathlib import Path

HEADING = re.compile(r"^##\s+(slide-(\d+))\s*(?:[—-]\s*(.*?))?\s*\((\d+)s\)\s*$")
FRAME_NUM = re.compile(r"slide-(\d+)")
RATE, CHANNELS = 48000, 1


def die(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    sys.exit(f"error: {msg}")


def pipewire_running() -> bool:
    return subprocess.run(["pgrep", "-x", "pipewire"],
                          capture_output=True).returncode == 0


def record_cmd(dest: Path, device: str | None, seconds: float | None = None) -> list[str]:
    """pw-record routes through the user's normal input; arecord talks to ALSA
    directly, which under PipeWire only works via pipewire-alsa."""
    if shutil.which("pw-record") and pipewire_running():
        cmd = ["pw-record", "--rate", str(RATE), "--channels", str(CHANNELS),
               "--format", "s24"]
        if device:
            cmd += ["--target", device]
        return cmd + [str(dest)]
    if shutil.which("arecord"):
        cmd = ["arecord", "-f", "S24_3LE", "-r", str(RATE), "-c", str(CHANNELS)]
        if device:
            cmd += ["-D", device]
        if seconds:
            cmd += ["-d", str(int(seconds))]
        return cmd + [str(dest)]
    die("no pw-record or arecord on PATH")


def play(path: Path) -> None:
    for tool, extra in (("pw-play", []), ("aplay", []),
                        ("ffplay", ["-autoexit", "-nodisp", "-loglevel", "error"])):
        if shutil.which(tool):
            subprocess.run([tool, *extra, str(path)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
    print("  (no player found)")


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def levels(path: Path) -> tuple[float, float]:
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-af", "volumedetect",
         "-f", "null", "-"], capture_output=True, text=True).stderr

    def grab(key: str) -> float:
        m = re.search(rf"{key}:\s*(-?[\d.]+) dB", out)
        return float(m.group(1)) if m else 0.0

    return grab("max_volume"), grab("mean_volume")


def verdict(peak: float, mean: float) -> str:
    if peak >= -0.5:
        return "CLIPPING — cut the gain or back off the mic, and redo"
    if peak < -30:
        return "very quiet — raise the gain or get closer"
    if mean < -40:
        return "quiet; normalization will lift it, and the noise floor with it"
    return "levels fine"


def load_blocks(script: Path) -> dict[str, dict]:
    blocks: dict[str, dict] = {}
    current = None
    for line in script.read_text(encoding="utf-8").splitlines():
        m = HEADING.match(line)
        if m:
            current = {"title": (m.group(3) or "").strip(),
                       "budget": int(m.group(4)), "lines": []}
            blocks[m.group(1)] = current
        elif current is not None and line.strip() and not line.startswith("#"):
            current["lines"].append(line.strip())
    return blocks


def frame_number(frame: str) -> int:
    m = FRAME_NUM.search(frame)
    return int(m.group(1)) if m else -1


def mmss(seconds: float) -> str:
    return f"{int(seconds // 60)}:{seconds % 60:04.1f}"


def do_status(frames: list[dict], raw: Path) -> int:
    done = 0
    total = 0.0
    for f in frames:
        stem = Path(f["frame"]).stem
        wav = raw / f"{stem}.wav"
        if wav.exists():
            d = duration(wav)
            total += d
            done += 1
            print(f"  {stem}  {d:5.1f}s   {f['title'][:48]}")
        else:
            print(f"  {stem}     --     {f['title'][:48]}   NOT RECORDED")
    print(f"\n  {done}/{len(frames)} recorded, {mmss(total)} of audio")
    return 0


def do_level(raw: Path, device: str | None) -> None:
    probe = raw / ".level-check.wav"
    probe.unlink(missing_ok=True)
    print("Level check — read a sentence at the volume you will present at.")
    input("[Enter] to start, then [Enter] again to stop > ")
    proc = subprocess.Popen(record_cmd(probe, device),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        input("  ● recording — Enter to stop ")
    except KeyboardInterrupt:
        pass
    proc.send_signal(signal.SIGINT)
    proc.wait()
    if probe.exists() and probe.stat().st_size > 1024:
        pk, mn = levels(probe)
        print(f"  peak {pk:.1f} dBFS, mean {mn:.1f} dBFS — {verdict(pk, mn)}")
        print("  Aim for peaks around -6 to -12 dBFS. Normalization fixes the level,")
        print("  it cannot fix clipping or a loud room.\n")
    else:
        print("  nothing captured — check your input device with --device\n")
    probe.unlink(missing_ok=True)


def record_one(stem: str, block: dict, wav: Path, device: str | None) -> str:
    """Returns 'kept', 'skipped', or 'quit'."""
    while True:
        print("\n" + "=" * 72)
        print(f"{stem}   {block['title']}   (budget {block['budget']}s)"
              + ("   [re-recording]" if wav.exists() else ""))
        print("=" * 72)
        for line in textwrap.wrap(" ".join(block["lines"]), 72):
            print(f"  {line}")
        print()

        choice = input("[Enter] record   s skip   q quit > ").strip().lower()
        if choice == "q":
            return "quit"
        if choice == "s":
            return "skipped"

        # Record to a temporary file so a bad take never destroys a good one.
        tmp = wav.with_suffix(".take.wav")
        tmp.unlink(missing_ok=True)
        proc = subprocess.Popen(record_cmd(tmp, device),
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            input("  ● recording — Enter to stop ")
            proc.send_signal(signal.SIGINT)
            proc.wait()
        except KeyboardInterrupt:
            proc.send_signal(signal.SIGINT)
            proc.wait()
            tmp.unlink(missing_ok=True)
            print("\n  discarded")
            continue

        if not tmp.exists() or tmp.stat().st_size < 1024:
            tmp.unlink(missing_ok=True)
            print("  nothing captured — check your input device with --device")
            continue

        d = duration(tmp)
        pk, mn = levels(tmp)
        print(f"  {d:.1f}s ({d - block['budget']:+.1f}s vs budget)   "
              f"peak {pk:.1f} dBFS — {verdict(pk, mn)}")

        while True:
            what = input("  [Enter] keep   r redo   p play > ").strip().lower()
            if what == "p":
                play(tmp)
                continue
            break
        if what == "r":
            tmp.unlink(missing_ok=True)
            continue
        tmp.replace(wav)
        return "kept"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("build", type=Path, help="_video/<slug>")
    ap.add_argument("--from", dest="start", type=int, default=0, metavar="N",
                    help="start at frame N")
    ap.add_argument("--only", type=int, nargs="+", metavar="N",
                    help="record exactly these frames, recorded or not")
    ap.add_argument("--status", action="store_true", help="report and exit")
    ap.add_argument("--level", action="store_true", help="mic level check first")
    ap.add_argument("--device", help="pw-record --target, or arecord -D value")
    args = ap.parse_args()

    frames_json = args.build / "frames.json"
    script = args.build / "script" / "narration.md"
    for p in (frames_json, script):
        if not p.is_file():
            die(f"no such file: {p}")
    raw = args.build / "audio" / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    frames = json.loads(frames_json.read_text(encoding="utf-8"))
    blocks = load_blocks(script)

    missing = [Path(f["frame"]).stem for f in frames
               if Path(f["frame"]).stem not in blocks]
    if missing:
        die(f"narration.md has no block for: {', '.join(missing[:5])}"
            + (" ..." if len(missing) > 5 else ""))

    if args.status:
        return do_status(frames, raw)
    if args.level:
        do_level(raw, args.device)

    if args.only:
        todo = [f for f in frames if frame_number(f["frame"]) in args.only]
    else:
        todo = [f for f in frames
                if frame_number(f["frame"]) >= args.start
                and not (raw / f"{Path(f['frame']).stem}.wav").exists()]

    if not todo:
        print("Every frame is already recorded. Use --only N to redo one.")
        return 0

    print(f"\n{len(todo)} frame(s) to record. Takes are written only when you keep them.")

    kept = 0
    for f in todo:
        stem = Path(f["frame"]).stem
        result = record_one(stem, blocks[stem], raw / f"{stem}.wav", args.device)
        if result == "quit":
            break
        kept += result == "kept"

    print(f"\nKept {kept} take(s).")
    recorded = sum(1 for f in frames if (raw / f"{Path(f['frame']).stem}.wav").exists())
    print(f"{recorded}/{len(frames)} frames now have audio.")
    if recorded == len(frames):
        print("\nNext: trim_silence.sh, then normalize_audio.sh, then build_video.sh.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
