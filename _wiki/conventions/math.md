---
type: Convention
title: Math (MathJax)
description: MathJax macro syntax and LaTeX the bundled MathJax cannot render, with substitutes.
tags: [authoring, math, mathjax]
timestamp: 2026-10-25
---

# Math (MathJax)

- **MathJax macros** use MathJax 2 syntax: `TeX: { Macros: {} }` (uppercase — not
  `tex: { macros: }`), injected via `include-in-header`
- **Unsupported LaTeX**: the bundled MathJax cannot load `\cancel` (renders red or
  `[Math Processing Error]`) and has no mathtools commands like `\xleftrightarrow`. Substitutes:
  `\underbrace{w_{pq}(n-1)}_{\approx\, 0}` for striking out a term,
  `\overset{\mathcal{F}}{\longleftrightarrow}` for a labelled arrow
