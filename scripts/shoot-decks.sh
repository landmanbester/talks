#!/usr/bin/env bash
# Render the site and screenshot every deck's title slide.
# Usage: scripts/shoot-decks.sh [--no-render] <output-dir> [port]
#
# --no-render reuses the existing _site build. A full render takes several
# minutes, so pass it when you have already rendered.
set -euo pipefail

RENDER=1
if [ "${1:-}" = "--no-render" ]; then RENDER=0; shift; fi

OUT="${1:?usage: shoot-decks.sh [--no-render] <output-dir> [port]}"
PORT="${2:-4321}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$OUT"
cd "$ROOT"

if [ "$RENDER" -eq 1 ]; then
  echo "--- rendering ---"
  quarto render
else
  echo "--- reusing existing _site ---"
fi

# Serve _site statically; quarto preview would rebuild and race us.
python3 -m http.server "$PORT" --directory _site >/dev/null 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null || true' EXIT
sleep 2

# Every directory in _site containing an index.html other than the root.
# A wedged headless Chrome would otherwise hang the whole run, so cap each
# shot. `|| true` keeps one bad deck from aborting the rest under `set -e`.
for page in $(find _site -mindepth 2 -name index.html); do
  rel="${page#_site/}"; rel="${rel%/index.html}"
  slug="$(echo "$rel" | tr '/' '-')"
  printf -- '--- shooting %-34s ' "$rel"
  timeout 90 google-chrome --headless=new \
    --screenshot="$OUT/$slug.png" \
    --window-size=1600,900 \
    --virtual-time-budget=6000 \
    "http://localhost:$PORT/$rel/#/title-slide" >/dev/null 2>&1 || true
  if [ -s "$OUT/$slug.png" ]; then echo "ok"; else echo "FAILED"; fi
done

echo "--- wrote to $OUT ---"
ls -1 "$OUT"
