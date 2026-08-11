# Splitting `talks/` into lectures and contributions

**Date:** 2026-08-11
**Status:** approved, ready for implementation planning

## Problem

The repository holds every presentation in a flat set of directories at the
root. Five of the six are lectures; one (`kremetart-pipeline`) is a conference
talk. The two kinds want different treatment:

- **Lectures** are re-given. They carry no fixed date and are branded with the
  standing institutional logos only.
- **Contributions** are conference and workshop talks. Each was given once, on a
  specific date, at a named event, and should carry that event's logo alongside
  the institutional ones.

With one flat namespace there is nowhere to hang those differences, so today
every deck repeats the same twelve lines of front matter and a single
`AGENTS.md` describes one set of rules for both kinds.

## Goals

1. Separate the two classes into `lectures/` and `contributions/` subtrees.
2. Give each class its own formatting layer and its own agent rules, applied
   automatically by location rather than by remembering.
3. Present both classes on the root index, with contributions dated and
   lectures not.
4. Preserve git history for every moved deck.

## Non-goals

- Retro-fitting logo strips onto the five existing lectures. The machinery
  ships; existing decks pick it up when next edited.
- Restyling any deck's content. This refactor relocates files, hoists shared
  configuration, and installs the class machinery.
- Sourcing the NRF logo. The slot is wired; the file arrives later.
- Migrating the theme to `_brand.yml` (see Considered and rejected).
- Alt-text/accessibility conventions and presenter/handout profile variants.
  Both are worthwhile; neither belongs in this change.

## Prerequisite: upgrade Quarto

The installed Quarto is **1.6.42**; the current release is **1.10.18**
(2026-07-24). The `quarto-authoring` skill consulted for this work is written
against **1.8.26**, so guidance already runs ahead of the binary.

The upgrade happens **before** the refactor, as its own commit, so that visual
regressions from the upgrade stay separable from regressions caused by the
split:

1. Upgrade to the current 1.10.x.
2. Render all six decks unchanged and screenshot each at 1600×900. Compare
   against the pre-upgrade renders; investigate any difference.
3. Re-run the two mechanism spikes below against the new binary.

Both mechanisms this design depends on are documented Quarto API rather than
incidental behaviour, so breakage is unlikely but must be confirmed:

- **`_metadata.yml` path resolution.** Verified on 1.6.42: relative paths in a
  directory's `_metadata.yml` resolve from the *document*, not the metadata
  file, so `../../templates/…` works from `lectures/<slug>/index.qmd`.
- **The `title-slide.html` template partial.** Documented by Quarto as a
  supported way to "replace the default title slide entirely with your own
  template". Verified on 1.6.42 to emit the logo strip with correctly rewritten
  asset paths.

## Layout

```
talks/
├── AGENTS.md ← CLAUDE.md          # shared conventions only
├── _quarto.yml                    # render "*/*/index.qmd"; resources: assets/logos/**
├── index.qmd                      # two listings, one per class
├── templates/
│   ├── dark-academic.scss         # canonical base + new .logo-strip rule
│   ├── lectures.scss              # thin per-class layer
│   ├── contributions.scss         # thin per-class layer
│   └── title-slide.html           # shared pandoc partial rendering the logo strip
├── assets/logos/                  # + nrf.png slot (file absent for now)
├── lectures/
│   ├── AGENTS.md ← CLAUDE.md
│   ├── _metadata.yml
│   ├── aperture-synthesis-imaging/
│   ├── covariance-toeplitz/
│   ├── cultcargo-fundamentals/
│   ├── deconvolution/
│   └── stimela-fundamentals/
├── contributions/
│   ├── AGENTS.md ← CLAUDE.md
│   ├── _metadata.yml
│   └── kremetart-pipeline/
├── _animations/                   # unchanged, stays at root
└── reference_pdfs/                # unchanged, stays at root
```

`_animations/` and `reference_pdfs/` feed either class, so they stay at the
root. Talk directories move with `git mv` to preserve history.

Directory naming keeps the existing convention in both classes: descriptive
slugs with no date prefix. A contribution's date lives in its front matter.

## Mechanism: one `_metadata.yml` per class

Quarto merges a directory's `_metadata.yml` into every document beneath it, and
resolves relative paths in that file **from the document**, not from the
metadata file. This was verified experimentally against Quarto 1.6.42: a
`lectures/_metadata.yml` declaring `theme: [dark, ../../templates/probe.scss]`
compiled the probe SCSS into `lectures/demo/index.qmd`'s output.

This makes the class boundary a single file per class rather than an edit to
every deck.

`lectures/_metadata.yml`:

```yaml
author: "Landman Bester"
date: today
format:
  revealjs:
    theme: [dark, ../../templates/dark-academic.scss, ../../templates/lectures.scss]
    template-partials: [../../templates/title-slide.html]
    slide-number: true
    code-line-numbers: false
    code-copy: true
    highlight-style: monokai
    center: true
    transition: slide
    mermaid-format: svg
    css: custom.css
    title-slide-attributes:
      data-background-image: images/meerkat-milkyway.jpg
      data-background-opacity: "0.5"
logos:
  # - /assets/logos/nrf.png     # uncomment once the file exists — see Open items
  - /assets/logos/sarao_logo.jpg
  - /assets/logos/rhodes_banner.jpg
```

