# PDF Export for Quarto Revealjs

## Method 1: Print to PDF (Recommended for revealjs)

Quarto can export revealjs slides to PDF using a headless Chromium browser.

### Setup
```bash
# Install Chromium (if not already present)
# On Ubuntu/Debian:
sudo apt install chromium-browser

# Or let Quarto handle it:
quarto install chromium
```

### Export
```bash
# Append ?print-pdf to the URL and use quarto's built-in export
quarto render index.qmd
# Then open in browser and print to PDF, or:

# Direct PDF export (requires chromium)
quarto render index.qmd --to revealjs
# Then use decktape:
npx decktape reveal index.html output.pdf
```

### Using decktape (most reliable)
```bash
# Install decktape
npm install -g decktape

# Export (after rendering HTML first)
quarto render index.qmd
decktape reveal index.html slides.pdf

# With options
decktape reveal --size 1920x1080 index.html slides.pdf
```

## Method 2: Beamer (Native LaTeX PDF)

For direct PDF output without a browser, use Quarto's beamer format. This uses LaTeX to produce PDF slides natively.

### Setup
```bash
# Install TinyTeX (lightweight LaTeX distribution)
quarto install tinytex
```

### Single-format beamer
```yaml
---
title: "Talk Title"
format:
  beamer:
    theme: metropolis
    aspectratio: 169
    fontsize: 12pt
---
```

### Dual-format (revealjs + beamer from same source)
```yaml
---
title: "Talk Title"
format:
  revealjs:
    theme: [dark, custom.scss]
  beamer:
    theme: metropolis
    aspectratio: 169
---
```

Then render selectively:
```bash
quarto render index.qmd --to revealjs   # HTML slides
quarto render index.qmd --to beamer     # PDF slides
```

### Beamer caveats
- Fragments (`. . .`) work but map to beamer overlays — the behavior is slightly different
- Two-column layouts work via `:::: {.columns}`
- Custom SCSS has no effect — beamer uses its own LaTeX themes
- Mermaid diagrams require extra setup (rendered as images)
- Some HTML-specific features (absolute positioning, background images) won't work

## Method 3: Self-Contained HTML (Alternative to PDF)

If PDF quality isn't critical, a self-contained HTML file is often a better sharing format:

```yaml
format:
  revealjs:
    embed-resources: true
```

This bundles all CSS, JS, images, and fonts into a single `.html` file that opens in any browser. Advantages: animations work, code highlighting is preserved, math renders at full quality.

## Choosing a Method

| Need | Method |
|------|--------|
| Best visual fidelity to HTML slides | decktape |
| Native PDF with LaTeX quality math | beamer |
| Quick sharing, don't need PDF | embed-resources HTML |
| Conference submission (PDF required) | beamer with metropolis theme |
| Handout with multiple fragments per page | beamer with `handout` option |

## Fragment Handling in PDF

By default, fragments are collapsed (all visible) in PDF. To get one PDF page per fragment state:

```yaml
format:
  revealjs:
    pdf-separate-fragments: true
```

For beamer, use the `handout` class option to collapse overlays:
```yaml
format:
  beamer:
    classoption: handout
```
