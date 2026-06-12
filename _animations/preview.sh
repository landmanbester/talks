#!/usr/bin/env bash
# Dev-loop render + frame sheet for the _animations/ explainer videos.
#
# Renders the scene at low quality, then extracts spot-check frames and
# prints their paths (read them with an image viewer / the Read tool).
#
# Usage:
#   preview.sh [-q l|m|h] [--no-render] <script.py> <SceneName> [t1 t2 ...]
#
#   -q l|m|h     quality (default l = 480p15; m = 720p30; h = 1080p60)
#   --no-render  skip rendering, just extract frames from the existing mp4
#   t1 t2 ...    timestamps (seconds) to extract; default: 10 evenly spaced
set -euo pipefail

MANIM="$HOME/software/manim/.venv/bin/manim"
QUAL=l
RENDER=1

while [[ $# -gt 0 ]]; do
    case "$1" in
        -q) QUAL="$2"; shift 2 ;;
        --no-render) RENDER=0; shift ;;
        *) break ;;
    esac
done

if [[ $# -lt 2 ]]; then
    echo "usage: preview.sh [-q l|m|h] [--no-render] <script.py> <SceneName> [t1 t2 ...]" >&2
    exit 2
fi

SCRIPT="$1"; SCENE="$2"; shift 2

case "$QUAL" in
    l) RES=480p15 ;;
    m) RES=720p30 ;;
    h) RES=1080p60 ;;
    *) echo "unknown quality: $QUAL" >&2; exit 2 ;;
esac

cd "$(dirname "$SCRIPT")"
SCRIPT="$(basename "$SCRIPT")"
STEM="${SCRIPT%.py}"
MP4="media/videos/$STEM/$RES/$SCENE.mp4"

if [[ $RENDER -eq 1 ]]; then
    # run manim bare — piping it (e.g. through tail) masks its exit code
    "$MANIM" -q"$QUAL" "$SCRIPT" "$SCENE"
fi

[[ -f "$MP4" ]] || { echo "no render found at $MP4" >&2; exit 1; }
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$MP4")

if [[ $# -eq 0 ]]; then
    # 10 evenly spaced timestamps, avoiding the very start/end
    mapfile -t TIMES < <(awk -v d="$DUR" 'BEGIN { for (i = 1; i <= 10; i++) printf "%.1f\n", d * i / 11 }')
else
    TIMES=("$@")
fi

OUT="/tmp/manim-frames/$SCENE"
rm -rf "$OUT"
mkdir -p "$OUT"

echo "video:    $PWD/$MP4"
echo "duration: ${DUR}s"
echo "frames:"
for t in "${TIMES[@]}"; do
    f="$OUT/f${t/./p}.png"
    ffmpeg -y -loglevel error -ss "$t" -i "$MP4" -frames:v 1 "$f"
    echo "  $f"
done
