#!/usr/bin/env bash
# Render a Quarto revealjs deck straight to numbered 1920x1080 PNG frames.
#
# Uses decktape's --screenshots, which emits PNGs at an exact requested size.
# This avoids the PDF -> pdftoppm hop entirely, and with it the whole class of
# off-by-a-few-pixels frames that then need padding before muxing.
#
# decktape's own screenshot filenames embed an index and the size, e.g.
# talk_1_1920x1080.png. The exact pattern has varied across versions, so rather
# than assume it, this script version-sorts whatever PNGs appear and renumbers
# them to slide-01.png, slide-02.png, ...
#
# Usage: extract_slides.sh <talk.html> <outdir> [WxH] [pause_ms]
set -euo pipefail

HTML=${1:?usage: extract_slides.sh <talk.html> <outdir> [WxH] [pause_ms]}
OUT=${2:?usage: extract_slides.sh <talk.html> <outdir> [WxH] [pause_ms]}
SIZE=${3:-1920x1080}
PAUSE=${4:-1000}

[ -f "$HTML" ] || { echo "ERROR: no such file: $HTML" >&2; exit 1; }
ABS=$(readlink -f "$HTML")
W=${SIZE%x*}; H=${SIZE#*x}

mkdir -p "$OUT"
SHOTS=$(mktemp -d); trap 'rm -rf "$SHOTS"' EXIT

# ?print-pdf puts reveal.js in its linear export mode, one frame per slide (and
# per fragment, given pdf-separate-fragments: true in the deck front matter).
echo "Rendering $ABS at $SIZE ..."
npx -y decktape reveal "file://${ABS}?print-pdf" "$SHOTS/deck.pdf" \
  -s "$SIZE" --pause "$PAUSE" \
  --screenshots --screenshots-directory "$SHOTS" \
  --screenshots-size "$SIZE" --screenshots-format png

shopt -s nullglob
frames=($(ls "$SHOTS"/*.png 2>/dev/null | sort -V))
if [ ${#frames[@]} -eq 0 ]; then
  echo "ERROR: decktape produced no screenshots. Check that the deck loads in a" >&2
  echo "       browser at file://${ABS}?print-pdf before retrying." >&2
  exit 1
fi

rm -f "$OUT"/slide-*.png
i=0
for f in "${frames[@]}"; do
  i=$((i+1))
  printf -v dest 'slide-%02d.png' "$i"
  cp "$f" "$OUT/$dest"
done

# Verify every frame is exactly the requested size. A frame that is not means
# the mux will letterbox or stretch it, and a stretched plot axis is a bad look.
bad=0
for f in "$OUT"/slide-*.png; do
  dim=$(ffprobe -v error -select_streams v:0 \
        -show_entries stream=width,height -of csv=p=0:s=x "$f")
  if [ "$dim" != "${W}x${H}" ]; then
    echo "  WARN: $(basename "$f") is $dim, expected ${W}x${H}" >&2
    bad=$((bad+1))
  fi
done

echo
echo "Extracted $i frame(s) into $OUT  ($((bad)) size mismatch(es))"
echo
echo "NEXT: open 2-3 of these and confirm the count matches your slide count."
echo "      decktape truncating at a broken slide is silent, and you will not"
echo "      notice until the finished video comes out short."
