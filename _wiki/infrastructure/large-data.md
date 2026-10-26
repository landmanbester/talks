---
type: Infrastructure
title: Large data, scratch space and Drive sync
description: Where big files live (/data/talks symlinks, including deck videos), /tmp is RAM, Drive sync with sync-data.sh, irreplaceable raw takes.
tags: [data, storage, backup]
timestamp: 2026-10-25
---

# Large data, scratch space and Drive sync

The machine's main drive is small; large files live on `/data/talks/` and are symlinked into the
repo, so scripts see ordinary paths:

| Repo path | What |
|---|---|
| `fits_files` | FITS images for `scripts/figures/` |
| `_video/<slug>/audio` | Narration takes and every processed stage |
| `_animations/<video>/media`, `<deck>/media` | manim render output and caches |
| `<deck>/slides` | manim-slides render output (segments + JSON) |
| `<deck>/videos` | Every video a deck plays: manim-slides segments, webm clips, footage |

Put new large inputs or outputs under `/data/talks/` and symlink them in the same way. `/tmp` is
RAM on this machine — scratch output bigger than a few screenshots goes in `/data/tmp/`. The
`.gitignore` patterns for these have **no trailing slash** on purpose — `dir/` only matches real
directories, not symlinks.

A deck's `videos/` is the one store the published site needs. It is not in git (the history only
grows with every re-render), so before a deck change that adds or replaces a video reaches `main`,
upload the set with `scripts/publish-videos.sh` — see [publish](../tools/publish.md). A new deck
that plays videos: `mkdir -p /data/talks/<class>/<slug>/videos` and symlink it in as `videos`
before writing into it (`manim_slides_qmd.py` warns if `videos/` is a real directory). `reference_pdfs/` (Canva PDF exports to port from) is gitignored too.

## Google Drive copy

`/data/talks/` has a Google Drive copy, kept in step by hand with `scripts/sync-data.sh` (rclone
remote `talks-drive:`; the folder ID lives in the rclone config, not in the repo). Transfers are by
MD5, so an unchanged file never moves:

```bash
scripts/sync-data.sh status       # what differs
scripts/sync-data.sh push -n      # dry run, then without -n: local → Drive
scripts/sync-data.sh pull         # fresh clone / other machine: fetch, then symlink into the repo
```

Push mirrors, but anything it would delete or overwrite on Drive is moved to `_deleted/<time>/`
there instead. Pull only fetches files missing locally. manim `media/` is not synced.

## The one irreplaceable thing

**`_video/<slug>/audio/raw/` is the only irreplaceable thing in the repo** — every other stage and
artifact is rebuilt from tracked source. Never delete anything under it. After any recording
session run `scripts/sync-data.sh push` and `scripts/backup-takes.sh` (a second local copy in
`~/backups/talks-takes`, on the other disk).
