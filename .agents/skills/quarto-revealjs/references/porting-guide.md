# Porting Guide: Canva / PDF / PPTX → Quarto Revealjs

## General Strategy

There is no automated conversion from Canva, PDF, or PowerPoint to Quarto `.qmd`. The port is manual but follows a predictable pattern. The goal is to extract *content* (text, math, code, structure) and recreate *design* using Quarto's native features and SCSS theming.

## Step-by-Step Process

### Step 0: Inventory a Canva PDF Export Efficiently

Canva exports **one PDF page per animation build**, so an 88-page PDF typically collapses to ~25 unique slides. Inventory it with contact sheets instead of reading pages one by one:

```bash
pdfinfo deck.pdf                          # page count, page size
pdftotext -layout deck.pdf /tmp/deck.txt  # text inventory (math/figures will be missing — they are images)
mkdir -p /tmp/pages && pdftoppm -png -r 50 deck.pdf /tmp/pages/page
cd /tmp/pages && for i in $(seq 0 9); do
  montage page-{...}.png -tile 3x3 -geometry +5+5 -label "%f" -background gray20 -fill white /tmp/sheet-$i.png
done
```

Read the sheets to map page ranges → unique slides. Port the **final build** of each group and recreate the build steps as fragments.

**Extracting figures**: render the needed pages at 150 dpi (`pdftoppm -png -r 150 -f N -l N`) and crop with ImageMagick using fractions of the page size. Verify all crops at once with a labelled montage, then iterate on the bad ones:

```bash
convert pN.png -crop ${W}x${H}+${X}+${Y} +repage images/figure.png
montage images/*.png -tile 4x -geometry 280x158+4+4 -label "%f" /tmp/check.png
```

- Earlier build pages often contain a figure **without** the text overlays that later builds add — crop from those instead of fighting the overlap
- An overlapping element on a white-background diagram can be painted out: `-fill white -draw "rectangle x1,y1 x2,y2"`
- `pdfimages` can pull original embedded rasters, but matching images/smasks to slides across duplicated build pages is fiddly — page-render cropping is usually faster and good enough
- **Embedded video links are NOT preserved** by Canva's PDF export (no `/URI` annotations — verify with `mutool clean -d deck.pdf out.pdf && grep -ao '/URI *([^)]*)' out.pdf`). Ask the user for the URLs

### Step 1: Extract Content Inventory

Go through the source presentation slide by slide and catalog:

- **Text content**: Headings, bullet points, prose
- **Math**: Equations (note: in Canva these may be rendered as images)
- **Code**: Any code snippets (often screenshots in Canva)
- **Images**: Diagrams, photos, logos — export as PNG or SVG from source
- **Videos**: Note any embedded YouTube links
- **Animations**: Which slides use progressive reveal / click-to-show
- **Layout**: Which slides use multi-column, full-bleed images, etc.

### Step 2: Retypeset Math

This is where Quarto massively improves on Canva. Canva's LaTeX rendering is limited and often uses images. In Quarto:

- Rewrite all equations as proper LaTeX in `$...$` or `$$...$$`
- Use `\begin{aligned}` for multi-line derivations
- Use `\color{...}` for colored equation elements (replacing Canva's colored text)
- Define macros in YAML front matter for frequently used symbols

**Common Canva → LaTeX translations:**

| Canva element | Quarto equivalent |
|---|---|
| LaTeX image/plugin | Native `$$...$$` |
| Colored text in equation | `\color{green}{R}` inside `$$` |
| Equation with annotations | Fragment reveal + colored math |
| Matrix display | `\begin{bmatrix}...\end{bmatrix}` |

### Step 3: Convert Animations to Fragments

Canva's click-to-reveal maps directly to Quarto's progressive reveal:

| Canva animation | Quarto equivalent |
|---|---|
| Element appears on click | `. . .` pause or `::: {.fragment}` |
| Sequence of reveals on same slide | Multiple `. . .` separators |
| Highlight on click | `::: {.fragment .highlight-red}` |
| Annotation callout appears | `::: {.fragment .fade-in}` |

**Example**: Canva slides 35-42 in the Covariance talk show the measurement model with progressive annotation (DATA → NOISE → SIGNAL → MEASUREMENT OPERATOR → likelihood → prior → evidence). In Quarto:

```markdown
## Linear + Gaussian Noise

The measurement model:

$$y = Rx + \epsilon, \quad \epsilon \sim \mathcal{N}(0, \Sigma)$$

. . .

Gives rise to a likelihood:

$$p(y|x) = \frac{1}{\sqrt{(2\pi)^n|\Sigma|}}
\exp\!\left(-\frac{1}{2}(y - Rx)^\dagger \Sigma^{-1}(y - Rx)\right)$$

. . .

Can solve analytically when the prior is Gaussian: $p(x) = \mathcal{N}(m, K)$

. . .

Can even use the evidence to adapt the prior to the problem!
```

### Step 4: Handle Images and Diagrams

**Export from Canva**: Use Canva's download feature to export individual pages or elements as PNG (raster) or SVG (vector). For diagrams you created in Canva's editor, SVG is preferred.

**Recreate simple diagrams**: For simple diagrams (flowcharts, block diagrams), consider recreating them as Mermaid diagrams in Quarto — they'll be resolution-independent and editable.

**Background images**: Canva slides with full-bleed background photos become:
```markdown
## {background-image="images/photo.jpg" background-opacity="0.4"}
```

### Step 5: Recreate Layout

| Canva layout | Quarto equivalent |
|---|---|
| Side-by-side elements | `:::: {.columns}` with `width` |
| Centered single element | Default behavior (with `center: true`) |
| Logos in corners | `logo:` in YAML or `::: {.absolute}` |
| Footer text | Drop it — the repo omits footers |
| Full-screen image | `{background-image=...}` |
| Overlapping elements | `::: {.absolute top=X left=Y}` |

### Step 6: Apply Theme

Replace Canva's visual design with the SCSS theme. The theme handles:
- Background colors and gradients
- Heading fonts and colors
- Code block styling
- Math block styling
- Callout box appearance

You will NOT get pixel-perfect reproduction of Canva's design. That's okay — the goal is a presentation that looks professional and is *maintainable*.

## What You Gain

- **Editable math**: No more re-rendering equation images
- **Version control**: Plain text `.qmd` files work with git
- **Executable code**: Code blocks can actually run and show output
- **Consistent styling**: SCSS theme applies everywhere automatically
- **Multiple outputs**: Same source → HTML slides, PDF, beamer
- **Speaker notes**: Proper presenter view with notes
- **Searchable**: All text is actual text, not images

## What You Lose

- **Drag-and-drop design**: No WYSIWYG editor
- **Fancy animations**: Canva has richer animation options
- **Stock assets**: Canva's image/icon library
- **Collaboration UI**: Canva's sharing and commenting
- **Exact layout control**: CSS positioning is less intuitive than drag-and-drop

## Tips for a Smooth Port

1. Port one talk at a time. Start with a math-heavy one where Quarto's advantages are most obvious.
2. Don't try to replicate Canva's exact visual design. Adopt a Quarto-native aesthetic.
3. Keep Canva images as PNG exports for complex graphics you can't easily recreate.
4. Use the dark theme — it looks good on projectors and gives presentations a modern, polished feel.
5. Build up a library of reusable slide patterns (equation reveal, code demo, etc.) that you can copy between talks.
