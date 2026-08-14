#!/usr/bin/env bash
# Mux slide PNGs + per-slide narration into a single H.264/AAC MP4.
#
# Expects, under <workdir>:
#   slide-01.png, slide-02.png, ...
#   audio/normalized/slide-01.wav, slide-02.wav, ...
#
# Usage: build_video.sh <workdir> [output.mp4]
set -euo pipefail

WORK=${1:?usage: build_video.sh <workdir> [output.mp4]}
OUTPUT=${2:-$WORK/talk.mp4}
AUDIO_DIR="$WORK/audio/normalized"

cd "$WORK"
shopt -s nullglob
# Version-sort rather than relying on glob order: a deck large enough to reach
# slide-100.png would otherwise sort it ahead of slide-11.png.
slides=($(ls slide-*.png 2>/dev/null | sort -V))
tracks=($(ls "$AUDIO_DIR"/slide-*.wav 2>/dev/null | sort -V))

if [ ${#slides[@]} -eq 0 ]; then
  echo "ERROR: no slide-*.png in $WORK" >&2
  exit 1
fi

# Hard-fail on mismatch rather than zipping the shorter list, which silently
# drops the tail of the talk.
if [ ${#slides[@]} -ne ${#tracks[@]} ]; then
  echo "ERROR: ${#slides[@]} slides but ${#tracks[@]} audio tracks." >&2
  echo "       Slides without narration, or narration without slides:" >&2
  diff <(printf '%s\n' "${slides[@]}" | sed 's/\.png$//') \
       <(printf '%s\n' "${tracks[@]}" | xargs -n1 basename | sed 's/\.wav$//') >&2 || true
  exit 1
fi

FRAMES=$(mktemp); AUDIOS=$(mktemp)
trap 'rm -f "$FRAMES" "$AUDIOS"' EXIT

total=0
for png in "${slides[@]}"; do
  wav="$AUDIO_DIR/${png%.png}.wav"
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$wav")
  printf "file '%s'\nduration %s\n" "$PWD/$png" "$dur" >> "$FRAMES"
  printf "file '%s'\n" "$wav" >> "$AUDIOS"
  total=$(python3 -c "print($total + $dur)")
  printf '  %-18s %6.1f s\n' "${png%.png}" "$dur"
  last="$png"
done

# The concat demuxer ignores the duration of the final entry, so the last image
# must be repeated or the closing slide is dropped.
printf "file '%s'\n" "$PWD/$last" >> "$FRAMES"

printf 'Total narration: %s\n' "$(python3 -c "
t=$total; print(f'{int(t//60)}:{t%60:04.1f}')")"

ffmpeg -hide_banner -loglevel warning -y \
  -f concat -safe 0 -i "$FRAMES" \
  -f concat -safe 0 -i "$AUDIOS" \
  -vf "fps=30,format=yuv420p" \
  -c:v libx264 -preset medium -crf 20 \
  -c:a aac -b:a 192k -ar 48000 -ac 1 \
  -movflags +faststart \
  -shortest "$OUTPUT"

echo "Wrote $OUTPUT"
ls -lh "$OUTPUT"
