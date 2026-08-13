# Lectures — Agent Context

> Rules for teaching decks. `CLAUDE.md` and `GEMINI.md` are symlinks to this file.
> The repository-wide conventions in `../AGENTS.md` still apply — this file
> covers only what is specific to lectures.

## What a lecture is

Teaching material, revised and re-given. A lecture is never "finished"; it is
the current best version of an explanation. Optimise for the second delivery,
not the first.

## Front matter

`lectures/_metadata.yml` supplies theme, revealjs options, title background,
logos, author, and `date: today`. A lecture's own front matter carries only
what is specific to it:

- `title:` — the topic
- `institute:` — the course or host institution (e.g. `NASSP Radio Astronomy Course`)
- MathJax macro blocks, mermaid overrides, a different title background

**Never hard-code a date.** `date: today` is inherited and is correct: the deck
is presented whenever it is presented. A hard-coded date makes a re-given
lecture look stale. This is the opposite of the contributions rule.

Nothing is required beyond a title. A lecture with only `title:` renders and
inherits the full class theme.

## Style

Lectures are dense by design and are read from a seat, not the back of a hall.

- `{.smaller}` on the heading rather than a wrapping `{style=...}` div, which
  breaks `. . .` fragments
- `{.incremental}` lists to pace a derivation; build long derivations across
  several slides rather than shrinking one
- Full working is expected — a lecture that skips the algebra is a talk
- Directory names are topic slugs with no date: `deconvolution/`, not
  `2025-03-deconvolution/`

## Logos

The institutional strip is inherited from `_metadata.yml` and appears on the
title slide. Lectures do not add event logos. The strip is deliberately quiet
here — see `../templates/lectures.scss`.

Note `assets/logos/sarao_logo.jpg` is already a combined NRF + SARAO lockup, so
the inherited pair covers NRF, SARAO, and Rhodes.

## Citations

Optional. If a lecture cites sources, follow the pattern in
`../contributions/AGENTS.md`: a `references.bib` beside `index.qmd`, and an
explicit `## References` slide holding `::: {#refs}` placed *before* the
closing slide.

## Gotchas

- **Every deck needs a `custom.css`.** `css: custom.css` is hoisted into
  `_metadata.yml`, so a deck without that file fails to render.
- **Do not prefix a talk directory with `_`.** Quarto skips underscore-prefixed
  directories entirely — the deck will silently not render.