`contributions/_metadata.yml` has the same shape with two differences:
`contributions.scss` replaces `lectures.scss`, and there is **no `date:` key** —
each contribution supplies its own.

Per-document front matter takes precedence over `_metadata.yml`, so existing
per-deck overrides survive untouched: `deconvolution`'s
`meerkat-dish-night.jpg` background and its `mermaid: theme: dark`, and the
MathJax macro blocks in `deconvolution` and `covariance-toeplitz`.

Each deck's front matter then shrinks to what is genuinely specific to it:
title, subtitle, institute, macros, and overrides.

### Two prerequisites this forces

1. `covariance-toeplitz/` and `deconvolution/` have no `custom.css`. The hoisted
   `css: custom.css` would fail for them, so both get the standard
   scrollbar-fix file:
   `.reveal div.sourceCode { overflow-x: hidden !important; }`
2. `covariance-toeplitz/covariance-toeplitz.qmd` is a stale duplicate of that
   deck's `index.qmd`. It is not rendered today; under the new glob it would
   remain unrendered, but it is dead weight that will drift. Delete it.

## Front matter contract

| Field | Lectures | Contributions |
|---|---|---|
| `date` | `today`, never hard-coded | hard-coded date of the event |
| `institute` | course or host institution | own affiliation, e.g. `SARAO / Rhodes` |
| `event` | — | **required**: conference or workshop name |
| `location` | — | **required**: city, country |
| `logos` | inherited institutional set | inherited institutional set **plus** event logos |
| `bibliography` | optional | **required** — see Citations |

The "never hard-code dates" rule that currently applies repo-wide becomes
lecture-scoped. Contributions invert it: the date is the point.

## Citations and bibliography

No deck in the repository currently uses `bibliography:` or a single `[@cite]`.
For conference contributions this is a genuine gap: inline attribution and a
closing references slide are expected of academic talks.

Contributions carry a `references.bib` beside `index.qmd` and declare it in
front matter:

```yaml
bibliography: references.bib
csl: ../../templates/aas.csl      # optional; omit for Chicago default
```

Citations use standard Pandoc syntax — `@smith2020` in text,
`[@smith2020; @jones2021]` parenthetical, `[-@smith2020]` to suppress the
author. Quarto places the bibliography at the end of the document, which on
revealjs means a final slide; give it an explicit home so it does not land
after the closing slide:

```markdown
## References {.smaller}

::: {#refs}
:::

## Thanks! {background-color="#0d1117" .closing-slide}
```

Lectures may use the same machinery but are not required to.

## Presenter features

Neither speaker notes nor presenter view is mentioned in the current
`AGENTS.md`, though both are standard revealjs and both matter for a live
conference talk. Contributions document them as expected practice:

- `::: {.notes}` blocks for speaker notes, visible only in presenter view
  (press `S`).
- Presenter view and the chalkboard/pointer plugins as delivery aids.

Speaker notes are the reason a contribution's `.qmd` remains the single source
of truth for the talk: the narration lives with the slide it belongs to.

## Logo strip

### Title slide

`templates/title-slide.html` is a pandoc partial overriding Quarto's default
title slide. It renders the standard title block and appends a strip built by
iterating the `logos:` metadata list:

```html
$if(logos)$<div class="logo-strip">$for(logos)$<img src="$logos$" alt="" />$endfor$</div>$endif$
```

Verified experimentally: the partial emitted
`<div class="logo-strip"><img src="../../assets/logos/sarao_logo.jpg" alt="">…`,
with Quarto rewriting the project-root-relative `/assets/…` paths to correct
document-relative ones and copying the files into `_site/assets/logos/`.

The copy depends on declaring the assets as project resources in the root
`_quarto.yml`:

```yaml
project:
  type: website
  render:
    - index.qmd
    - "*/*/index.qmd"
  resources:
    - assets/logos/**
```

One partial serves both classes; the class SCSS layers size the strip
differently. An entry pointing at a file that does not exist yields a broken
image on the title slide, so the `logos:` lists ship with only the logos that
exist — see Open items.

### Closing slide

The closing slide is slide body content, so it uses native fenced divs rather
than inline HTML, per the existing repo rule:

```markdown
## Thanks! {background-color="#0d1117" .closing-slide}

::: {.contact}
landman.bester@gmail.com
:::

::: {.logo-strip}
![](/assets/logos/sarao_logo.jpg)
![](/assets/logos/rhodes_banner.jpg)
:::
```

Both classes may use this; it is documented as expected practice for
contributions, where the final slide stays on screen during questions.

### Shared theme change

`.logo-strip` is added to `templates/dark-academic.scss` as the base rule —
horizontal flex row, centred, gapped, with a sensible default logo height and
`max-width: 100%`. The two class layers override scale only:

- `lectures.scss` — smaller, lower-emphasis strip.
- `contributions.scss` — larger strip with room for event logos.

