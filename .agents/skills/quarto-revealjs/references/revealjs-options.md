# Revealjs YAML Options Reference

Complete reference for the most useful `format: revealjs:` options in Quarto front matter.

---

## Appearance

```yaml
format:
  revealjs:
    theme: [dark, custom.scss]    # Built-in + custom SCSS overlay
    highlight-style: monokai      # Code syntax theme
    slide-number: true            # Show slide numbers
    show-slide-number: all        # all | print | speaker
    code-line-numbers: false      # Line numbers in code blocks
    code-copy: true               # Copy button on code blocks
    smaller: false                # Smaller default font
    scrollable: false             # Allow scrolling on overflow
    center: true                  # Vertically center content
    hash-type: number             # URL hash style
    width: 1920                   # Slide width in pixels
    height: 1080                  # Slide height in pixels
    margin: 0.1                   # Content margin (fraction)
```

## Built-in Themes

Available values for `theme:`: `beige`, `blood`, `dark`, `default`, `league`, `moon`, `night`, `serif`, `simple`, `sky`, `solarized`.

You can layer a custom SCSS on top: `theme: [dark, my-overrides.scss]`

## Navigation & Controls

```yaml
format:
  revealjs:
    controls: true               # Arrow controls in corner
    controls-layout: bottom-right
    controls-tutorial: true      # Bounce arrows on first slide
    progress: true               # Progress bar at bottom
    history: true                # Push each slide to browser history
    keyboard: true               # Keyboard navigation
    touch: true                  # Touch navigation
    loop: false                  # Loop back to first slide
    navigation-mode: default     # default | linear | grid
```

## Branding & Layout

```yaml
format:
  revealjs:
    logo: images/logo.png         # Logo image (bottom-right by default)
    footer: "SARAO | AI4RI 2025"  # Footer text (not used in this repo)
    css: custom.css               # Additional CSS
    title-slide-attributes:
      data-background-image: images/bg.jpg
      data-background-opacity: "0.5"
      data-background-color: "#1a1a2e"
```

## Code Display

```yaml
format:
  revealjs:
    code-fold: false             # Collapsible code blocks
    code-summary: "Show code"    # Label for collapsed code
    code-overflow: wrap          # wrap | scroll
    code-line-numbers: false
    code-copy: true
    code-tools: false            # Source code display toggle
    highlight-style: monokai     # See below for options
```

Available `highlight-style` values: `a11y`, `arrow`, `atom-one`, `ayu`, `breeze`, `github`, `gruvbox`, `monokai`, `nord`, `oblivion`, `printing`, `radical`, `solarized`, `vim-dark`, `zenburn`.

## Transitions

```yaml
format:
  revealjs:
    transition: slide            # none | fade | slide | convex | concave | zoom
    transition-speed: default    # default | fast | slow
    background-transition: fade  # Same options as transition
```

Per-slide override: `## Title {transition="zoom"}`

## Math

```yaml
format:
  revealjs:
    html-math-method: mathjax    # mathjax | katex | webtex
    # MathJax config:
    include-in-header:
      text: |
        <script>
        MathJax = {
          tex: {
            tags: 'ams',
            macros: {
              R: "{\\mathbb{R}}",
              bm: ["{\\boldsymbol{#1}}", 1]
            }
          }
        };
        </script>
```

## Printing & Export

```yaml
format:
  revealjs:
    print-pdf: true              # Enable PDF print stylesheet
    pdf-separate-fragments: false # Each fragment = separate PDF page
    pdf-max-pages-per-slide: 1
```

## Multiplex / Presenter Mode

- Press `S` during presentation to open speaker notes view
- Press `F` for fullscreen
- Press `O` for overview mode
- Press `B` or `.` to blank the screen

## Embed Resources (self-contained HTML)

```yaml
format:
  revealjs:
    embed-resources: true        # Bundle all assets into single HTML
    self-contained: true         # Alias for embed-resources
```

Useful for sharing a single HTML file that works offline.

## Multiple Formats

You can render to both revealjs and beamer from the same source:

```yaml
format:
  revealjs:
    theme: dark
  beamer:
    theme: metropolis
    aspectratio: 169
```

Then: `quarto render index.qmd --to revealjs` or `quarto render index.qmd --to beamer`

## Freeze (for reproducible executable code)

```yaml
execute:
  freeze: auto                   # Don't re-run unchanged code
  cache: true                    # Cache execution results
```
