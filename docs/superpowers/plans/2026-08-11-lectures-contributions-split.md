# Lectures / Contributions Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the flat talk directories into `lectures/` and `contributions/` subtrees, each with its own formatting layer and agent rules, with a root index listing both classes.

**Architecture:** Each class becomes a directory holding a `_metadata.yml` that supplies all shared revealjs front matter, and an `AGENTS.md` that Claude Code loads automatically when working in that subtree. A shared pandoc title-slide partial renders a logo strip from a `logos:` metadata list. The canonical `dark-academic.scss` stays the base theme; two thin per-class SCSS layers sit on top.

**Tech Stack:** Quarto (revealjs), SCSS, pandoc templates, Python (scaffold script), bash + headless Chrome (verification).

**Spec:** `docs/superpowers/specs/2026-08-11-lectures-contributions-split-design.md`

## Global Constraints

- **Branch:** all work happens on `splitify`. Never commit to `main`.
- **Quarto version:** every task after Task 1 assumes the upgraded Quarto (1.10.x). Task 1 is a hard prerequisite.
- **Nothing is mandatory.** No front-matter field is enforced anywhere. `quarto render` must never fail because metadata is missing. Do not add schema checks or validation.
- **Contributions set no `date:` fallback.** An undated contribution renders a blank date. Never default it to `today`.
- **Theme path from a deck** is `../../templates/dark-academic.scss` (two levels, not one).
- **No inline HTML for layout** in `.qmd` bodies — Quarto fenced divs only. The title-slide *partial* is exempt; it is a pandoc template, not slide content.
- **`. . .` fragment pauses must be at top level** — they break silently inside `:::` divs.
- **Do not restyle deck content.** This refactor relocates files, hoists configuration, and installs machinery. Slide bodies are not touched except where a task says so explicitly.
- **The only approved shared-theme edit** is adding `.logo-strip` to `templates/dark-academic.scss`. Any other change to that file needs the user's sign-off first.

## File Structure

**Created:**
- `lectures/_metadata.yml` — all shared revealjs front matter for lectures, plus `date: today`
- `contributions/_metadata.yml` — same, minus any date, plus the contributions SCSS layer
- `lectures/AGENTS.md` + `lectures/CLAUDE.md` (symlink) — lecture authoring rules
- `contributions/AGENTS.md` + `contributions/CLAUDE.md` (symlink) — contribution authoring rules
- `templates/title-slide.html` — stock Quarto partial plus a logo strip
- `templates/lectures.scss` — logo-strip scale for lectures
- `templates/contributions.scss` — logo-strip scale for contributions
- `scripts/shoot-decks.sh` — renders and screenshots every deck; used as the verification harness by Tasks 1, 3, 4, 5, 7
- `covariance-toeplitz/custom.css`, `deconvolution/custom.css` — scrollbar fix, required once `css:` is hoisted

**Modified:**
- `_quarto.yml` — render glob `*/*/index.qmd`, `resources: assets/logos/**`
- `index.qmd` — two listings
- `templates/dark-academic.scss` — append `.logo-strip`
- `AGENTS.md` — shared rules only; structure section rewritten
- `README.md` — layout and command sections
- `.gitignore` — one rule for deck PDF exports
- `.claude/skills/quarto-revealjs/scripts/scaffold_talk.py` — required class argument
- `.claude/skills/quarto-revealjs/references/scaffolding.md` — document the class argument
- All six `index.qmd` files — strip hoisted front matter

**Deleted:** `covariance-toeplitz/covariance-toeplitz.qmd`
**Untracked (kept on disk):** `deconvolution/deconvolution.pdf`

---

## Task 1: Upgrade Quarto and prove nothing broke

Prerequisite for everything else. Produces no repository change beyond the verification harness, so that upgrade regressions stay separable from refactor regressions.

**Files:**
- Create: `scripts/shoot-decks.sh`

**Interfaces:**
- Produces: `scripts/shoot-decks.sh <outdir>` — renders the site and writes `<outdir>/<deck-slug>.png` for every deck's title slide. Later tasks call it to compare before/after states.

- [ ] **Step 1: Record the starting version**

```bash
quarto --version | tee /tmp/claude-scratch-quarto-before.txt
```

Expected: `1.6.42`. If it already reports 1.10.x, skip to Step 6.

- [ ] **Step 2: Write the verification harness**

Create `scripts/shoot-decks.sh`:

```bash
#!/usr/bin/env bash
# Render the site and screenshot every deck's title slide.
# Usage: scripts/shoot-decks.sh <output-dir> [port]
set -euo pipefail

OUT="${1:?usage: shoot-decks.sh <output-dir> [port]}"
PORT="${2:-4321}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$OUT"
cd "$ROOT"

echo "--- rendering ---"
quarto render

# Serve _site statically; quarto preview would rebuild and race us.
python3 -m http.server "$PORT" --directory _site >/dev/null 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null || true' EXIT
sleep 2

# Every directory in _site containing an index.html other than the root.
find _site -mindepth 2 -name index.html | while read -r page; do
  rel="${page#_site/}"; rel="${rel%/index.html}"
  slug="$(echo "$rel" | tr '/' '-')"
  echo "--- shooting $rel ---"
  google-chrome --headless=new \
    --screenshot="$OUT/$slug.png" \
    --window-size=1600,900 \
    --virtual-time-budget=6000 \
    "http://localhost:$PORT/$rel/#/title-slide" >/dev/null 2>&1
done

echo "--- wrote to $OUT ---"
ls -1 "$OUT"
```

