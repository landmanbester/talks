#!/usr/bin/env bash
# Upload every deck's videos/ to the `site-videos` GitHub release, where the
# publish workflow (.github/workflows/publish.yml) fetches them before rendering.
#
#   scripts/publish-videos.sh        # tar, upload (replacing the old tarball)
#   scripts/publish-videos.sh -n     # list what would go in, upload nothing
#
# The videos are not tracked in git: each <class>/<slug>/videos is a symlink
# into /data/talks/. Run this whenever a deck's videos change, *before* pushing
# the deck change to main — otherwise the site is built against the old set.
# Needs `gh` logged in with write access to the repo.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
TAG="site-videos"
cd "$REPO"

dirs=()
for d in lectures/*/videos contributions/*/videos; do
    [ -e "$d" ] && dirs+=("$d")
done
[ ${#dirs[@]} -gt 0 ] || { echo "error: no */*/videos directories found" >&2; exit 1; }

# The upload replaces the whole set, so a missing videos/ link would silently
# drop that deck from the site. Same check as the publish workflow: every
# video a deck references must exist here before anything is uploaded.
missing=0
for qmd in lectures/*/*.qmd contributions/*/*.qmd; do
    dir=$(dirname "$qmd")
    for v in $(grep -oE 'videos/[^"'"'"' )>]+\.(mp4|webm|mov)' "$qmd" | sort -u); do
        if [ ! -f "$dir/$v" ]; then echo "missing $dir/$v" >&2; missing=1; fi
    done
done
if [ "$missing" -ne 0 ]; then
    echo "error: not uploading. Is a videos/ symlink into /data/talks/ missing?" \
         "scripts/sync-data.sh pull recreates them." >&2
    exit 1
fi

if [ "${1:-}" = "-n" ]; then
    du -shL "${dirs[@]}"
    exit 0
fi

out="$(mktemp -d /data/tmp/site-videos.XXXXXX)"
trap 'rm -r "$out"' EXIT
# -h follows the symlinks, so the archive holds real files at repo-relative paths
tar -chf "$out/videos.tar" "${dirs[@]}"
du -h "$out/videos.tar"

if ! gh release view "$TAG" >/dev/null 2>&1; then
    gh release create "$TAG" --title "Site videos" --latest=false \
        --notes "Deck videos for the published site. Uploaded by scripts/publish-videos.sh; not a software release."
fi
gh release upload "$TAG" "$out/videos.tar" --clobber
echo "uploaded videos.tar to release $TAG"
