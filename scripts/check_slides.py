#!/usr/bin/env python3
"""Find slides whose content overflows the deck, and shoot them fully revealed.

Two jobs that share the same trick:

  1. Overflow detection. Reveal lays every slide out at a fixed logical size
     (1050x700 by default) and scales that to the window. Measuring
     `offsetHeight` per slide turns "eyeball 30 screenshots" into "here are the
     3 that are too tall", and separates slides that merely crowd the frame
     (over the design height) from ones actually cut off (over height/0.9,
     where 0.9 is what reveal's `margin: 0.1` leaves for content).

  2. Screenshots with every fragment revealed. AGENTS.md used to prescribe
     hand-editing `fragments: false` into the deck's front matter, rendering,
     shooting, then removing it again -- a ritual that ships a broken deck if it
     is interrupted halfway. This forces `.fragment` elements visible in the
     browser instead, so the source tree is never touched.

Both work by writing a probe copy of the *rendered* deck into `_site/`, which is
generated and gitignored. Deck sources are only ever read.

Usage:
    scripts/check_slides.py                        # render, then check every deck
    scripts/check_slides.py --no-render            # reuse the existing _site build
    scripts/check_slides.py --no-render deconvolution
    scripts/check_slides.py --no-render --shots /data/tmp/shots stimela-fundamentals

Exits 1 if any slide overflows, so it can gate a commit or a CI job.
"""

from __future__ import annotations

import argparse
import functools
import html
import http.server
import json
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
CHROME = "google-chrome"
PROBE_NAME = "__check_slides.html"

