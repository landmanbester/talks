#!/usr/bin/env bash
# Safe final render for the _animations/ explainer videos.
#
# Clears stale partial_movie_files first (a truncated segment from an
# interrupted run poisons the stitch: silently short mp4 or InvalidDataError,
# and --flush_cache does NOT fix it), renders bare so the exit code is real,
# then ffprobe-checks the duration against any existing dev render.
#
# Usage:
#   final.sh [-q h|k|m|l] <script.py> <SceneName>
#
#   -q  quality (default h = 1080p60; k = 2160p60 4K)
set -euo pipefail

MANIM="$HOME/software/manim/.venv/bin/manim"
QUAL=h

while [[ $# -gt 0 ]]; do
    case "$1" in
        -q) QUAL="$2"; shift 2 ;;
        *) break ;;
    esac
done

if [[ $# -ne 2 ]]; then
    echo "usage: final.sh [-q h|k|m|l] <script.py> <SceneName>" >&2
    exit 2
fi

SCRIPT="$1"; SCENE="$2"

case "$QUAL" in
    l) RES=480p15 ;;
    m) RES=720p30 ;;
    h) RES=1080p60 ;;
    k) RES=2160p60 ;;
    *) echo "unknown quality: $QUAL" >&2; exit 2 ;;
esac

cd "$(dirname "$SCRIPT")"
SCRIPT="$(basename "$SCRIPT")"
STEM="${SCRIPT%.py}"
MP4="media/videos/$STEM/$RES/$SCENE.mp4"

# pre-flight: a final render must not inherit possibly-corrupt partials
rm -rf "media/videos/$STEM/$RES/partial_movie_files"

"$MANIM" -q"$QUAL" "$SCRIPT" "$SCENE"

[[ -f "$MP4" ]] || { echo "render reported success but $MP4 is missing" >&2; exit 1; }
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$MP4")

# cross-check duration against any dev render of the same scene
STATUS=0
for other in 480p15 720p30 1080p60 2160p60; do
    [[ "$other" == "$RES" ]] && continue
    REF="media/videos/$STEM/$other/$SCENE.mp4"
    if [[ -f "$REF" ]]; then
        REFDUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$REF")
        # frame-rate rounding gives ~1s drift between 15fps and 60fps renders;
        # a poisoned stitch loses tens of seconds — only flag gross mismatch
        if ! awk -v a="$DUR" -v b="$REFDUR" 'BEGIN { d = a - b; if (d < 0) d = -d; exit !(d < 5.0) }'; then
            echo "WARNING: duration ${DUR}s differs from $other render (${REFDUR}s) — stitch may be broken" >&2
            STATUS=1
        fi
    fi
done

echo "video:    $PWD/$MP4"
echo "duration: ${DUR}s"
echo "size:     $(du -h "$MP4" | cut -f1)"
exit $STATUS
