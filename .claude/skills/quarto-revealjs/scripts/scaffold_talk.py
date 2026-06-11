#!/usr/bin/env python3
"""Scaffold a new Quarto revealjs talk directory."""

import argparse
import os
from pathlib import Path
from textwrap import dedent


def scaffold_talk(
    title: str,
    author: str = "Landman Bester",
    event: str = "",
    output: str | None = None,
    theme_path: str = "dark-academic.scss",
    logo_path: str = "",
    footer: str = "",
    standalone: bool = False,
):
    """Create a new talk directory with index.qmd and supporting files."""
    if output is None:
        slug = title.lower().replace(" ", "-").replace(",", "")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        output = slug

    out_path = Path(output)
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "images").mkdir(exist_ok=True)

    # Determine theme reference
    if standalone:
        # Copy theme into talk directory
        theme_ref = "dark-academic.scss"
    else:
        theme_ref = theme_path

    # Build YAML front matter
    institute_line = f'\ninstitute: "{event}"' if event else ""
    logo_line = f"\n    logo: {logo_path}" if logo_path else ""
    footer_line = f'\n    footer: "{footer}"' if footer else ""

    qmd_content = dedent(f"""\
    ---
    title: "{title}"
    author: "{author}"
    date: today{institute_line}
    format:
      revealjs:
        theme: [dark, {theme_ref}]
        slide-number: true
        code-line-numbers: false
        code-copy: true
        highlight-style: monokai
        center: true
        transition: slide
        mermaid-format: svg{logo_line}{footer_line}
        css: custom.css
        title-slide-attributes:
          data-background-image: images/meerkat-milkyway.jpg
          data-background-opacity: "0.5"
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

    ## Code Example

    ```python
    import jax.numpy as jnp

    def fft_matvec(c, x):
        return jnp.fft.ifft(jnp.fft.fft(c) * jnp.fft.fft(x)).real
    ```

    ---

    ## {{background-color="#0d1117"}}

    ::: {{.closing-slide}}
    ## Thanks!

    ::: {{.contact}}
    {author.lower().replace(" ", ".")}@sarao.ac.za
    :::
    :::
    """)

    (out_path / "index.qmd").write_text(qmd_content)

    # Create custom.css to fix Quarto's injected scrollbar on code blocks
    custom_css = dedent("""\
    /* Quarto injects `.reveal div.sourceCode { overflow: auto; }` which adds
       a cosmetic horizontal scrollbar even when code fits. Override it. */
    .reveal div.sourceCode { overflow-x: hidden !important; }
    """)
    (out_path / "custom.css").write_text(custom_css)

    print(f"Created talk scaffold at: {out_path}/")
    print(f"  index.qmd   — edit this file")
    print(f"  custom.css  — fixes Quarto's code block scrollbar bug")
    print(f"  images/     — put images here")
    print(f"\nNote: copy meerkat-milkyway.jpg into images/ for the title background.")
    print(f"  cp ../assets/logos/meerkat-milkyway.jpg {out_path}/images/")
    print(f"\nTo render: cd {out_path} && quarto render index.qmd")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new Quarto revealjs talk"
    )
    parser.add_argument("title", help="Talk title")
    parser.add_argument("--author", default="Landman Bester")
    parser.add_argument("--event", default="")
    parser.add_argument("--output", default=None, help="Output directory path")
    parser.add_argument(
        "--theme", default="../templates/dark-academic.scss",
        help="Path to SCSS theme (relative to the talk directory)"
    )
    parser.add_argument("--logo", default="", help="Path to logo image")
    parser.add_argument("--footer", default="", help="Footer text (omit by default — takes up space on dense slides)")
    parser.add_argument(
        "--standalone", action="store_true",
        help="Create a self-contained talk (copy theme into directory)"
    )

    args = parser.parse_args()
    scaffold_talk(
        title=args.title,
        author=args.author,
        event=args.event,
        output=args.output,
        theme_path=args.theme,
        logo_path=args.logo,
        footer=args.footer,
        standalone=args.standalone,
    )


if __name__ == "__main__":
    main()