```bash
chmod +x scripts/shoot-decks.sh
```

- [ ] **Step 3: Capture the pre-upgrade baseline**

```bash
scripts/shoot-decks.sh /tmp/claude-scratch-decks-before
```

Expected: six PNGs, one per deck. Read two or three of them to confirm they show real title slides (background image, title, author) and not blank pages.

- [ ] **Step 4: Upgrade Quarto**

This writes to `/opt` and `/usr/local/bin`, so it needs elevated privileges. **The user runs this**, by typing it in the session prefixed with `!`:

```bash
curl -LO https://quarto.org/download/latest/quarto-linux-amd64.deb && sudo dpkg -i quarto-linux-amd64.deb && rm quarto-linux-amd64.deb
```

- [ ] **Step 5: Confirm the new version**

```bash
quarto --version
```

Expected: `1.10.x` (1.10.18 or later).

- [ ] **Step 6: Re-render and compare**

```bash
scripts/shoot-decks.sh /tmp/claude-scratch-decks-after
```

Read each of the six `after` PNGs against its `before` counterpart. Expected: visually identical. Any difference must be understood before continuing — do not proceed on "looks close enough".

If ImageMagick is available, get a numeric answer first and only eyeball the ones that differ:

```bash
for f in /tmp/claude-scratch-decks-before/*.png; do
  b="$(basename "$f")"
  printf '%s: ' "$b"
  compare -metric AE "$f" "/tmp/claude-scratch-decks-after/$b" null: 2>&1 || true
  echo
done
```

- [ ] **Step 7: Re-run the two mechanism spikes**

The design depends on two Quarto behaviours verified only against 1.6.42. Re-prove both:

```bash
S=/tmp/claude-scratch-spike && rm -rf $S && mkdir -p $S/templates $S/lectures/demo && cd $S
printf 'project:\n  type: website\n  render:\n    - "*/*/index.qmd"\n  resources:\n    - assets/logos/**\n' > _quarto.yml
mkdir -p assets/logos && cp /home/bester/talks/assets/logos/sarao_logo.jpg assets/logos/
printf '/*-- scss:rules --*/\n.reveal h2 { color: rgb(1, 2, 3); }\n' > templates/probe.scss
cp /opt/quarto/share/formats/revealjs/pandoc/title-slide.html templates/title-slide.html
printf '$if(logos)$\n<div class="logo-strip">$for(logos)$<img src="$logos$" alt="" />$endfor$</div>\n$endif$\n' >> templates/title-slide.html
printf 'format:\n  revealjs:\n    theme: [dark, ../../templates/probe.scss]\n    template-partials: [../../templates/title-slide.html]\nlogos:\n  - /assets/logos/sarao_logo.jpg\n' > lectures/_metadata.yml
printf -- '---\ntitle: "Probe"\n---\n\n## Hello\n' > lectures/demo/index.qmd
quarto render
echo "--- spike A: doc-relative _metadata.yml paths ---"
grep -rl "rgb(1, *2, *3)" _site/ | head -1
echo "--- spike B: logo strip in title slide ---"
grep -o '<div class="logo-strip">.*</div>' _site/lectures/demo/index.html
cd /home/bester/talks
```

Expected: spike A prints a theme CSS path (the probe compiled in); spike B prints the logo-strip div with a rewritten relative `src`. Both empty means the design's mechanism has changed under the new Quarto — **stop and report** rather than working around it.

- [ ] **Step 8: Commit the harness**

```bash
git add scripts/shoot-decks.sh
git commit -m "test: add deck screenshot harness for refactor verification"
```

---

## Task 2: Housekeeping

Clears the stale files and creates the two `custom.css` files that hoisting `css:` in Task 4 will require. Independent of the move, so it lands first and keeps later diffs readable.

**Files:**
- Delete: `covariance-toeplitz/covariance-toeplitz.qmd`
- Create: `covariance-toeplitz/custom.css`, `deconvolution/custom.css`
- Modify: `.gitignore`
- Untrack: `deconvolution/deconvolution.pdf`

- [ ] **Step 1: Confirm the stale file is still what the audit found**

```bash
diff covariance-toeplitz/covariance-toeplitz.qmd covariance-toeplitz/index.qmd | head -20
```

Expected: differences showing `date: "11 March 2025"` vs `date: today`, `.png` vs `.jpg` background, and lowercase `tex:`/`macros:` vs `TeX:`/`Macros:`. This confirms it is the superseded predecessor, not a live variant. If the diff looks different from that, stop and re-audit.

- [ ] **Step 2: Delete it**

```bash
git rm covariance-toeplitz/covariance-toeplitz.qmd
```

- [ ] **Step 3: Create the two missing custom.css files**

Both get the identical scrollbar fix already present in the other four decks. Write to `covariance-toeplitz/custom.css` **and** `deconvolution/custom.css`:

```css
/* Quarto injects `.reveal div.sourceCode { overflow: auto; }` which adds
   a cosmetic horizontal scrollbar even when code fits. Override it. */
.reveal div.sourceCode { overflow-x: hidden !important; }
```

