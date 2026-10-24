#!/usr/bin/env bash
# Mirror every talk's raw narration takes to a backup location.
#
# _video/<slug>/audio/raw/ is the only thing in this repo that cannot be
# regenerated: everything else is rebuilt from tracked source, and the audio
# stages after raw/ are rebuilt from raw/ by the quarto-talk-video scripts.
# It is gitignored (too large), so nothing else protects it.
#
# On this machine audio/ is a symlink into /data/talks/ (nvme0). The default
# destination is on the other disk, so one drive failing loses neither copy.
# For an off-machine copy, pass a mounted drive or an rsync remote instead.
#
#   scripts/backup-takes.sh                      # → ~/backups/talks-takes
#   scripts/backup-takes.sh user@host:backups/talks-takes
#
# Additive: takes deleted locally are kept in the backup (no --delete).
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-$HOME/backups/talks-takes}"

shopt -s nullglob
raws=("$REPO"/_video/*/audio/raw)
if [ ${#raws[@]} -eq 0 ]; then
    echo "no _video/*/audio/raw directories found" >&2
    exit 1
fi

for raw in "${raws[@]}"; do
    slug="$(basename "$(dirname "$(dirname "$raw")")")"
    case "$DEST" in
        *:*) ;;                              # rsync remote: let rsync create it
        *)   mkdir -p "$DEST/$slug" ;;
    esac
    echo "== $slug"
    rsync -a --info=stats1 "$raw/" "$DEST/$slug/raw/"
done
