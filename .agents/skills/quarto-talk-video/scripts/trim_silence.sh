#!/usr/bin/env bash
# Trim leading and trailing silence from narration takes -- the dead air around
# hitting record and stop. Mid-take pauses are PRESERVED on purpose: in
# equation-heavy narration they are load-bearing, and tools that cut them make
# the delivery sound rushed.
#
# Trailing silence is handled by reversing, trimming the (now leading) silence,
# and reversing back -- ffmpeg's silenceremove only reliably trims from the start.
#
# Usage: trim_silence.sh <indir> <outdir> [pad_seconds] [threshold_dB]
set -euo pipefail

IN=${1:?usage: trim_silence.sh <indir> <outdir> [pad_seconds] [threshold_dB]}
OUT=${2:?usage: trim_silence.sh <indir> <outdir> [pad_seconds] [threshold_dB]}
PAD=${3:-0.25}      # silence left in place at each end, seconds
THRESH=${4:--45}    # dB below which audio counts as silence

mkdir -p "$OUT"
shopt -s nullglob
files=("$IN"/*.wav)
if [ ${#files[@]} -eq 0 ]; then
  echo "ERROR: no .wav files in $IN" >&2
  exit 1
fi

FILT="silenceremove=start_periods=1:start_silence=${PAD}:start_threshold=${THRESH}dB:detection=rms"

for f in "${files[@]}"; do
  base=$(basename "$f")
  before=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")

  ffmpeg -hide_banner -loglevel error -y -i "$f" \
    -af "${FILT},areverse,${FILT},areverse" \
    -ar 48000 -ac 1 -c:a pcm_s24le "$OUT/$base"

  after=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/$base")
  printf '  %-24s %6.1fs -> %6.1fs  (-%.1fs)\n' \
    "$base" "$before" "$after" "$(python3 -c "print($before-$after)")"

  # A take that shrinks to almost nothing means the threshold ate real speech,
  # usually because the recording level was very low.
  if python3 -c "import sys; sys.exit(0 if $after < 0.5 else 1)"; then
    echo "  WARN: $base is now under 0.5s -- check recording level or raise threshold" >&2
  fi
done

total=$(python3 -c "
import subprocess, glob
print(sum(float(subprocess.run(['ffprobe','-v','error','-show_entries',
  'format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
  for f in sorted(glob.glob('$OUT/*.wav'))))")
printf 'Trimmed %d file(s). Total: %s\n' "${#files[@]}" \
  "$(python3 -c "t=$total; print(f'{int(t//60)}:{t%60:04.1f}')")"