- [ ] **Step 4: Untrack the committed PDF export, keeping the file**

```bash
git rm --cached deconvolution/deconvolution.pdf
ls -la deconvolution/deconvolution.pdf
```

Expected: git reports the file removed from the index; `ls` still shows it on disk. If the file is gone from disk, you used `git rm` without `--cached` — restore it with `git checkout HEAD -- deconvolution/deconvolution.pdf` and retry.

- [ ] **Step 5: Add the gitignore rule**

Append to `.gitignore`, after the `# Rendered outputs` block:

```
# Deck PDF exports (regenerate with decktape — see README)
*/deconvolution.pdf
*.pdf
!reference_pdfs/*.pdf
```

Note `reference_pdfs/` is already ignored wholesale by its own rule, so the negation is belt-and-braces and harmless.

- [ ] **Step 6: Verify the ignore works and the render is unaffected**

```bash
git status --short
git check-ignore -v deconvolution/deconvolution.pdf
quarto render 2>&1 | tail -5
```

Expected: `git status` shows the deletion, the two new CSS files, and the modified `.gitignore` — but **not** `deconvolution.pdf` as untracked. `check-ignore` names the rule. The render completes.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "chore: remove superseded deck source, untrack PDF export, add missing custom.css"
```

---

## Task 3: Move the decks into class subtrees

Relocates all six decks and makes the site build again. Deliberately does *not*
hoist front matter — that is Task 4 — so that a break here is unambiguously a
path problem.

**Files:**
- Move: five decks into `lectures/`, `kremetart-pipeline` into `contributions/`
- Modify: `_quarto.yml`, all six `index.qmd` (theme path only), `README.md`

- [ ] **Step 1: Create the class directories and move the decks**

```bash
mkdir -p lectures contributions
git mv aperture-synthesis-imaging lectures/
git mv covariance-toeplitz        lectures/
git mv cultcargo-fundamentals     lectures/
git mv deconvolution              lectures/
git mv stimela-fundamentals       lectures/
git mv kremetart-pipeline         contributions/
```

- [ ] **Step 2: Verify git tracked the moves as renames**

```bash
git status --short | head -20
```

Expected: lines beginning `R` (rename), not `D`/`A` pairs. Renames are what
preserve `git log --follow`.

- [ ] **Step 3: Update the render glob and declare the logo assets as resources**

Replace the whole of `_quarto.yml` with:

```yaml
project:
  type: website
  render:
    - index.qmd
    - "*/*/index.qmd"
  resources:
    - assets/logos/**

website:
  title: "Talks — Landman Bester"
  description: "Lectures and conference contributions — SARAO / Rhodes / AIMS South Africa"
```

The `resources:` block is what copies `assets/logos/` into `_site/` so the
`/assets/logos/...` paths used by the logo strip resolve. It is added here
rather than in Task 5 because it is project configuration, and Task 5 should be
purely about the strip itself.

- [ ] **Step 4: Fix the theme path in all six decks**

Each deck is now one level deeper, so `../templates` no longer resolves. These
lines are removed entirely in Task 4; fixing them now keeps the tree rendering
at every commit.

```bash
sed -i 's|\.\./templates/dark-academic\.scss|../../templates/dark-academic.scss|' \
  lectures/*/index.qmd contributions/*/index.qmd
grep -rn "templates/dark-academic.scss" lectures contributions
```

Expected: six lines, all reading `../../templates/dark-academic.scss`.

- [ ] **Step 5: Render and confirm all six decks still build**

```bash
quarto render 2>&1 | tail -10
ls _site/lectures _site/contributions
```

Expected: `Output created` for each deck; `_site/lectures/` holds five
directories and `_site/contributions/` holds one.

- [ ] **Step 6: Screenshot to confirm nothing shifted visually**

```bash
scripts/shoot-decks.sh /tmp/claude-scratch-decks-moved
```

Read the six PNGs. Expected: identical to `/tmp/claude-scratch-decks-after`
from Task 1 — same backgrounds, same titles. A missing background image means
the theme path or a resource path is wrong.

- [ ] **Step 7: Update the README layout section**

In `README.md`, replace the `## Layout` code block's talk-directory portion so
it shows the two classes, and fix the preview URL in `## Everyday commands`:

```
├── lectures/              # Course and teaching decks (undated)
│   ├── AGENTS.md          # Lecture-specific agent rules
│   ├── _metadata.yml      # Shared revealjs front matter for all lectures
│   └── <talk-name>/
│       ├── index.qmd
│       ├── custom.css
│       └── images/
├── contributions/         # Conference and workshop talks (dated)
│   ├── AGENTS.md
│   ├── _metadata.yml
│   └── <talk-name>/
```

and

```bash
cd lectures/<talk-name>       # or contributions/<talk-name>
quarto preview index.qmd
# → serves at http://localhost:PORT/lectures/<talk-name>/  (note the prefix!)
```

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "refactor: move decks into lectures/ and contributions/ subtrees"
```

---

## Task 4: Hoist shared front matter into per-class `_metadata.yml`

The change that makes the class boundary real: after this, formatting for a
whole class is one file.

**Files:**
- Create: `lectures/_metadata.yml`, `contributions/_metadata.yml`
- Modify: all six `index.qmd`

**Interfaces:**
- Produces: both `_metadata.yml` files supply `theme`, `template-partials`,
  `css`, `title-slide-attributes`, and the revealjs option block. Task 5 adds
  `logos:` and the class SCSS layer to these same two files.

- [ ] **Step 1: Create `lectures/_metadata.yml`**

```yaml
# Shared front matter for every lecture. Per-deck front matter overrides these.
author: "Landman Bester"
date: today

format:
  revealjs:
    theme: [dark, ../../templates/dark-academic.scss]
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
```

Paths here are resolved relative to the *document*, not this file — which is
why `../../templates/` is correct from `lectures/<slug>/index.qmd`.

- [ ] **Step 2: Create `contributions/_metadata.yml`**

Identical except for the missing `date:` — a contribution supplies its own, and
defaulting it would silently stamp an old talk with today.

```yaml
# Shared front matter for every contribution. Per-deck front matter overrides these.
# Deliberately no `date:` — each contribution sets its own event date.
author: "Landman Bester"

format:
  revealjs:
    theme: [dark, ../../templates/dark-academic.scss]
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
```

- [ ] **Step 3: Strip the hoisted keys from the five lecture decks**

For each of `lectures/aperture-synthesis-imaging`, `lectures/covariance-toeplitz`,
`lectures/cultcargo-fundamentals`, `lectures/deconvolution`,
`lectures/stimela-fundamentals`: remove `author:`, `date:`, and from the
`revealjs:` block remove `theme:`, `slide-number:`, `code-line-numbers:`,
`code-copy:`, `highlight-style:`, `center:`, `transition:`, `mermaid-format:`,
`css:`, and `title-slide-attributes:`.

**Keep** everything genuinely deck-specific:
- `title:`, `subtitle:`, `institute:`
- `include-in-header:` MathJax macro blocks (`deconvolution`, `covariance-toeplitz`)
- `deconvolution`'s `mermaid: {theme: dark}` and its
  `title-slide-attributes:` override — its background is
  `images/meerkat-dish-night.jpg` at opacity `0.6`, not the shared default

After stripping, `lectures/cultcargo-fundamentals/index.qmd` should open:

```yaml
---
title: "CASA and cult-cargo"
institute: "SARAO"
---
```

and `lectures/deconvolution/index.qmd` should retain:

```yaml
---
title: "Deconvolution"
institute: "AIMS South Africa"
format:
  revealjs:
    mermaid:
      theme: dark
    title-slide-attributes:
      data-background-image: images/meerkat-dish-night.jpg
      data-background-opacity: "0.6"
    include-in-header:
      text: |
        <script>
        MathJax = {
          TeX: {
            Macros: {
              prox: "\\operatorname{prox}",
              argmin: "\\operatorname{argmin}",
              minimize: "\\operatorname{minimize}"
            }
          }
        };
        </script>
---
```

- [ ] **Step 4: Drop the stray footer from `covariance-toeplitz`**

That deck carries `footer: "SARAO | AIMS South Africa"`, which contradicts the
house rule that footers are omitted because they cost space on dense slides.
Remove the line while stripping. This is the one content-adjacent change the
refactor makes, and it aligns the deck with the documented convention.

- [ ] **Step 5: Strip the contribution deck**

`contributions/kremetart-pipeline/index.qmd` keeps `title:`, `subtitle:`, and
`institute:`, and gains an explicit date since contributions no longer inherit
one. Use the date the talk was actually given — if unknown, ask the user rather
than guessing; a wrong date on a conference talk is worse than a blank one.

```yaml
---
title: "KREMETART"
subtitle: "Streaming calibration, imaging & transient detection for TART"
institute: "SARAO / Rhodes"
date: "2026-06-18"        # confirm with the user
---
```

- [ ] **Step 6: Verify the hoist produced identical output**

```bash
quarto render 2>&1 | tail -5
scripts/shoot-decks.sh /tmp/claude-scratch-decks-hoisted
```

Read all six PNGs against `/tmp/claude-scratch-decks-moved`. Expected: identical
apart from `kremetart-pipeline`'s date line and `covariance-toeplitz` losing its
footer. Anything else differing means a hoisted key did not apply — check that
the deck's remaining front matter is not accidentally overriding it with an
empty value.

- [ ] **Step 7: Confirm a deck with no metadata at all still renders**

The "nothing is mandatory" constraint, tested rather than assumed:

```bash
mkdir -p contributions/_probe && printf -- '---\ntitle: "Probe"\n---\n\n## Hello\n' > contributions/_probe/index.qmd
printf '.reveal div.sourceCode { overflow-x: hidden !important; }\n' > contributions/_probe/custom.css
quarto render 2>&1 | grep -iE "error|Output created.*_probe"
rm -rf contributions/_probe _site/contributions/_probe
```

Expected: an `Output created` line for the probe and no errors — a contribution
with only a title builds. Note the probe needs its own `custom.css` because
`css:` is hoisted; that is a real constraint on the scaffold script, handled in
Task 7.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "refactor: hoist shared revealjs front matter into per-class _metadata.yml"
```

---

## Task 5: Logo strip

Installs the title-slide partial, the shared `.logo-strip` rule, and the two
class SCSS layers, then wires them into both `_metadata.yml` files.

**Files:**
- Create: `templates/title-slide.html`, `templates/lectures.scss`, `templates/contributions.scss`
- Modify: `templates/dark-academic.scss`, `lectures/_metadata.yml`, `contributions/_metadata.yml`

**Interfaces:**
- Consumes: the `resources: assets/logos/**` declaration added to `_quarto.yml` in Task 3.
- Produces: a `logos:` metadata key — a list of project-root-relative image
  paths — rendered as `<div class="logo-strip">` on the title slide. Task 7's
  scaffold script emits this key.

- [ ] **Step 1: Start the partial from Quarto's stock template, do not hand-write it**

The stock partial carries `$for(title-slide-attributes/pairs)$`, which is what
applies every deck's background image. A hand-written replacement that omits it
silently kills the title background on all six decks.

```bash
cp /opt/quarto/share/formats/revealjs/pandoc/title-slide.html templates/title-slide.html
cat templates/title-slide.html
```

Expected: a `<section id="$idprefix$title-slide"...>` block with `$title$`,
`$subtitle$`, `$author$`, `$institute$`, `$date$`. If the file differs from
this shape under the new Quarto, keep whatever it now contains and append to
it — the point is to extend the stock template, not to match a remembered one.

- [ ] **Step 2: Append the event line and logo strip to the partial**

Add before the closing `</section>`, so `templates/title-slide.html` ends:

```html
$if(event)$
  <p class="event">$event$$if(location)$ &middot; $location$$endif$</p>
$endif$
$if(logos)$
  <div class="logo-strip">$for(logos)$<img src="$logos$" alt="" />$endfor$</div>
$endif$
</section>
```

Every block is guarded by `$if(...)$`, so a deck that sets none of these keys
renders exactly the stock title slide. That is what keeps the fields optional.

- [ ] **Step 3: Add `.logo-strip` to the shared theme**

This is the one approved edit to `templates/dark-academic.scss`. Append to the
`// --- Custom utility classes ---` section at the end of the file. The white
chip treatment is lifted from the proven `.logo-chip` rule in the
kremetart deck, so mixed logo formats all read against the dark background:

```scss
// Logo strip — title slide (via templates/title-slide.html) and closing slides.
// Each logo sits on a white rounded chip so light, dark, and transparent
// source images all read against the dark background.
.reveal .logo-strip {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.9em;
  margin-top: 1.4em;
  max-width: 100%;

  img {
    height: 52px;
    width: auto;
    margin: 0;
    background: #ffffff;
    border-radius: 10px;
    padding: 7px 11px;
    border: none;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
  }
}

.reveal .event {
  font-size: 0.75em;
  color: #8b949e;
}
```

- [ ] **Step 4: Create the two class layers**

`templates/lectures.scss` — the standing institutional logos are supporting
detail on a lecture, so the strip is smaller and set back:

```scss
/*-- scss:rules --*/

