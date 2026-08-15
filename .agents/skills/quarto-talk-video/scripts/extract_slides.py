#!/usr/bin/env python3
"""Render a Quarto revealjs deck to numbered PNG frames, one per fragment step.

Replaces the decktape route, which does not work here: puppeteer's `page.pdf()`
crashes with "Attempted to use detached Frame" against current Chrome, and on
Ubuntu 24.04+ its bundled Chromium additionally cannot start because
`apparmor_restrict_unprivileged_userns=1` blocks the sandbox. This drives the
system Chrome directly instead, with no puppeteer in the picture.

Frames follow the live talk: arriving at a slide with nothing revealed is one
frame, and each fragment step is another. A slide with 3 fragment steps
therefore yields 4 frames. Pass --per-slide for one fully-revealed frame per
slide instead.

Reveal is configured with `fragmentInURL: false`, so fragment state cannot be
requested through the URL hash. The probe injected here calls
`Reveal.slide(h, v, f)` directly, which works regardless of that setting.

Usage:
    extract_slides.py <deck.html> <outdir> [WxH]
    extract_slides.py _site/contributions/my-talk/index.html _video/my-talk

Writes slide-01.png ... slide-NN.png plus frames.json, which maps each frame to
its slide heading and fragment step -- use it when writing the narration.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME = "google-chrome"
PROBE_NAME = "__extract_slides.html"

PROBE_JS = r"""
<style>
  /* Presentation chrome has no place in a submission video. */
  .reveal .slide-number, .reveal .controls, .reveal .progress,
  .reveal .slide-menu-button, .reveal .backarrow { display: none !important; }

  /* Kill every transition. Reveal fades fragments in over ~200ms, and under
     --virtual-time-budget the screenshot can land mid-fade -- which renders as
     a slide that is blank except for its heading, silently and only on the
     steps that reveal several fragments at once. With transitions off, the DOM
     state at capture time is exactly what is painted. */
  .reveal .slides section, .reveal .fragment, .reveal * {
    transition: none !important; animation: none !important;
  }
  .reveal .fragment.visible {
    opacity: 1 !important; visibility: visible !important;
  }
