# Contributions — Agent Context

> Rules for conference and workshop talks. `CLAUDE.md` and `GEMINI.md` are symlinks to this file.
> The repository-wide conventions in `../AGENTS.md` still apply — this file
> covers only what is specific to contributions.

## What a contribution is

A talk given once, at a named event, on a specific date. It is a record as much
as a deliverable: the version presented is the version kept.

## Front matter

`contributions/_metadata.yml` supplies theme, revealjs options, title
background, logos, and author. It deliberately supplies **no date**.

```yaml
---
title: "KREMETART"
subtitle: "Streaming calibration, imaging & transient detection for TART"
institute: "SARAO / Rhodes"
date: "2026-08-11"
event: "SARAO Postgraduate Bursary Conference"
location: "Cape Town, South Africa"
---
```

- `date:` is the date of the **event**, hard-coded. This inverts the lecture
  rule. `date: today` is wrong here — it would relabel an old talk every time
  the site rebuilds.
- `institute:` is your own affiliation, not the venue. The venue is `event:`.
- `event:` and `location:` appear on the title slide and in the root listing.

**Nothing is required.** A contribution with only a `title:` renders, appears
in the listing with blank cells, and the site builds. These fields are worth
setting because they populate the listing and title slide, not because anything
enforces them. Never add validation.

If a date is genuinely unknown, leave it out — a blank cell is honest. Do not
guess, and do not fall back to `today`.

## Style

Conference slots are short and the room is large.

- Budget slides against the slot: a 15-minute contributed talk is a different
  object from a 45-minute lecture. When it does not fit, **split or cut** — do
  not shrink the font
- Read from the back of a hall: fewer equations per slide, larger figures
- One idea per slide; put the derivation in the paper, not the deck

## Logos

The institutional strip is inherited. Note `assets/logos/sarao_logo.jpg` is
already a combined NRF + SARAO lockup, so the inherited pair covers NRF, SARAO,
and Rhodes.

A contribution **appends** its event's logos by redeclaring the whole list in
its own front matter — YAML lists replace rather than merge:

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

A deck that cites nothing needs neither the file nor the key. For citation
syntax beyond the above, consult standard Quarto citations documentation.

## Delivery

These matter for a live talk and are worth setting up before the room fills:

- **Speaker notes** — `::: {.notes}` blocks, visible only in presenter view
  (`S` during the presentation). Keep the narration with the slide it belongs
  to; the `.qmd` stays the single source of truth for the talk
- **Presenter view** shows notes, next slide, and a timer — check the timer
  against the slot before presenting
- **Chalkboard** (`C`) and **pointer** (`B`) are available for questions, when
  someone asks about a detail no slide covers
