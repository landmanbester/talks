#!/usr/bin/env bash
# Validate a finished MP4 against a conference submission spec.
# Exits non-zero on any FAIL. Run this before renaming to the submission filename.
#
# Usage: validate_video.sh <video.mp4> [spec.json]
set -uo pipefail

VIDEO=${1:?usage: validate_video.sh <video.mp4> [spec.json]}
SPEC=${2:-spec.json}

[ -f "$VIDEO" ] || { echo "ERROR: no such file: $VIDEO" >&2; exit 1; }
[ -f "$SPEC" ]  || { echo "ERROR: no spec file: $SPEC" >&2; exit 1; }

ffprobe -v error -print_format json -show_format -show_streams "$VIDEO" > /tmp/probe.json

python3 - "$VIDEO" "$SPEC" <<'PY'
import json, os, sys, re

video, spec_path = sys.argv[1], sys.argv[2]
spec  = json.load(open(spec_path))
probe = json.load(open("/tmp/probe.json"))

fmt = probe["format"]
v = next((s for s in probe["streams"] if s["codec_type"] == "video"), None)
a = next((s for s in probe["streams"] if s["codec_type"] == "audio"), None)

fails, warns = [], []
def check(ok, label, detail):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label:<22} {detail}")
    if not ok:
        fails.append(label)

print(f"\n{os.path.basename(video)}\n")

dur = float(fmt["duration"])
limit = spec["max_duration_s"]
check(dur <= limit, "duration",
      f"{int(dur//60)}:{dur%60:04.1f}  (limit {int(limit//60)}:{limit%60:02.0f})")
if dur > limit * 0.97:
    warns.append(f"only {limit-dur:.0f}s of headroom -- one re-record could push it over")

size = int(fmt["size"])
check(size <= spec["max_size_bytes"], "file size",
      f"{size/2**30:.2f} GiB  (limit {spec['max_size_bytes']/2**30:.2f} GiB)")

check(spec["container"] in fmt["format_name"].split(","), "container",
      fmt["format_name"])
check(v is not None and v["codec_name"] == spec["video_codec"], "video codec",
      v["codec_name"] if v else "NO VIDEO STREAM")
check(a is not None and a["codec_name"] == spec["audio_codec"], "audio codec",
      a["codec_name"] if a else "NO AUDIO STREAM")

if v:
    check(v.get("pix_fmt") == "yuv420p", "pixel format",
          f"{v.get('pix_fmt')}  (yuv420p required for broad playback)")
    check((v.get("width"), v.get("height")) == (1920, 1080), "resolution",
          f"{v.get('width')}x{v.get('height')}")

# faststart: the moov atom must precede mdat or the file buffers badly on web players.
with open(video, "rb") as fh:
    head = fh.read(1 << 20)
moov, mdat = head.find(b"moov"), head.find(b"mdat")
check(moov != -1 and (mdat == -1 or moov < mdat), "faststart",
      "moov before mdat" if moov != -1 else "moov not in first 1 MiB -- remux with -movflags +faststart")

# Silent-audio catch: a muxed-but-empty track is a classic late-night mistake.
if a and float(a.get("duration", 0) or 0) < dur * 0.5:
    warns.append("audio stream much shorter than video -- check the mux")

name = os.path.basename(video)
pat = spec.get("filename_pattern", "")
if pat:
    rx = "^" + re.sub(r"\\\{[a-z_]+\\\}", r"[A-Za-z0-9._-]+", re.escape(pat)) + "$"
    ok = re.match(rx, name) is not None
    print(f"  [{'PASS' if ok else 'TODO'}] {'filename':<22} {name}   (pattern {pat})")
    if not ok:
        warns.append(f"rename to match {pat} before submitting")
if re.search(r"[^A-Za-z0-9._-]", name):
    warns.append("filename has spaces or non-ASCII characters -- some portals reject these")

for w in warns:
    print(f"  [WARN] {w}")

print()
if fails:
    print(f"NOT COMPLIANT -- {len(fails)} check(s) failed: {', '.join(fails)}")
    sys.exit(1)
print("Compliant. Safe to rename and submit.")
PY
