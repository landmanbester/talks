#!/usr/bin/env bash
# Two-pass EBU R128 loudness normalization.
# Pass 1 measures; pass 2 applies a linear gain using the measured values.
# Single-pass loudnorm uses a running estimate and pumps between files recorded
# in different sessions -- which is the normal case for per-slide narration.
#
# Usage: normalize_audio.sh <indir> <outdir> [target_lufs]
set -euo pipefail

IN=${1:?usage: normalize_audio.sh <indir> <outdir> [target_lufs]}
OUT=${2:?usage: normalize_audio.sh <indir> <outdir> [target_lufs]}
I=${3:--16}
TP=-1.5
LRA=11

mkdir -p "$OUT"
shopt -s nullglob
files=("$IN"/*.wav)
if [ ${#files[@]} -eq 0 ]; then
  echo "ERROR: no .wav files in $IN" >&2
  exit 1
fi

for f in "${files[@]}"; do
  base=$(basename "$f")

  # Pass 1: measure. loudnorm prints its JSON block to stderr.
  meas=$(ffmpeg -hide_banner -nostats -i "$f" \
    -af "loudnorm=I=$I:TP=$TP:LRA=$LRA:print_format=json" \
    -f null - 2>&1 | sed -n '/^{/,/^}/p')

  read -r m_i m_tp m_lra m_thresh offset <<<"$(python3 -c '
import json, sys
d = json.load(sys.stdin)
print(d["input_i"], d["input_tp"], d["input_lra"],
      d["input_thresh"], d["target_offset"])
' <<<"$meas")"

  # A measured integrated loudness of -inf means the file is effectively silent.
  case "$m_i" in
    -inf|-70.0|-70)
      echo "WARN: $base looks silent (input_i=$m_i) -- copying unchanged" >&2
      cp "$f" "$OUT/$base"
      continue
      ;;
  esac

  # Pass 2: apply as a linear gain so dynamics are preserved.
  ffmpeg -hide_banner -loglevel error -y -i "$f" \
    -af "loudnorm=I=$I:TP=$TP:LRA=$LRA:measured_I=$m_i:measured_TP=$m_tp:\
measured_LRA=$m_lra:measured_thresh=$m_thresh:offset=$offset:linear=true:print_format=summary" \
    -ar 48000 -ac 1 -c:a pcm_s24le "$OUT/$base"

  printf '  %-24s %8s LUFS -> %s LUFS\n' "$base" "$m_i" "$I"
done

echo "Normalized ${#files[@]} file(s) into $OUT"