// Lectures: a quiet institutional strip. The content is the point.
.reveal .logo-strip {
  gap: 0.7em;
  margin-top: 1.1em;
  opacity: 0.85;

  img { height: 42px; }
}
```

`templates/contributions.scss` — a conference title slide carries more logos
and is read from further away:

```scss
/*-- scss:rules --*/

// Contributions: a fuller strip with room for event logos alongside the
// institutional ones, sized to stay legible from the back of a lecture hall.
.reveal .logo-strip {
  gap: 1.1em;
  margin-top: 1.5em;

  img { height: 60px; }
}
```

- [ ] **Step 5: Wire both into the class metadata**

In `lectures/_metadata.yml`, extend the theme list and add the partial and
logos:

```yaml
format:
  revealjs:
    theme: [dark, ../../templates/dark-academic.scss, ../../templates/lectures.scss]
    template-partials:
      - ../../templates/title-slide.html

logos:
  # - /assets/logos/nrf.png     # uncomment once the file exists
  - /assets/logos/sarao_logo.jpg
  - /assets/logos/rhodes_banner.jpg
```

In `contributions/_metadata.yml`, the same with `contributions.scss`:

```yaml
format:
  revealjs:
    theme: [dark, ../../templates/dark-academic.scss, ../../templates/contributions.scss]
    template-partials:
      - ../../templates/title-slide.html