Editing the shared theme was explicitly approved for this change.

## Root index

Two listings on one page:

```yaml
listing:
  - id: contributions
    contents: contributions/*/index.qmd
    type: table
    fields: [date, title, event, institute]
    sort: "date desc"
  - id: lectures
    contents: lectures/*/index.qmd
    type: table
    fields: [title, institute]
    sort: "title"
```

Rendered under `## Contributions` and `## Lectures` headings, each followed by
a `::: {#contributions}` / `::: {#lectures}` div. Contributions sort
most-recent-first; lectures sort alphabetically, since they carry no meaningful
date.

## Agent rules

The root `AGENTS.md` retains everything shared: the manim workflow, mermaid
conventions, theme classes, the render and headless-screenshot loop, overflow
fixes, and boundaries. Its directory-structure section is rewritten for the new
tree. The date rule and the title-slide conventions move out of it into the
class files.

`lectures/AGENTS.md`:

- `date: today` — never hard-code
- base logos only; no `event`/`location` metadata
- dense-slide conventions: `{.smaller}` on headings, incremental lists, heavy
  math and derivations are expected
- `institute` names the course or host institution
- citations optional; if used, follow the contributions pattern

`contributions/AGENTS.md`:

- `date:` is the hard-coded date of the event
- `event:` and `location:` are required
- logos on both the title slide and the closing slide
- event logos are appended to the inherited institutional set
- slide budget tied to the talk's time slot; conference talks are short, so
  prefer splitting over shrinking
- `bibliography: references.bib` required, with an explicit `## References`
  slide placed before the closing slide
- speaker notes in `::: {.notes}` blocks; presenter view and chalkboard
  documented as delivery aids

Each file gets a `CLAUDE.md` symlink beside it, matching the root convention.
Claude Code loads a nested `CLAUDE.md` automatically when working in that
subtree, so the correct rules apply by location without being requested.

## Supporting updates

- `.claude/skills/quarto-revealjs/scripts/scaffold_talk.py` takes a required
  class argument (`lecture` | `contribution`), creates the directory in the
  right subtree, and writes class-appropriate front matter — thinner now, since
  `_metadata.yml` carries the shared block, and with `event`/`location` stubs
  for contributions.
- `.claude/skills/quarto-revealjs/references/scaffolding.md` documents the new
  argument and the two-class layout.
- `README.md` layout and command sections are updated. Preview URLs gain a path
  segment: `http://localhost:PORT/lectures/<slug>/`.
- `.gitignore` needs no change. Its patterns are either unanchored or anchored
  to paths that do not move, and `!templates/*.html` already un-ignores the new
  title-slide partial.
- The root `AGENTS.md` gains a pointer to the `quarto-authoring` skill for
  citations, cross-references, and conditional content, noting that the skill
  targets Quarto 1.8.26 — accurate only once the upgrade lands.
- `contributions/AGENTS.md` should be created with the `skill-creator`
  conventions in mind if the scaffolding later splits into per-class skills;
  that split is deliberately deferred until the two rule sets have settled.

## Considered and rejected: `_brand.yml`

Quarto's `_brand.yml` is the official mechanism for exactly this problem —
consistent colors, typography, and logos across a project — and it supports
revealjs. It was evaluated rather than assumed away.

Findings, tested against the installed 1.6.42:

- Brand colors **do** apply to revealjs on 1.6.42; the palette compiled into the
  generated theme CSS.
- The schema has since moved. `logo: path.jpg` is rejected on 1.6.42
  (`Brand validation failed … location logo`); `logo: {medium: path}` is
  accepted. Current documentation describes the newer form.
- Quarto 1.8 added light/dark logo variants, `brand-mode: dark` for revealjs,
  and brand extensions for sharing brand assets across projects.

Rejected because it does not fit the requirement. brand.yml expresses colors,
typography, and a *single* logo; the requirement here is a strip of three to
five logos, which would still have to be hand-rolled. The decks are dark-only,
so light/dark support buys nothing. Adopting it would mean rewriting a mature
`dark-academic.scss` for features this project does not use.

Worth revisiting if the collection ever needs light-mode output or a shared
brand across separate repositories.

## Verification

0. Pre-refactor, post-upgrade: all six decks render unchanged and screenshot
   clean under the new Quarto; both mechanism spikes re-confirmed.
1. `quarto render` from the root completes with all six decks built.
2. `_site/assets/logos/` is populated.
3. The root index shows two tables: one dated contribution, five undated
   lectures, all titles and venues populated.
4. One deck per class screenshotted at 1600×900 via headless Chrome to confirm
   the title-slide partial did not disturb the layout.
5. `git log --follow` on a moved deck's `index.qmd` shows history across the
   move.

## Open items

- **NRF logo.** `assets/logos/nrf.png` does not exist. Until it is added, the
  `logos:` lists in both `_metadata.yml` files must omit that entry, or the
  title slide will show a broken image. Implementation should ship the lists
  with the two logos that exist and leave the `nrf.png` line commented out with
  a note.