</style>
<script>
(function () {
  var GIVE_UP_MS = __GIVE_UP_MS__;
  var KEEP_EMPTY = __KEEP_EMPTY__;

  var fontsReady = !document.fonts;
  if (document.fonts) document.fonts.ready.then(function () { fontsReady = true; });

  var mathReady = false;
  (function awaitMath() {
    if (window.MathJax && MathJax.Hub && MathJax.Hub.Queue) {
      MathJax.Hub.Queue(function () { mathReady = true; });
    } else if (!window.MathJax && document.readyState === 'complete') {
      mathReady = true;
    } else {
      setTimeout(awaitMath, 100);
    }
  })();

  function headingOf(sec) {
    var h = sec.querySelector('h1, h2, h3');
    var t = h ? h.textContent.trim().replace(/\s+/g, ' ') : '';
    if (t) return t.slice(0, 80);
    if (sec.id) return '#' + sec.id;
    return '(untitled)';
  }

  // Fragments sharing a data-fragment-index reveal together, so the number of
  // steps is the number of distinct indices, not the number of elements.
  function fragmentSteps(sec) {
    var idx = {};
    sec.querySelectorAll('.fragment').forEach(function (f) {
      // Only fragments belonging to this slide, not to a nested one.
      if (f.closest('section') !== sec) return;
      var i = f.getAttribute('data-fragment-index');
      idx[i === null ? 'auto' : i] = true;
    });
    return Object.keys(idx).length;
  }

  // With nothing revealed, a slide whose whole body is fragmented renders as a
  // bare heading -- fine live, but in a video it is a blank card held for the
  // length of the narration. Slides with a background or any static content
  // still have a worthwhile opening frame.
  function hasOpeningFrame(sec) {
    if (sec.hasAttribute('data-background-image') ||
        sec.hasAttribute('data-background-video') ||
        sec.hasAttribute('data-background-color')) return true;
    var clone = sec.cloneNode(true);
    clone.querySelectorAll('h1, h2, h3, .fragment').forEach(function (n) {
      n.parentNode.removeChild(n);
    });
    if (clone.textContent.trim()) return true;
    return !!clone.querySelector('img, svg, video, canvas, table, pre');
  }

  function states() {
    var out = [];
    document.querySelectorAll('.reveal .slides > section').forEach(function (top, h) {
      var kids = top.querySelectorAll(':scope > section');
      var leaves = kids.length ? Array.prototype.slice.call(kids) : [top];
      leaves.forEach(function (sec, v) {
        var steps = fragmentSteps(sec);
        var title = headingOf(sec);
        var first = (steps > 0 && !KEEP_EMPTY && !hasOpeningFrame(sec)) ? 0 : -1;
        for (var f = first; f < steps; f++) {
          out.push({
            h: h, v: kids.length ? v : 0, f: f,
            anchor: kids.length ? h + '/' + v : String(h),
            step: f - first + 1, steps: steps - first, title: title
          });
        }
      });
    });
    return out;
  }

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
    var all = states();
    var m = /[?&]shot=(\d+)/.exec(location.search);

    if (!m) {
      var out = document.createElement('pre');
      out.id = '__extract_slides__';
      out.textContent = JSON.stringify({ settled: !!settled, states: all });
      document.body.appendChild(out);
      return;
    }

    var s = all[parseInt(m[1], 10)];
    if (!s) return;
    // Reveal.slide's third argument is the fragment index; -1 shows none.
    Reveal.slide(s.h, s.v, s.f);
  });
})();
</script>
"""


def die(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    sys.exit(f"error: {msg}")


def chrome(args: list[str], timeout_ms: int) -> str:
    """Run headless Chrome once, in its own throwaway profile.

    --no-sandbox is required on Ubuntu 24.04+, where
    apparmor_restrict_unprivileged_userns blocks Chrome's own sandbox.

    The profile must NOT be shared between invocations: a second Chrome pointed
    at a live profile hits the singleton lock and silently screenshots stale
    page state, which shows up as duplicate frames. Chrome also keeps flushing
    the profile after exit, so cleanup is best-effort rather than a
    TemporaryDirectory context manager, which races it and raises.
    """
    profile = tempfile.mkdtemp(prefix="extract-slides-")
    try:
        return subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
             f"--user-data-dir={profile}", *args],
            capture_output=True, text=True, timeout=timeout_ms / 1000 + 60,
        ).stdout
    except FileNotFoundError:
        die(f"{CHROME} not found on PATH")
    except subprocess.TimeoutExpired:
        die("chrome timed out")
    finally:
        shutil.rmtree(profile, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck", type=Path, help="rendered deck index.html under _site/")
    ap.add_argument("outdir", type=Path, help="build dir, e.g. _video/<slug>")
    ap.add_argument("size", nargs="?", default="1920x1080", help="WxH (default 1920x1080)")
    ap.add_argument("--keep-empty-intro", action="store_true",
                    help="keep the nothing-revealed frame even when it renders as "
                         "a bare heading (default: skip it)")
    ap.add_argument("--per-slide", action="store_true",
                    help="one fully-revealed frame per slide instead of per fragment step")
    ap.add_argument("--timeout", type=int, default=15000, metavar="MS",
                    help="per-page virtual time budget (default 15000)")
    args = ap.parse_args()

    if not shutil.which(CHROME):
        die(f"{CHROME} not found on PATH")
    if not args.deck.is_file():
        die(f"no such file: {args.deck}")
    args.deck = args.deck.resolve()   # file:// URIs need an absolute path
    try:
        w, h = (int(x) for x in args.size.lower().split("x"))
    except ValueError:
        die(f"bad size {args.size!r}, expected WxH like 1920x1080")

    probe = args.deck.parent / PROBE_NAME
    source = args.deck.read_text(encoding="utf-8")
    if "</body>" not in source:
        die(f"{args.deck} has no </body> to inject into")
    probe.write_text(
        source.replace("</body>",
                       PROBE_JS
                       .replace("__GIVE_UP_MS__", str(int(args.timeout * 0.5)))
                       .replace("__KEEP_EMPTY__",
                                "true" if args.keep_empty_intro else "false")
                       + "</body>"),
        encoding="utf-8")

    try:
        # Pass 1: enumerate the states to shoot.
        dom = chrome([f"--window-size={w},{h}",
                      f"--virtual-time-budget={args.timeout}",
                      "--dump-dom", probe.as_uri()], args.timeout)
        m = re.search(r'<pre id="__extract_slides__">(.*?)</pre>', dom, re.S)
        if not m:
            die("probe did not report -- open the deck in a browser to check it loads")
        report = json.loads(html.unescape(m.group(1)))
        if not report["settled"]:
            die("reveal/MathJax had not settled; raise --timeout")

        states = report["states"]
        # The probe indexes into its own full enumeration, so each state has to
        # carry that index through any filtering done here.
        for i, s in enumerate(states):
            s["probe_index"] = i
        if args.per_slide:
            # Keep only the last step of each slide: everything revealed.
            by_slide: dict[str, dict] = {}
            for s in states:
                by_slide[s["anchor"]] = s
            states = list(by_slide.values())

        args.outdir.mkdir(parents=True, exist_ok=True)
        for stale in args.outdir.glob("slide-*.png"):
            stale.unlink()

        # Pass 2: one Chrome per state. Slower than a single navigating session,
        # but every frame is independent, so one bad slide cannot truncate the
        # run the way decktape's sequential stepping does.
        print(f"Rendering {len(states)} frame(s) at {w}x{h} ...")
        frames = []
        for i, s in enumerate(states):
            png = args.outdir / f"slide-{i + 1:02d}.png"
            chrome([f"--screenshot={png}", f"--window-size={w},{h}",
                    f"--virtual-time-budget={args.timeout}",
                    f"{probe.as_uri()}?shot={s['probe_index']}"],
                   args.timeout)
            if not png.exists() or png.stat().st_size == 0:
                die(f"chrome produced no frame for state {i} ({s['title']})")
            dim = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0",
                 "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", str(png)],
                capture_output=True, text=True).stdout.strip()
            if dim != f"{w}x{h}":
                die(f"{png.name} is {dim}, expected {w}x{h}")
            frames.append({"frame": png.name, **s})
            print(f"  {png.name}  {s['title'][:44]:<44} step {s['step']}/{s['steps']}")
    finally:
        probe.unlink(missing_ok=True)

    # Identical consecutive frames mean a state was never applied -- the failure
    # mode when Chrome screenshots stale page content. It is invisible until the
    # finished video shows the same slide twice, so fail here instead.
    dupes = []
    for prev, cur in zip(frames, frames[1:]):
        a = hashlib.md5((args.outdir / prev["frame"]).read_bytes()).hexdigest()
        b = hashlib.md5((args.outdir / cur["frame"]).read_bytes()).hexdigest()
        if a == b:
            dupes.append((prev["frame"], cur["frame"], cur["title"]))
    if dupes:
        for a, b, title in dupes:
            print(f"  DUPLICATE {a} == {b}  ({title})", file=sys.stderr)
        die(f"{len(dupes)} consecutive frame pair(s) are byte-identical, so those "
            "states never rendered. Re-run; if it persists, check the deck for "
            "fragments that reveal nothing visible.")

    (args.outdir / "frames.json").write_text(json.dumps(frames, indent=2), encoding="utf-8")
    print(f"\nWrote {len(frames)} frame(s) + frames.json to {args.outdir}")
    print("NEXT: eyeball 2-3 frames and confirm the count matches your slide count.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