logos:
  # - /assets/logos/nrf.png     # uncomment once the file exists
  - /assets/logos/sarao_logo.jpg
  - /assets/logos/rhodes_banner.jpg
```

A contribution appends its event logos by redeclaring the whole `logos:` list
in its own front matter — YAML lists replace rather than merge.

- [ ] **Step 6: Render and confirm the assets ship**

```bash
quarto render 2>&1 | tail -5
ls _site/assets/logos/
grep -o '<div class="logo-strip">.*</div>' _site/lectures/deconvolution/index.html
```

Expected: `_site/assets/logos/` is populated; the grep prints the strip with
`src` rewritten to a relative path such as `../../assets/logos/sarao_logo.jpg`.
An empty grep means `template-partials` did not apply — check the path resolves
from the *document*, two levels up.

- [ ] **Step 7: Screenshot every title slide**

```bash
scripts/shoot-decks.sh /tmp/claude-scratch-decks-logos
```

Read all six PNGs. Expected, and each is a real failure mode worth looking for:
- the background image is **still there** (the partial kept `title-slide-attributes`)
- two logo chips sit below the title, not overlapping it or running off the slide
- the contribution's chips are visibly larger than the lectures'
- no broken-image icon (the `nrf.png` line is commented out)

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "feat: add title-slide logo strip with per-class sizing"
```

