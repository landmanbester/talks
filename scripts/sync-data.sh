#!/usr/bin/env bash
# Keep the large-data store (/data/talks/) in step with its Google Drive copy.
#
#   scripts/sync-data.sh status          # what differs, in either direction
#   scripts/sync-data.sh push [-n]       # local → Drive   (-n: dry run)
#   scripts/sync-data.sh pull [-n]       # Drive → local, then link into the repo
#
# rclone only transfers files whose MD5 differs (--checksum; Drive stores the
# hashes), so a run where nothing changed moves nothing. rsync cannot talk to
# Drive; rclone is the equivalent.
#
# Neither direction can lose data:
#   push  mirrors local onto Drive, but a file deleted or overwritten locally
#         is moved to _deleted/<timestamp>/ on Drive, not removed
#   pull  only fetches files missing locally; an existing local file is never
#         touched, even if Drive's copy differs (Drive mtimes from a browser
#         upload are upload times, so "newer" cannot be trusted)
#
# One-time setup — the folder ID lives in the rclone config, not in this repo:
#   rclone config create talks-drive drive scope=drive root_folder_id=<folder-id>
#
# Override the locations with TALKS_DATA and TALKS_REMOTE.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DATA="${TALKS_DATA:-/data/talks}"
REMOTE="${TALKS_REMOTE:-talks-drive:}"
# Paths are built as ${REMOTE}<sub>, so a remote with a subpath needs a slash
case "$REMOTE" in *: | */) ;; *) REMOTE="$REMOTE/" ;; esac

# manim media/ is regenerable and its caches churn on every render; _deleted/
# is push's own safety net and must never be mirrored back into itself.
FILTERS=(--exclude "_deleted/**" --exclude "media/**")
COMMON=(--checksum --fast-list --transfers 8 --stats-one-line --stats 30s -v)

usage() { sed -n '2,6p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }

# Recreate the repo's symlinks into $DATA for whatever the store holds, so a
# fresh clone is usable after one pull. Existing links and real directories
# are left alone.
link_into_repo() {
    local targets=()
    [ -d "$DATA/fits_files" ] && targets+=("fits_files")
    for p in "$DATA"/_video/*/audio "$DATA"/_animations/*/media \
             "$DATA"/lectures/*/media "$DATA"/contributions/*/media \
             "$DATA"/lectures/*/videos "$DATA"/contributions/*/videos; do
        [ -d "$p" ] && targets+=("${p#"$DATA"/}")
    done
    for rel in "${targets[@]}"; do
        local link="$REPO/$rel"
        if [ -e "$link" ] || [ -L "$link" ]; then continue; fi
        if [ ! -d "$(dirname "$link")" ]; then
            echo "skip $rel: $(dirname "$rel")/ is not in this checkout"
            continue
        fi
        ln -s "$DATA/$rel" "$link"
        echo "linked $rel -> $DATA/$rel"
    done
}

cmd="${1:-}"; shift || true
dry=()
case "${1:-}" in -n|--dry-run) dry=(--dry-run); shift ;; "") ;; *) usage ;; esac
[ $# -eq 0 ] || usage

case "$cmd" in
    status)
        # rclone check exits 1 both for "files differ" and for an unreachable
        # remote, so rule out the failures first — a silent "no differences"
        # must never be the result of not having looked.
        [ -d "$DATA" ] || { echo "error: $DATA does not exist" >&2; exit 1; }
        rclone lsf --max-depth 1 "$REMOTE" >/dev/null \
            || { echo "error: cannot list $REMOTE (rclone config?)" >&2; exit 1; }
        report="$(mktemp)"; trap 'rm -f "$report"' EXIT
        rc=0
        rclone check "$DATA" "$REMOTE" "${FILTERS[@]}" --checksum --fast-list -q \
            --combined "$report" || rc=$?
        grep -v '^= ' "$report" || true
        echo "(+ local only, - Drive only, * differs, ! error; identical files hidden)"
        [ "$rc" -le 1 ] || exit "$rc"
        ;;
    push)
        rclone sync "$DATA" "$REMOTE" "${FILTERS[@]}" "${COMMON[@]}" "${dry[@]}" \
            --backup-dir "${REMOTE}_deleted/$(date +%Y-%m-%dT%H%M%S)"
        ;;
    pull)
        mkdir -p "$DATA"
        rclone copy "$REMOTE" "$DATA" "${FILTERS[@]}" "${COMMON[@]}" "${dry[@]}" --ignore-existing
        if [ ${#dry[@]} -eq 0 ]; then link_into_repo; fi
        ;;
    *) usage ;;
esac