# Injected into the rendered deck. Waits for Reveal (and MathJax, which resizes
# equations late and would otherwise be measured mid-typeset), forces fragments
# visible when asked, then measures every leaf slide and parks the result in the
# DOM where --dump-dom can retrieve it.
PROBE_JS = r"""
<script>
(function () {
  var REVEAL_FRAGMENTS = __REVEAL_FRAGMENTS__;
  // Must stay comfortably under Chrome's --virtual-time-budget: if the probe is
  // still polling when the budget expires, --dump-dom fires with no report and
  // the whole deck looks like a load failure.
  var GIVE_UP_MS = __GIVE_UP_MS__;

  function revealFragments() {
    // Reveal hides fragments with visibility:hidden, so they already occupy
    // layout space -- this is purely so screenshots show the final state.
    document.querySelectorAll('.reveal .fragment').forEach(function (f) {
      f.classList.add('visible');
      f.classList.remove('current-fragment');
    });
  }

  function headingOf(sec) {
    var h = sec.querySelector('h1, h2, h3');
    var t = h ? h.textContent.trim().replace(/\s+/g, ' ') : '';
    if (t) return t.slice(0, 60);
    // Background-image slides often carry an empty heading, so fall back to the
    // anchor Quarto generated -- still enough to find the slide in the .qmd.
    if (sec.id) return '#' + sec.id;
    t = sec.textContent.trim().replace(/\s+/g, ' ');
    return t ? t.slice(0, 40) + '...' : '(untitled)';
  }

  function measure(settled) {
    var cfg = (window.Reveal && Reveal.getConfig) ? Reveal.getConfig() : {};
    var limit = cfg.height || 700;

    // Reveal scales the deck to fit the window, so the design height is not the
    // clipping point. `margin: 0.1` keeps a 10% frame, and content is free to
    // grow into it: visible logical height is height/0.9 ~= 778px, and measuring
    // confirms that holds at 1050x700, 1600x900, 1920x1080 and 2560x1440 alike.
    // So past `limit` a slide is merely cramped -- it touches the frame edge --
    // while past `clipAt` it is genuinely cut off.
    var scale = (window.Reveal && Reveal.getScale) ? Reveal.getScale() : 1;
    var clipAt = scale > 0 ? window.innerHeight / scale : limit;
    var slides = [];

    // Top-level sections are horizontal positions. A section containing further
    // sections is a `.stack` wrapper -- it is not itself a slide, and measuring
    // it would report the sum of its children.
    var tops = document.querySelectorAll('.reveal .slides > section');
    tops.forEach(function (top, h) {
      var kids = top.querySelectorAll(':scope > section');
      var leaves = kids.length ? Array.prototype.slice.call(kids) : [top];
      leaves.forEach(function (sec, v) {
        slides.push({
          h: h,
          v: kids.length ? v : 0,
          anchor: kids.length ? h + '/' + v : String(h),
          title: headingOf(sec),
          height: sec.offsetHeight,
          // Nothing but hidden elements (a .plain-figure heading over a
          // background video): 0px is the right answer, not a missed layout.
          empty: Array.prototype.every.call(sec.children, function (el) {
            return getComputedStyle(el).display === 'none';
          })
        });
      });
    });

    var out = document.createElement('pre');
    out.id = '__check_slides__';
    out.textContent = JSON.stringify({
      limit: limit,
      clipAt: Math.round(clipAt),
      scale: scale,
      innerHeight: window.innerHeight,
      settled: !!settled,
      slides: slides
    });
    document.body.appendChild(out);
  }

  // Web fonts change text metrics when they swap in, and MathJax 2 typesets
  // asynchronously off a CDN. Both move slide heights by ~20px, which is enough
  // to flip a borderline slide in and out of the report between runs.
  var fontsReady = !document.fonts;
  if (document.fonts) document.fonts.ready.then(function () { fontsReady = true; });

  var mathReady = false;
  (function awaitMath() {
    if (window.MathJax && MathJax.Hub && MathJax.Hub.Queue) {
      // Pushing onto MathJax's own queue is the only reliable "typesetting is
      // finished" signal; inspecting queue.pending reports 0 too early.
      MathJax.Hub.Queue(function () { mathReady = true; });
    } else if (!window.MathJax && document.readyState === 'complete') {
      mathReady = true;   // deck has no maths
    } else {
      setTimeout(awaitMath, 100);
    }
  })();

  function layoutSignature() {
    var sum = 0;
    document.querySelectorAll('.reveal .slides section').forEach(function (s) {
      sum += s.offsetHeight;
    });
    return window.innerHeight + ':' + sum;
  }

  function ready(cb) {
    var waited = 0, lastSig = '', stable = 0;
    (function poll() {
      var revealUp = window.Reveal && (!Reveal.isReady || Reveal.isReady());
      // Chrome reports innerHeight 0 until it has sized the window, and Reveal
      // sits at its minScale floor until it has laid out. Rather than guess at
      // every input, wait for the thing being measured to stop moving.
      var sig = layoutSignature();
      stable = (window.innerHeight > 0 && sig === lastSig) ? stable + 1 : 0;
      lastSig = sig;
      var settled = revealUp && mathReady && fontsReady && stable >= 2;
      if (settled || waited > GIVE_UP_MS) return cb(settled);
      waited += 250;
      setTimeout(poll, 250);
    })();
  }

  ready(function (settled) {
    // Reveal only lays out slides within `viewDistance` (default 3) of the
    // current one and sets display:none on the rest, which measures as height
    // 0 -- i.e. silently "fits". Without this, only the first few slides of a
    // deck are ever really checked.
    if (window.Reveal && Reveal.configure) {
      Reveal.configure({ viewDistance: 999, mobileViewDistance: 999 });
    }
    // Always reveal fragments when measuring: overflow that only appears after
    // the last fragment is the case worth catching.
    revealFragments();
    // One more beat for the reflow that laying out every slide, revealing
    // fragments, and typesetting maths can trigger.
    setTimeout(function () { measure(settled); }, 1500);
  });
})();
</script>
"""