---

## Task 6: Root index with two listings

**Files:**
- Modify: `index.qmd`

- [ ] **Step 1: Rewrite `index.qmd`**

```markdown
---
title: "Talks"
format:
  html:
    theme: darkly
listing:
  - id: contributions
    contents: "contributions/*/index.qmd"
    type: table
    fields: [date, title, event, institute]
    field-display-names:
      event: "Event"
      institute: "Affiliation"
    sort: "date desc"
    sort-ui: false
    filter-ui: false
  - id: lectures
    contents: "lectures/*/index.qmd"
    type: table
    fields: [title, institute]
    field-display-names:
      institute: "Venue"
    sort: "title"
    sort-ui: false
    filter-ui: false
---

Quarto revealjs presentations. Click a title to open the slides.

## Contributions

Conference and workshop talks, each given once on the date shown.

::: {#contributions}
:::

## Lectures

Teaching material, revised and re-given. No fixed date.

::: {#lectures}
:::
```

- [ ] **Step 2: Render and inspect the generated tables**

```bash
quarto render index.qmd 2>&1 | tail -3
grep -c "kremetart" _site/index.html
grep -c "deconvolution" _site/index.html
```

Expected: both greps return at least 1 — each class's decks appear in its own
table.

- [ ] **Step 3: Screenshot the index**

```bash
google-chrome --headless=new --screenshot=/tmp/claude-scratch-index.png \
  --window-size=1600,1200 --virtual-time-budget=6000 \
  "file://$PWD/_site/index.html"
```

Read `/tmp/claude-scratch-index.png`. Expected: a **Contributions** table with
one dated row, then a **Lectures** table with five undated rows. Both tables
populated — an empty table means the `contents:` glob is wrong.

- [ ] **Step 4: Prove missing fields degrade gracefully**

The "nothing is mandatory" constraint applied to the listing:

```bash
mkdir -p contributions/_probe
printf -- '---\ntitle: "Probe With No Metadata"\n---\n\n## Hello\n' > contributions/_probe/index.qmd
printf '.reveal div.sourceCode { overflow-x: hidden !important; }\n' > contributions/_probe/custom.css
quarto render 2>&1 | grep -ciE "^error" || echo "no errors"
grep -c "Probe With No Metadata" _site/index.html
rm -rf contributions/_probe _site/contributions/_probe
quarto render >/dev/null 2>&1
```

Expected: no errors, and the probe appears in the contributions table with
blank date/event/affiliation cells. If the render fails, something is treating
a field as required — find it and remove the requirement.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: split root index into contributions and lectures listings"
```

---

## Task 7: Agent rules and scaffolding

Splits the rules by location and teaches the scaffold script about classes.
These land together because a new deck is created by the script and then
authored under the rules — a reviewer would accept or reject them as one
change.

**Files:**
- Create: `lectures/AGENTS.md`, `lectures/CLAUDE.md`, `contributions/AGENTS.md`, `contributions/CLAUDE.md`
- Modify: `AGENTS.md`, `README.md`, `.claude/skills/quarto-revealjs/scripts/scaffold_talk.py`, `.claude/skills/quarto-revealjs/references/scaffolding.md`

- [ ] **Step 1: Write `lectures/AGENTS.md`**

```markdown
# Lectures — Agent Context

> Rules for teaching decks. `CLAUDE.md` is a symlink to this file.
> The repository-wide conventions in `../AGENTS.md` still apply; this file
> only covers what is specific to lectures.

## What a lecture is

Teaching material, revised and re-given. A lecture is never "finished" — it is
the current best version of an explanation. Optimise for the second delivery,
not the first.

## Front matter

`lectures/_metadata.yml` supplies theme, revealjs options, title background,
author, and `date: today`. A lecture's own front matter should carry only what
is specific to it:

- `title:` — the topic
- `institute:` — the course or host institution (e.g. `NASSP Radio Astronomy Course`)
- MathJax macros, mermaid overrides, a different title background

**Never hard-code a date.** `date: today` is inherited and is correct: the deck
is presented whenever it is presented. A hard-coded date makes a re-given
lecture look stale.

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

## Citations

Optional. If a lecture cites sources, follow the contributions pattern in
`../contributions/AGENTS.md`: a `references.bib` beside `index.qmd`, and an
explicit `## References` slide holding `::: {#refs}` placed *before* the
closing slide.
```

- [ ] **Step 2: Write `contributions/AGENTS.md`**

```markdown
# Contributions — Agent Context

> Rules for conference and workshop talks. `CLAUDE.md` is a symlink to this file.
> The repository-wide conventions in `../AGENTS.md` still apply; this file
> only covers what is specific to contributions.

## What a contribution is

A talk given once, at a named event, on a specific date. It is a record as much
as a deliverable — the version presented is the version kept.

## Front matter

`contributions/_metadata.yml` supplies theme, revealjs options, title
background, and author. It deliberately supplies **no date**.

```yaml
---
title: "KREMETART"
subtitle: "Streaming calibration, imaging & transient detection for TART"
institute: "SARAO / Rhodes"
date: "2026-06-18"
event: "SARAO Postgraduate Bursary Conference"
location: "Cape Town, South Africa"
---
```

