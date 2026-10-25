---
type: Convention
title: Theme classes (dark-academic.scss)
description: CSS classes provided by the shared theme and when to use each.
tags: [authoring, theme, css]
timestamp: 2026-10-25
---

# Theme classes (`templates/dark-academic.scss`)

`templates/dark-academic.scss` is the canonical shared theme; `lectures.scss` and
`contributions.scss` layer on top. **Editing the shared theme, or adding shared CSS/SCSS files,
needs the user's approval first** (see Boundaries in `AGENTS.md`).

| Class | Use |
|---|---|
| `.highlight-box` | Key equations, definitions (blue border) |
| `.result-box` | Important results, theorems (green border) |
| `.muted` | Secondary notes, small print |
| `.small` | Explicit small text (0.7em) |
| `.closing-slide` | The final "Thanks!" slide |
| `.contact` | Monospace contact line on closing slide |
| `.overlay-caption` | Caption pill over a full-bleed background; tune `font-size` per deck |
| `.bottom-caption-slide` on heading | Full-bleed slide: hides the empty `##`, pins captions to the bottom |
| `.plain-figure` on heading | Hides the empty `##` so a figure gets the whole slide |
| `{.smaller}` on heading | Reduce entire slide font to ~70% |
| `{.incremental}` on list | Reveal list items one by one |

Palette shared by figures and animations: bg `#0d1117`, blue `#58a6ff`, amber `#d29922`,
green `#3fb950`, red `#f85149`.
