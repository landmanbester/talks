# Common Patterns for Quarto Revealjs

A reference catalog of patterns for technical presentations. Organized by use case.

## Table of Contents

1. [Math Typesetting](#math-typesetting)
2. [Code Blocks](#code-blocks)
3. [Progressive Reveal & Animation](#progressive-reveal--animation)
4. [Layout](#layout)
5. [Media & Figures](#media--figures)
6. [Callouts & Exercises](#callouts--exercises)
7. [Matrices & Tables](#matrices--tables)
8. [Background Customization](#background-customization)
9. [Custom Div Classes](#custom-div-classes)
10. [Mermaid Diagrams](#mermaid-diagrams)

---

## Math Typesetting

Quarto uses MathJax for HTML output and native LaTeX for PDF/beamer. Both `$...$` (inline) and `$$...$$` (display) work.

### Inline math
```markdown
The Toeplitz property requires $T_{i,j} = T_{i-1,j-1}$ for all $i,j > 1$.
```

### Display math
```markdown
$$
X(\nu) = \int_{-\infty}^{\infty} x(t) e^{-2\pi \imath \nu t} \, dt
$$
```

### Aligned equations
```markdown
$$
\begin{aligned}
P(s) &= \int K(r) \exp(-2\pi \imath s \cdot r) \, dr \\
S(s, s') &\propto \delta(s - s') P(s)
\end{aligned}
$$
```

### Colored math (using \color)
```markdown
$$
p(y|x) = \frac{1}{\sqrt{(2\pi)^n |\Sigma|}} \exp\left(
  -\frac{1}{2} (y - {\color{green}R}{\color{cyan}x})^\dagger
  \Sigma^{-1} (y - {\color{green}R}{\color{cyan}x})
\right)
$$
```

### Matrices
```markdown
$$
T = \begin{bmatrix}
a & b & c & d & e \\
f & a & b & c & d \\
g & f & a & b & c \\
h & g & f & a & b \\
i & h & g & f & a
\end{bmatrix}
$$
```

### Math with fragment reveal
```markdown
$$
y = Rx + \epsilon
$$

::: {.fragment}
$$\epsilon \sim \mathcal{N}(0, \Sigma)$$
:::

::: {.fragment}
$$
p(y|x) = \frac{1}{\sqrt{(2\pi)^n|\Sigma|}}
\exp\!\left(-\frac{1}{2}(y - Rx)^\dagger \Sigma^{-1}(y - Rx)\right)
$$
:::
```

### Custom LaTeX macros (define once in YAML)

**Important:** Use MathJax 2 syntax with uppercase keys (`TeX`, `Macros`), not lowercase (`tex`, `macros`).

```yaml
format:
  revealjs:
    include-in-header:
      text: |
        <script>
        MathJax = {
          TeX: {
            Macros: {
              bm: ["{\\boldsymbol{#1}}", 1],
              R: "{\\mathbb{R}}",
              E: "{\\mathbb{E}}",
              Fourier: "{\\mathcal{F}}"
            }
          }
        };
        </script>
```

Then use: `$\Fourier[x(t)](s)$`, `$\bm{c} = [c_0, \ldots, c_{N-1}]$`

---

## Code Blocks

### Static (syntax-highlighted, not executed)
````markdown
```python
import jax.numpy as jnp
from jax import jit, vmap

@jit
def circulant_matvec(c, x):
    """Circulant matrix-vector product via FFT."""
    C_hat = jnp.fft.fft(c)
    x_hat = jnp.fft.fft(x)
    return jnp.fft.ifft(C_hat * x_hat).real
```
````

### Executable (requires Jupyter)
````markdown
```{python}
#| echo: true
#| eval: true
#| output-location: fragment
import numpy as np
c = np.array([1, 2, 3, 4, 5])
print(f"Eigenvalues: {np.fft.fft(c)}")
```
````

### Code with line highlighting
````markdown
```{.python code-line-numbers="3-5"}
def toeplitz_embed(row, col):
    n = len(row)
    # Circulant embedding: concatenate row and reversed column
    first_col = np.concatenate([col, [0], row[-1:0:-1]])
    return first_col
```
````

### Code with filename tab
````markdown
```{.python filename="toeplitz.py"}
from scipy.linalg import toeplitz
T = toeplitz([1, 2, 3, 4], [1, 5, 6, 7])
```
````

### Side-by-side code + output
````markdown
:::: {.columns}
::: {.column width="55%"}
```{python}
#| echo: true
#| eval: true
import numpy as np
P = np.roll(np.eye(4), 1, axis=0)
print(P)
```
:::
::: {.column width="45%"}
The cyclic permutation matrix $P_4$ shifts each element down by one position, with wrap-around.

$$P_{mn} = \delta_{m,(n+1) \bmod N}$$
:::
::::
````

---

## Progressive Reveal & Animation

### Pause (`. . .`)
The simplest reveal mechanism. Content after `. . .` appears on click.

**Warning:** `. . .` only works at **top level** — it breaks silently inside `:::` divs (columns, fragments, callouts), rendering as literal dots. Inside divs, use `{.incremental}` for lists or `{.fragment}` divs for other content.
```markdown
## Covariance and Toeplitz Matrices

Evaluating the covariance function at all pairs gives the covariance matrix:
$$K_{ij} = \text{cov}(x_i, x_j) = K(t_i, t_j)$$

. . .

If the GP is stationary and isotropic:
$$K = K(r), \quad r = |t - t'|$$

. . .

In this case the covariance matrix is Toeplitz!
```

### Fragment classes
```markdown
::: {.fragment .fade-in}
Appears with fade
:::

::: {.fragment .fade-up}
Slides up into view
:::

::: {.fragment .highlight-red}
Text turns red
:::

::: {.fragment .semi-fade-out}
Partially fades after next click
:::
```

Available fragment classes: `fade-in`, `fade-out`, `fade-up`, `fade-down`, `fade-left`, `fade-right`, `fade-in-then-out`, `fade-in-then-semi-out`, `grow`, `semi-fade-out`, `shrink`, `strike`, `highlight-red`, `highlight-green`, `highlight-blue`, `highlight-current-red`, `highlight-current-green`, `highlight-current-blue`.

### Fragment ordering
```markdown
::: {.fragment fragment-index=2}
This appears second.
:::

::: {.fragment fragment-index=1}
This appears first (despite being written after).
:::
```

### Auto-animate (morph between slides)
```markdown
## {auto-animate=true}

$$y = Rx + \epsilon$$

## {auto-animate=true}

$$y = Rx + \epsilon, \quad \epsilon \sim \mathcal{N}(0, \Sigma)$$

$$p(y|x) = \frac{1}{\sqrt{(2\pi)^n|\Sigma|}}
\exp\!\left(-\frac{1}{2}(y-Rx)^\dagger \Sigma^{-1}(y-Rx)\right)$$
```

---

## Layout

### Two columns (equal)
```markdown
:::: {.columns}
::: {.column width="50%"}
Left content
:::
::: {.column width="50%"}
Right content
:::
::::
```

### Two columns (asymmetric)
```markdown
:::: {.columns}
::: {.column width="65%"}
Main content / code
:::
::: {.column width="35%"}
Side notes / annotations
:::
::::
```

### Absolute positioning (for precise placement)
```markdown
::: {.absolute top=200 left=50}
![](images/logo.png){width=150}
:::

::: {.absolute bottom=30 right=30}
*Source: Wikipedia*
:::
```

### Footer override per slide
```markdown
## Special Slide {footer="Custom footer for this slide only"}
```

### Smaller text on a dense slide
```markdown
## Dense Content {.smaller}
```

### Scrollable slide (for long content)
```markdown
## Long Content {.scrollable}
```

---

## Media & Figures

### Image with sizing
```markdown
![Caption text](images/roots-of-unity.png){width=60% fig-align="center"}
```

### Image without caption (just display)
```markdown
![ ](images/sampling-aliasing.png){width=80%}
```

### Background image (full slide)
```markdown
## {background-image="images/meerkat-milkyway.jpg" background-opacity=0.3}

### Title over background
```

### Embedded video
```markdown
{{< video https://www.youtube.com/watch?v=spUNpyF58BY width="80%" >}}
```

### Local video
```markdown
{{< video images/demo.mp4 width="70%" >}}
```

### Linked images (fig-link bug workaround)

`fig-link` is a known Quarto bug for standalone images in revealjs — when an image is the only content on a slide, the link gets stripped. Workaround: use markdown linked images or ensure there is other text on the slide.

```markdown
[![MeerKAT array](images/meerkat.jpg)](https://www.sarao.ac.za)
```

---

## Callouts & Exercises

### Exercise box
```markdown
::: {.callout-note}
## Exercise
Show that the eigenvalues of a circulant matrix are given by the
Fourier transform of its first row or column.
:::
```

### Important result
```markdown
::: {.callout-important}
## Wiener-Khinchin Theorem
The power spectrum $P(s)$ is the Fourier transform of the
autocovariance function $K(r)$.
:::
```

### Tip
```markdown
::: {.callout-tip}
## Computational trick
Use circulant embedding to apply Toeplitz matrices via FFT in
$\mathcal{O}(N \log N)$ instead of $\mathcal{O}(N^2)$.
:::
```

Callout types: `note`, `tip`, `warning`, `caution`, `important`.

---

## Matrices & Tables

### LaTeX matrix environments
Use `bmatrix` (brackets), `pmatrix` (parentheses), `vmatrix` (vertical bars), or plain `matrix`.

### Markdown tables
```markdown
| $x(t)$ | $\longleftrightarrow$ | $X(\nu)$ |
|:------:|:---------------------:|:---------:|
| $A_0 \delta(t - t_0)$ | | $A_0 e^{-2\pi \imath \nu t_0}$ |
| $\sqcap(t)$ | | $\text{sinc}(\nu)$ |
| $\exp(-at^2)$ | | $\sqrt{\frac{\pi}{a}} \exp(-\pi^2 \nu^2 / a)$ |
```

### Styled tables (via SCSS or attributes)
```markdown
| Theorem | Formula |
|---------|---------|
| Linearity | $\mathcal{F}[ax + by] = a\mathcal{F}[x] + b\mathcal{F}[y]$ |
| Shift | $\mathcal{F}[x(t-t_0)] = e^{-2\pi \imath s t_0}\mathcal{F}[x(t)]$ |
| Convolution | $\mathcal{F}[x \cdot y] = \mathcal{F}[x] * \mathcal{F}[y]$ |

: Fourier Theorems {.striped}
```

---

## Background Customization

### Per-slide background color
```markdown
## Dark Slide {background-color="#1a1a2e"}
```

### Background image
```markdown
## {background-image="images/bg.jpg" background-size="cover" background-opacity="0.4"}
```

### Background gradient
```markdown
## {background-color="linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)"}
```

---

## Mermaid Diagrams

Quarto renders Mermaid diagrams natively. Style them richly — plain unstyled Mermaid looks too bare on dark slides. Use YAML config blocks (not the older `%%{init:...}%%` syntax) with `theme: base` and custom `themeVariables` for full control over colors.

**Important:** Set `mermaid-format: svg` in the YAML front matter (under `revealjs:`) — the default `js` format overrides custom themes.

````markdown
```{mermaid}
%%| fig-width: 4.5
---
config:
  theme: base
  themeVariables:
    lineColor: "#4ade80"
    primaryColor: "#1a5c3a"
    primaryBorderColor: "#4ade80"
    primaryTextColor: "#fff"
    fontFamily: "inherit"
---
flowchart LR
    C["📦 &nbsp; CABS &nbsp;"] <-.-> S["⚙️ &nbsp; Stimela &nbsp;"]
    R["📋 &nbsp; RECIPES &nbsp;"] <-.-> S
    D["💾 &nbsp; DATA &nbsp;"] <-.-> S
```
````

**Styling tips:**

- `mermaid-format: svg` required in YAML front matter for custom theming to work
- Use `theme: base` with custom `themeVariables` for full control — never rely on Mermaid's default harsh black lines
- Emoji prefixes convey meaning visually (e.g. `📦`, `⚙️`, `💾`, `📋`)
- `&nbsp;` padding widens nodes: `["&nbsp; label &nbsp;"]`
- `<br />` for line breaks in labels (not `\n`)
- Do NOT use quotation marks or parentheses inside node labels — they break the Mermaid parser
- Use `<-.->` for dashed bidirectional arrows (visually lighter than solid `-->`)
- `%%|` cell options control sizing: `%%| fig-width: 4.5`
- Available themes: `default`, `forest`, `dark`, `neutral`, `base`
- For comprehensive Mermaid reference, see the `quarto-authoring` skill's `references/diagrams.md`

---

## Code Block Scrollbar Fix

Quarto injects `.reveal div.sourceCode { overflow: auto; }` from its own internal stylesheet, which adds a cosmetic horizontal scrollbar to code blocks even when the code fits. This override must be in a separately-loaded CSS file — `include-in-header` does NOT work because Quarto's injected stylesheet wins.

Create `custom.css` in the talk directory:

```css
/* Quarto injects `.reveal div.sourceCode { overflow: auto; }` which adds
   a cosmetic horizontal scrollbar even when code fits. Override it. */
.reveal div.sourceCode { overflow-x: hidden !important; }
```

Reference it in YAML:

```yaml
format:
  revealjs:
    css: custom.css
```

---

## Nested Slide URL Navigation

When using `#` section headers, revealjs nests slides horizontally. Navigation URLs use the format `#/H/V` where H = horizontal section (0-indexed) and V = vertical slide within that section (0-indexed). The `#/slug` anchor reaches only the `#` section header itself (H position, V=0).

Fragment state **cannot** be set via URL — headless screenshots always show the pre-fragment (initial) state.

```bash
# Section 2, slide 3 (0-indexed)
google-chrome --headless=new --screenshot=/tmp/slide.png \
  --window-size=1600,900 --virtual-time-budget=5000 \
  "http://localhost:PORT/#/2/3"
```

---

## Custom Div Classes

Use Quarto's native fenced divs with CSS classes defined in your SCSS theme. **Do not use raw HTML `{=html}` blocks, inline style tags, CSS flexbox, or JavaScript for element positioning** — per AGENTS.md, always use Quarto's native constructs.

### Styled box (defined in SCSS theme)
```markdown
::: {.highlight-box}
$$K = K(r), \quad r = |t - t'|$$
:::
```

### Result box
```markdown
::: {.result-box}
**Theorem:** The eigenvalues of a circulant matrix are given by the DFT of its first column.
:::
```

Where `.highlight-box` and `.result-box` are defined in your SCSS theme.
