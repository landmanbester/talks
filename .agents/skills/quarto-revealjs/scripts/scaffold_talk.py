#!/usr/bin/env python3
"""Scaffold a new Quarto revealjs talk directory.

Talks belong to one of two classes, and the class decides where the directory
lands and which rules apply to it:

    lecture      -> lectures/<slug>/       (undated, re-given)
    contribution -> contributions/<slug>/  (dated, given once at an event)

Shared front matter (theme, revealjs options, title background, logos, css)
lives in each class's `_metadata.yml`, so a scaffolded deck is deliberately
thin — it carries only what is specific to it.
"""

import argparse
from pathlib import Path
from textwrap import dedent

CLASS_DIRS = {"lecture": "lectures", "contribution": "contributions"}


def scaffold_talk(
    talk_class: str,
    title: str,
    institute: str = "",
    output: str | None = None,
):
    """Create a new talk directory with index.qmd and supporting files."""
    if output is None:
        slug = title.lower().replace(" ", "-").replace(",", "")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        output = f"{CLASS_DIRS[talk_class]}/{slug}"

    out_path = Path(output)
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "images").mkdir(exist_ok=True)

    # `institute` is the course/host for a lecture, and your own affiliation
    # for a contribution — the venue there is `event:`.
    institute_line = f'\ninstitute: "{institute}"' if institute else ""

    # Contributions are dated records of a talk given once. Nothing is
    # enforced, so these ship as empty stubs rather than required fields.
    if talk_class == "contribution":
        meta_lines = institute_line + (
            '\ndate: ""            # event date, e.g. "2026-06-18"'
            '\nevent: ""           # conference or workshop name'
            '\nlocation: ""        # city, country'
        )
    else:
        meta_lines = institute_line

    # NOTE: the template must be flush-left. An earlier version used dedent()
    # on a 4-space-indented template, but the interpolated {meta_lines}
    # had no indent, so dedent found no common prefix and emitted broken
    # (indented) YAML.
    qmd_content = f"""\
---
title: "{title}"{meta_lines}
---

## Introduction

<!-- Replace with your opening content -->

---

## Main Content

<!-- Your slides here -->

$$
y = Rx + \\epsilon, \\quad \\epsilon \\sim \\mathcal{{N}}(0, \\Sigma)
$$

. . .

This appears on click.

---

## Thanks! {{background-color="#0d1117" .closing-slide}}

::: {{.contact}}
landman.bester@gmail.com
:::
"""

    (out_path / "index.qmd").write_text(qmd_content)

    # custom.css is load-bearing: `css: custom.css` is hoisted into the class
    # _metadata.yml, so a deck without this file fails to render.
    custom_css = dedent("""\
    /* Quarto injects `.reveal div.sourceCode { overflow: auto; }` which adds
       a cosmetic horizontal scrollbar even when code fits. Override it. */
    .reveal div.sourceCode { overflow-x: hidden !important; }
    """)
    (out_path / "custom.css").write_text(custom_css)

    print(f"Created {talk_class} scaffold at: {out_path}/")
    print(f"  index.qmd   — edit this file")
    print(f"  custom.css  — required; fixes Quarto's code block scrollbar bug")
    print(f"  images/     — put images here")
    print(f"\nTheme, logos, and revealjs options come from "
          f"{CLASS_DIRS[talk_class]}/_metadata.yml — see "
          f"{CLASS_DIRS[talk_class]}/AGENTS.md for the class rules.")
    print(f"\nCopy the title background into images/:")
    print(f"  cp assets/logos/meerkat-milkyway.jpg {out_path}/images/")
    print(f"\nTo render: quarto render {out_path}/index.qmd")
    print(f"To preview: cd {out_path} && quarto preview index.qmd")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new Quarto revealjs talk"
    )
    parser.add_argument(
        "talk_class", choices=["lecture", "contribution"],
        help="lecture -> lectures/ (undated); contribution -> contributions/ (dated)"
    )
    parser.add_argument("title", help="Talk title")
    parser.add_argument(
        "--institute", default="",
        help="Course or host institution for a lecture; your own affiliation "
             "for a contribution"
    )
    parser.add_argument("--output", default=None, help="Output directory path")

    args = parser.parse_args()
    scaffold_talk(
        talk_class=args.talk_class,
        title=args.title,
        institute=args.institute,
        output=args.output,
    )


if __name__ == "__main__":
    main()
