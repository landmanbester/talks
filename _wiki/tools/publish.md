---
type: Tool
title: Publish the site to GitHub Pages
description: Push to main → Actions renders and deploys; deck videos are untracked and come from the site-videos release.
tags: [publish, github-pages, videos, ci]
timestamp: 2026-10-26
---

# Publish the site to GitHub Pages

The site is published by `.github/workflows/publish.yml` on every push to `main` (or by hand:
Actions tab → *Publish site* → Run workflow). It renders the whole site with Quarto 1.10.18 on
GitHub's runner and deploys `_site/` with `actions/deploy-pages`, so there is no `gh-pages`
branch accumulating a copy of every render. URL: `https://landmanbester.github.io/talks/`, each
deck at `…/talks/<class>/<slug>/`. One-time setup: Settings → Pages → Source: "GitHub Actions".
Never run `quarto publish gh-pages` — it brings back the growing branch.

## Videos come from a release, not from git

Every deck's `videos/` is a gitignored symlink into `/data/talks/<class>/<slug>/videos`
([large data](../infrastructure/large-data.md)). Committing videos made the repo history grow by
a full copy on every re-render. The runner cannot see `/data`, so:

```bash
scripts/publish-videos.sh -n   # what would be uploaded (sizes per deck)
scripts/publish-videos.sh      # tar all */*/videos (symlinks followed) → release `site-videos`
```

The tarball replaces the previous one (`--clobber`); release assets do not count toward repo size
(2 GB per file). The workflow downloads and extracts it at the repo root before rendering.

**Order matters:** upload the videos *before* pushing a deck change that needs them. The workflow
greps every `videos/….mp4|webm|mov` reference in `lectures/*/*.qmd` and `contributions/*/*.qmd`
(including the generated `_<name>.qmd` segment includes) and fails with the missing paths rather
than publish a deck with blank slides; fix by running the script and re-running the workflow.

## Limits worth knowing

GitHub Pages: published site ≤ 1 GB, ~100 GB/month bandwidth (soft), deploy ≤ 10 min. At
720p30 a video-heavy deck is ~10–30 MB, so the site budget is dozens of such decks.

## What the runner does not have

Anything gitignored besides videos: `media`, `slides`, `fits_files`, `reference_pdfs/`, `*.pdf`.
A deck must only reference tracked files (images, CSS) and its `videos/` — never a path into
`media/` or `slides/`. No deck executes code cells; if one ever does, the workflow needs a Python
setup step.

**Mermaid hang:** the first run sat silently on the first deck with a Mermaid diagram until
cancelled. Quarto renders Mermaid through headless Chrome; locally it uses its own bundled
Chromium, on the runner it fell back to the system Chrome, which stalls on Ubuntu 24.04 (AppArmor
restricts the unprivileged user namespaces its sandbox needs). The workflow now lifts that
restriction and runs `quarto install chrome-headless-shell`, and the job has a 20-minute timeout.