- `date:` is the date of the **event**, hard-coded. This inverts the lecture
  rule, and `date: today` is wrong here — it would relabel an old talk every
  time the site rebuilds.
- `institute:` is your own affiliation, not the venue. The venue is `event:`.
- `event:` and `location:` appear on the title slide and in the root listing.

**Nothing is required.** A contribution with only a `title:` renders, and the
site builds. These fields are worth setting because they populate the listing
and the title slide, not because anything enforces them. Never add validation.

If a date is genuinely unknown, leave it out — a blank cell is honest. Do not
guess, and do not fall back to `today`.

## Style

Conference slots are short and the room is large.

- Budget slides against the slot: a 15-minute contributed talk is a different
  object from a 45-minute lecture. When it does not fit, **split or cut** —
  do not shrink the font
- Read from the back of a hall: fewer equations per slide, larger figures
- One idea per slide; put the derivation in the paper, not the deck

## Logos

The institutional strip is inherited. A contribution **appends** the event's
logos by redeclaring the whole list in its own front matter — YAML lists
replace rather than merge:

```yaml
logos:
  - /assets/logos/sarao_logo.jpg
  - /assets/logos/rhodes_banner.jpg
  - images/logos/conference.png
```

Put the strip on the closing slide too. That slide stays on screen through the
question session, so it is the one people look at longest. Use fenced divs, not
raw HTML:

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

## Citations

Academic talks attribute. When citing, add a `references.bib` beside
`index.qmd` and declare it:

```yaml
bibliography: references.bib
```

Cite with standard Pandoc syntax — `@smith2020`, `[@smith2020; @jones2021]`,
`[-@smith2020]` to suppress the author.

Quarto appends the bibliography at the end of the document, which on revealjs
means it lands *after* your closing slide unless you give it a home. Place it
explicitly:

```markdown
## References {.smaller}

::: {#refs}
:::

## Thanks! {background-color="#0d1117" .closing-slide}
```

A deck that cites nothing needs neither the file nor the key.

## Delivery

These matter for a live talk and are worth setting up before the room fills:

- **Speaker notes** — `::: {.notes}` blocks. Visible only in presenter view,
  which is `S` during the presentation. Keep the narration with the slide it
  belongs to; the `.qmd` stays the single source of truth for the talk
- **Presenter view** shows notes, next slide, and a timer — check the timer
  against the slot before presenting
- **Chalkboard** (`C`) and **pointer** (`B`) are available for questions,
  when someone asks about a detail no slide covers
```

- [ ] **Step 3: Create the symlinks**

```bash
ln -s AGENTS.md lectures/CLAUDE.md
ln -s AGENTS.md contributions/CLAUDE.md
ls -la lectures/CLAUDE.md contributions/CLAUDE.md
```

Expected: both listed as symlinks pointing at `AGENTS.md`, matching the root
convention.

- [ ] **Step 4: Trim the root `AGENTS.md`**

Three edits, leaving everything else (manim, mermaid, theme classes, the
screenshot loop, overflow fixes, boundaries) untouched:

1. Replace the `## Directory structure` tree with the new layout — the two
   class directories each holding `AGENTS.md`, `_metadata.yml`, and their
   decks; `scripts/shoot-decks.sh`; `templates/` gaining `title-slide.html`,
   `lectures.scss`, `contributions.scss`.

2. In `### Authoring conventions`, replace the **Dynamic date** bullet and the
   theme-path bullet with:

```markdown
- **Class rules live with the class** — `lectures/AGENTS.md` and
  `contributions/AGENTS.md` carry the front-matter, style, logo, and citation
  rules for their subtree, and are loaded automatically when working there.
  Dates in particular differ between the two: read the class file first
- **Shared front matter is hoisted** — theme, revealjs options, title
  background, and `css:` come from the class `_metadata.yml`. A deck's own
  front matter carries only what is specific to it. Theme path, when a deck
  needs to override it, is `../../templates/dark-academic.scss`
```

3. Add to the top of `## Boundaries`:

```markdown
- **Every deck needs a `custom.css`** — `css: custom.css` is hoisted into both
  class `_metadata.yml` files, so a deck without that file fails to render.
  The scaffold script creates it; hand-made directories need it too
```

- [ ] **Step 5: Add the skill pointer to the root `AGENTS.md`**

Under `### 1. Scaffold and port`, after the existing skill description:

```markdown
For citations, cross-references, conditional content, and general Quarto
authoring beyond slides, use the `quarto-authoring` skill (currently v1.4,
written against Quarto 1.9.36).
```

- [ ] **Step 6: Teach the scaffold script about classes**

In `.claude/skills/quarto-revealjs/scripts/scaffold_talk.py`:

- Add a required positional argument `talk_class` with `choices=["lecture", "contribution"]`, placed **before** `title`.
- Derive the output directory as `lectures/<slug>` or `contributions/<slug>` when `--output` is not given.
- Emit thin front matter, since `_metadata.yml` now carries the shared block.
- **Rename the existing `event` parameter to `institute`**, and the `--event`
  flag to `--institute`. Today that parameter populates the `institute:` key
  despite being called `event`; under the new contract `event:` is a *different*
  field meaning the conference name, so leaving the old name in place guarantees
  a mix-up. Rename the function parameter, the `argparse` flag, and the call
  site in `main()` together.