def die(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    sys.exit(f"error: {msg}")


def find_decks(names: list[str]) -> list[Path]:
    """Locate rendered decks under _site, optionally filtered by slug."""
    found = sorted(p for p in SITE.glob("*/*/index.html"))
    if not found:
        die(f"no rendered decks under {SITE}. Run without --no-render first.")
    if not names:
        return found
    picked = []
    for name in names:
        matches = [p for p in found if name in str(p.parent.relative_to(SITE))]
        if not matches:
            die(f"no deck matching {name!r}. Available: "
                + ", ".join(p.parent.name for p in found))
        picked.extend(matches)
    return sorted(set(picked))


def build_probe_js(reveal_fragments: bool, timeout: int) -> str:
    """Fill in the probe's compile-time constants."""
    return (PROBE_JS
            .replace("__REVEAL_FRAGMENTS__", "true" if reveal_fragments else "false")
            # Half the budget: the probe still needs time to measure and for
            # Chrome to serialise the DOM after it reports.
            .replace("__GIVE_UP_MS__", str(int(timeout * 0.5))))


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class _QuietServer(http.server.ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        pass   # Chrome drops connections (media range requests) on exit


@functools.cache
def _server() -> _QuietServer:
    """Serve _site/ on a free local port for the life of this run.

    Decks are loaded over HTTP, not file://: Quarto's OJS bootstrap raises an
    alert() on file:// URLs, and a modal blocks headless Chrome until it times out.
    """
    handler = functools.partial(_QuietHandler, directory=str(SITE))
    srv = _QuietServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def probe_url(probe: Path) -> str:
    return (f"http://127.0.0.1:{_server().server_port}/"
            f"{probe.relative_to(SITE).as_posix()}")


def probe_source(deck: Path, js: str, keep_video: bool) -> str:
    """The deck's HTML with the probe injected.

    Autoslide (manim-slides segments run into their hold loops) would move the
    deck under the probe, so it goes. Background videos never affect layout,
    and with every slide preloaded a deck of segments loads dozens of them and
    the budget runs out -- the measuring pass drops them; screenshots keep them.
    """
    source = deck.read_text(encoding="utf-8")
    if "</body>" not in source:
        die(f"{deck} has no </body> to inject into")
    attrs = r"autoslide" if keep_video else r"background-video[\w-]*|autoslide"
    source = re.sub(rf'\sdata-(?:{attrs})="[^"]*"', "", source)
    return source.replace("</body>", js + "</body>")


def run_probe(deck: Path, reveal_fragments: bool, timeout: int, window: str,
              _retry: bool = True) -> dict:
    """Inject the probe into a copy of the deck and read back its report."""
    probe = deck.parent / PROBE_NAME
    js = build_probe_js(reveal_fragments, timeout)
    probe.write_text(probe_source(deck, js, keep_video=False), encoding="utf-8")

    # Chrome writes a profile into the cwd unless told otherwise; keep it out of
    # the repo and out of whatever the user's real profile is.
    with tempfile.TemporaryDirectory() as profile:
        try:
            dom = subprocess.run(
                [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                 f"--user-data-dir={profile}",
                 f"--window-size={window.replace('x', ',')}",
                 f"--virtual-time-budget={timeout}",
                 "--dump-dom", probe_url(probe)],
                capture_output=True, text=True, timeout=timeout / 1000 + 60,
            ).stdout
        except FileNotFoundError:
            die(f"{CHROME} not found on PATH")
        except subprocess.TimeoutExpired:
            die(f"chrome timed out on {deck.parent.name}")
        finally:
            probe.unlink(missing_ok=True)

    m = re.search(r'<pre id="__check_slides__">(.*?)</pre>', dom, re.S)
    report = json.loads(html.unescape(m.group(1))) if m else None

    # Both failures below are the same underlying problem -- the page needed more
    # time than the budget allowed -- and both are intermittent, because MathJax
    # comes off a CDN. Retry once with a bigger budget before giving up.
    problem = None
    if report is None:
        problem = "probe did not report"
    elif not report.get("innerHeight"):
        # Chrome reports innerHeight 0 until it sizes the window; measuring then
        # gives a clipping threshold of 0 and flags every slide.
        problem = "chrome never sized the window"
    elif not report.get("settled"):
        problem = "reveal or MathJax had not settled"

    if problem:
        if _retry:
            return run_probe(deck, reveal_fragments, timeout * 3, window,
                             _retry=False)
        die(f"{deck.parent.name}: {problem}, even at --timeout {timeout}. "
            "Open the deck in a browser to check it loads.")
    return report


def shoot(deck: Path, slides: list[dict], outdir: Path, timeout: int,
          window: str) -> None:
    """Screenshot every slide of one deck with all fragments already revealed."""
    probe = deck.parent / PROBE_NAME
    js = build_probe_js(reveal_fragments=True, timeout=timeout)
    probe.write_text(probe_source(deck, js, keep_video=True), encoding="utf-8")
    slug = "-".join(deck.parent.relative_to(SITE).parts)
    outdir.mkdir(parents=True, exist_ok=True)

    try:
        with tempfile.TemporaryDirectory() as profile:
            for i, s in enumerate(slides, start=1):
                png = outdir / f"{slug}-{i:02d}-{s['anchor'].replace('/', '_')}.png"
                subprocess.run(
                    [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                     f"--user-data-dir={profile}",
                     f"--screenshot={png}",
                     f"--window-size={window.replace('x', ',')}",
                     f"--virtual-time-budget={timeout}",
                     f"{probe_url(probe)}#/{s['anchor']}"],
                    capture_output=True, timeout=timeout / 1000 + 60,
                )
                flag = "  <-- OVERFLOW" if s["over"] else ""
                print(f"    {png.name}{flag}")
    finally:
        probe.unlink(missing_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("decks", nargs="*",
                    help="deck slugs to check (default: all)")
    ap.add_argument("--no-render", action="store_true",
                    help="reuse the existing _site build")
    ap.add_argument("--shots", metavar="DIR",
                    help="also screenshot every slide, fragments revealed")
    ap.add_argument("--window", default="1920x1080", metavar="WxH",
                    help="screenshot viewport (default 1920x1080). Does not move "
                         "the clipping threshold -- reveal scales to fit, so that "
                         "is fixed by the deck margin.")
    ap.add_argument("--tolerance", type=int, default=8, metavar="PX",
                    help="slack before reporting, in logical px (default 8)")
    ap.add_argument("--strict", action="store_true",
                    help="also fail on slides over the design height, not just "
                         "on ones visibly cut off")
    ap.add_argument("--timeout", type=int, default=15000, metavar="MS",
                    help="per-page virtual time budget (default 15000)")
    args = ap.parse_args()

    if not shutil.which(CHROME):
        die(f"{CHROME} not found on PATH")

    if not args.no_render:
        print("--- rendering ---")
        if subprocess.run(["quarto", "render"], cwd=ROOT).returncode != 0:
            die("quarto render failed")

    decks = find_decks(args.decks)
    clipped_total = tight_total = 0
    limits: set[int] = set()

    for deck in decks:
        rel = deck.parent.relative_to(SITE)
        report = run_probe(deck, reveal_fragments=bool(args.shots),
                           timeout=args.timeout, window=args.window)
        slides, limit, clip_at = report["slides"], report["limit"], report["clipAt"]
        limits.add(limit)
        # A zero-height slide was never laid out, so it was never checked. That
        # is how this tool silently passed a clipped deck once already.
        unmeasured = [s for s in slides if s["height"] == 0 and not s.get("empty")]
        if unmeasured:
            die(f"{rel}: {len(unmeasured)} slide(s) measured 0px, so they were "
                "not checked at all. Raise --timeout and re-run.")
        for s in slides:
            s["over"] = s["height"] > clip_at + args.tolerance
            s["tight"] = not s["over"] and s["height"] > limit + args.tolerance

        clipped = [s for s in slides if s["over"]]
        tight = [s for s in slides if s["tight"]]
        clipped_total += len(clipped)
        tight_total += len(tight)

        bits = []
        if clipped:
            bits.append(f"{len(clipped)} CLIPPED")
        if tight:
            bits.append(f"{len(tight)} tight")
        status = ", ".join(bits) if bits else "ok"
        print(f"\n{rel}  ({len(slides)} slides, design {limit}px, "
              f"cut off past {clip_at}px) -- {status}")
        for s in clipped:
            print(f"  CLIPPED  #/{s['anchor']:<6} {s['height']:>4}px "
                  f"(+{s['height'] - clip_at} over visible)  {s['title']}")
        for s in tight:
            print(f"  tight    #/{s['anchor']:<6} {s['height']:>4}px "
                  f"(+{s['height'] - limit} over design)  {s['title']}")

        if args.shots:
            shoot(deck, slides, Path(args.shots), args.timeout, args.window)

    print(f"\n{'=' * 68}")
    if tight_total:
        # Decks may configure different heights, so only name a number when
        # every deck checked agrees on one.
        where = f"{limits.pop()}px design height" if len(limits) == 1 else "design height"
        print(f"{tight_total} slide(s) exceed the {where}. They are not cut off,\n"
              "  but they reach into the margin reveal keeps around the frame, so "
              "they read as cramped.")
    if clipped_total:
        print(f"{clipped_total} slide(s) are visibly cut off. "
              "See 'Fix overflow' in AGENTS.md.")
        return 1
    if tight_total and args.strict:
        return 1
    print("No slides are cut off.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
