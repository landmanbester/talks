# Talks — Agent Context

> Entry point for AI coding agents. `CLAUDE.md` and `GEMINI.md` are symlinks to this file.
> It holds the always-on rules and routes to the wiki in `_wiki/`, which holds everything else.
> `README.md` is the human-facing guide.

## Project

Quarto revealjs presentations for technical talks at SARAO / Rhodes / AIMS South Africa. Decks are
written fresh or ported from Canva or Beamer, then refined until the slides look right. Prioritize
semantic structure, reproducible visualizations, and clean Markdown over pixel-perfect mimicry of
the original deck. Never recreate Canva's visual layouts with custom HTML/JS positioning hacks.

## Always-on rules

- **Two classes of deck.** `lectures/` (teaching, re-given, `date: today`, never a hard-coded date)
  and `contributions/` (given once, hard-coded event date). Each class directory has its own
  `AGENTS.md` — read it before authoring there. Create decks with the scaffold script
  (`python3 .agents/skills/quarto-revealjs/scripts/scaffold_talk.py lecture|contribution "Title"`)
- **Never prefix a talk directory with `_`** — the deck silently will not render
- **Nothing in front matter is enforced** — a deck with only a `title:` must render. Never add
  schema checks or validation
- **No inline HTML/CSS/JS for layout** — fenced divs and Quarto constructs only. The documented
  exceptions (raw `<video>` for muted autoplay, `{ojs}` cells, the manim-slides click cue) are in
  the wiki pages linked below
- **Words for the presenter go in `::: {.notes}`**, never on a slide
- **Large files live on `/data/talks/`**, symlinked into the repo; `/tmp` is RAM, so scratch goes in
  `/data/tmp/`. `.gitignore` patterns for these symlinks have no trailing slash
- **Measure, don't eyeball**: run `scripts/check_slides.py` on a deck before calling it done
- Repo structure at a glance: `templates/` (shared theme + title partial), `assets/logos/`,
  `scripts/` (tooling), `_animations/` (manim explainers), `_video/` (talk-video builds),
  `.agents/skills/` (skills), `_wiki/` (knowledge base), `docs/superpowers/` (past design specs)

## Before you… read

Open `_wiki/index.md` for the map; open only the pages a task needs.

| Before you… | Read |
|---|---|
| write or edit any deck front matter, create a deck, or add deck CSS | `_wiki/conventions/front-matter.md` |
| lay out slides, use fragments/columns/image swaps, notes, closing slide | `_wiki/conventions/slide-patterns.md` |
| write equations or MathJax macros | `_wiki/conventions/math.md` |
| style with theme classes, or want a new shared class | `_wiki/conventions/theme-classes.md` |
| add a Mermaid diagram | `_wiki/conventions/mermaid.md` |
| embed any video | `_wiki/techniques/embedding-video.md` |
| build annotations up on an image over several clicks (Canva-style builds) | `_wiki/techniques/build-up-figures.md` |
| add an interactive figure / sliders (`{ojs}`) | `_wiki/techniques/interactive-figures-ojs.md` |
| put an `_animations/` explainer in a deck, stepped on the clicker | `_wiki/techniques/manim-slides-stepping.md` |
| make a transparent manim clip for a slide | `_wiki/techniques/manim-slide-clips.md` |
| write or render an `_animations/` explainer video | `_wiki/techniques/explainer-videos.md`, `_wiki/gotchas/manim.md` |
| render, preview, publish, or screenshot a slide | `_wiki/tools/render.md` |
| check or fix overflow | `_wiki/tools/check-slides.md` |
| record narration / build a talk video | `_wiki/tools/talk-videos.md` |
| create or move large files, sync with Drive, touch recordings | `_wiki/infrastructure/large-data.md` |
| run Python tooling or manim | `_wiki/infrastructure/python-env.md` |
| hit something odd | `_wiki/gotchas/index.md` (symptom → fix) |
| port a deck or work on an existing one | `_wiki/decks/index.md` |
| need to know where something lives in the repo | `_wiki/infrastructure/repo-map.md` |

## Skills

Task-specific procedures live in `.agents/skills/<name>/SKILL.md`. Claude Code discovers them
automatically via the `.claude/skills` symlink; **other agents must read the `SKILL.md` themselves**
before starting the matching task — the file is the instruction set, not background reading.

| Task | Read |
|---|---|
| Create, port, render, or debug a deck | `.agents/skills/quarto-revealjs/SKILL.md` |
| Record / assemble a talk video from a deck | `.agents/skills/quarto-talk-video/SKILL.md` |
| Plan an explainer animation (before any code) | `.agents/skills/manim-composer/SKILL.md` |
| Write ManimCE code | `.agents/skills/manimce-best-practices/SKILL.md` |

Paths in a `SKILL.md` are relative to that skill's own directory, not to the repo root — the repo
also has a top-level `scripts/`, so always invoke a skill's helper by its full path
(`.agents/skills/quarto-talk-video/scripts/build_video.sh`).

Where a skill and this file or the wiki disagree, this file and the wiki win.

## Keeping the wiki current

The wiki is maintained by agents; the user reads it. When you learn a gotcha, settle a convention,
or add a technique, **update or add the page and a line in `_wiki/log.md` in the same commit**.
Format (Open Knowledge Format style): one concept per file; YAML front matter with `type`
(required: `Convention`, `Technique`, `Tool`, `Gotcha`, `Infrastructure`, `Deck`, `Index`, `Log`),
`title`, `description`, `tags`, `timestamp`; plain relative markdown links; list every page in its
directory's `index.md`. Add a row to `_wiki/gotchas/index.md` for any new symptom. If a new page
should be read before some task, add a row to the table above.

## Boundaries

- **Ask first** before cross-cutting structural changes: editing the shared theme
  (`templates/dark-academic.scss`), adding shared CSS/SCSS files, or repository-wide refactors
- **Never** run destructive commands (`rm -rf`, history rewrites) without explicit approval — and
  never delete anything under `_video/*/audio/raw/`, the only irreplaceable data in the repo
