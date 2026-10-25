---
type: Convention
title: Mermaid diagrams
description: How to size and style Mermaid diagrams for the dark theme; label rules that avoid parser errors.
tags: [authoring, mermaid, diagrams]
timestamp: 2026-10-25
---

# Mermaid diagrams

Translate pipelines, architectures, and systems into Mermaid. Unstyled Mermaid looks bare on dark
slides — always style it. `mermaid-format: svg` is inherited from `_metadata.yml` (the default `js`
format overrides custom themes).

- Configure with a **YAML config block inside the cell** (not `%%{init:...}%%`), `theme: base`, and
  `themeVariables` matching the dark-academic palette
- **Always set both `%%| fig-width:` and `%%| fig-height:`** — without a height the SVG container
  reserves far more vertical space than the diagram needs and pushes content off the slide (a 4-node
  `flowchart LR` wants `fig-width: 9`, `fig-height: 1.8`). Too wide a `fig-width` adds a scrollbar
- The first line after the config declares the diagram type (`flowchart TD`, `sequenceDiagram`)
- **No quotation marks or parentheses** inside node labels — they break the parser
- `<br />` for line breaks in labels (not `\n`); `&nbsp;` padding for wider nodes
- Start labels with a Unicode emoji for meaning (`📡 Array`, `📦 CABS`, `⚙️ Stimela`)