- Drop the now-unused `--logo` and `--footer` flags and the `theme_path` /
  `standalone` handling: theme and logos come from `_metadata.yml`, and the
  house rule omits footers. Removing them prevents a scaffolded deck from
  emitting keys that fight the hoisted block.

Replace the `qmd_content` construction with:

```python
    if talk_class == "contribution":
        meta_lines = (
            f'\ninstitute: "{institute}"' if institute else ""
        ) + '\ndate: ""            # event date, e.g. "2026-06-18"' \
          + '\nevent: ""           # conference or workshop name' \
          + '\nlocation: ""        # city, country'
    else:
        meta_lines = f'\ninstitute: "{institute}"' if institute else ""

    qmd_content = f"""\
---
title: "{title}"{meta_lines}
---

## Introduction

<!-- Replace with your opening content -->

## Thanks! {{background-color="#0d1117" .closing-slide}}

::: {{.contact}}
landman.bester@gmail.com
:::
"""
```

Keep the existing `custom.css` creation — it is now load-bearing, because
`css: custom.css` is hoisted and a deck without the file fails to render.

Update the closing `print()` guidance to reference the class directory and the
two-segment preview URL.

- [ ] **Step 7: Verify the script produces a rendering deck of each class**

```bash
python .claude/skills/quarto-revealjs/scripts/scaffold_talk.py lecture "Scaffold Probe"
python .claude/skills/quarto-revealjs/scripts/scaffold_talk.py contribution "Scaffold Probe Two"
ls lectures/scaffold-probe contributions/scaffold-probe-two
quarto render 2>&1 | grep -ciE "^error" || echo "no errors"
rm -rf lectures/scaffold-probe contributions/scaffold-probe-two
quarto render >/dev/null 2>&1
```

Expected: each directory contains `index.qmd`, `custom.css`, `images/`; both
render without error; the contribution's front matter carries empty
`date`/`event`/`location` stubs and the lecture's does not.

- [ ] **Step 8: Document the class argument**

In `.claude/skills/quarto-revealjs/references/scaffolding.md`, update the usage
examples to show the required class argument and the resulting two-class
layout:

```bash
python scripts/scaffold_talk.py lecture "Interferometry Basics"
# → lectures/interferometry-basics/

python scripts/scaffold_talk.py contribution "KAT-7 Transient Search"
# → contributions/kat-7-transient-search/
```

Note that shared front matter now lives in the class `_metadata.yml`, so
scaffolded decks are deliberately thin, and that `custom.css` is required.

- [ ] **Step 9: Update the README commands section**

Point the "create a new talk" paragraph at the class argument, and confirm the
layout tree edited in Task 3 still matches the final structure.

- [ ] **Step 10: Commit**

```bash
git add -A
git commit -m "docs: split agent rules by class and teach scaffold script about classes"
```

---

## Task 8: Final acceptance

**Files:** none — verification only.

- [ ] **Step 1: Full clean render**

```bash
rm -rf _site .quarto
quarto render 2>&1 | tail -15
```

Expected: `Output created` for the index and all six decks; no errors.

- [ ] **Step 2: Screenshot everything and read it**

```bash
scripts/shoot-decks.sh /tmp/claude-scratch-decks-final
```

Read all six. Expected: correct background, correct title, logo strip present
and sized per class, nothing overflowing.

- [ ] **Step 3: Confirm history survived the moves**

```bash
git log --follow --oneline -- lectures/deconvolution/index.qmd | tail -3
git log --follow --oneline -- contributions/kremetart-pipeline/index.qmd | tail -3
```

Expected: commits predating this branch. History stopping at the move commit
means `git mv` was not used and the moves need redoing.

- [ ] **Step 4: Confirm the class rules are discoverable**

```bash
ls -la lectures/CLAUDE.md contributions/CLAUDE.md
readlink lectures/CLAUDE.md contributions/CLAUDE.md
```

Expected: both symlinks resolve to `AGENTS.md`.

- [ ] **Step 5: Confirm nothing is enforced**

```bash
grep -rniE "required|must set|validation" lectures/AGENTS.md contributions/AGENTS.md
```

Expected: only prose explaining that fields are *not* required. Any rule
demanding a field contradicts the design and should be softened.

- [ ] **Step 6: Report**

Summarise for the user: decks moved, files deleted/untracked, the Quarto
version before and after, and anything that differed in the screenshots. Do not
claim success on any step whose command was not actually run.

---

## Notes for the implementer

- **`nrf.png` does not exist.** Both `_metadata.yml` files ship with that line
  commented out. Do not uncomment it, and do not download a logo — the user is
  supplying the file. A broken image on every title slide is the failure mode.
- **The kremetart deck's date is unconfirmed.** Task 4 Step 5 uses a placeholder.
  Ask the user rather than shipping a guessed date.
- **`kremetart-pipeline/index.qmd` uses raw `<video>` tags** where the house
  rule calls for `{{< video >}}`. One is a full-slide background video the
  shortcode cannot express and is justified; the other is not. Out of scope —
  do not fix it here.
- **Screenshots always show the pre-fragment state.** Fragment URLs cannot be
  driven from the command line. Title slides have no fragments, so the
  verification in this plan is unaffected.
