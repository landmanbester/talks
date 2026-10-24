#!/usr/bin/env python3
"""Restore a restoring beam to a FITS header that lost it.

Montage drops `BMAJ`/`BMIN`/`BPA` when it reprojects and coadds, so an
image-space mosaic built with it arrives with no record of its own resolution.
Nothing downstream can tell: the image still displays, still has a WCS, and
still differences against another image without complaint -- it just silently
compares Jy/beam values measured with different beams, which is not a comparison
of anything. The values have to come from the inputs that went into the mosaic.

    PY="uv run"   # repo env, see pyproject.toml

    $PY scripts/figures/stamp_beam.py IMAGE.fits \
        --bmaj 0.002111010951921344 --bmin 0.001486398930691199 --bpa 5.3e-07 \
        --source "input images to the montage mosaic"

`--bmaj/--bmin` are degrees by default, matching the FITS convention and so the
value pasted straight out of an input header. Use `--arcsec` for arcseconds.

The edit is header-only and in place. The data array is hashed before and after
and the run aborts if it changed, because a header rewrite that needs an extra
2880-byte block moves every byte of the data and is worth being sure about.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

import numpy as np
from astropy.io import fits

BEAM_KEYS = ("BMAJ", "BMIN", "BPA")


def die(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    sys.exit(f"error: {msg}")


def data_digest(path: Path, hdu: int) -> str:
    """SHA-256 of the raw data array, read in chunks to bound memory."""
    h = hashlib.sha256()
    with fits.open(path, memmap=True) as hdul:
        arr = hdul[hdu].data
        if arr is None:
            die(f"{path}[{hdu}] has no data")
        flat = arr.reshape(-1)
        step = max(1, 64 * 1024 * 1024 // flat.dtype.itemsize)
        for i in range(0, flat.size, step):
            h.update(np.ascontiguousarray(flat[i:i + step]).tobytes())
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image", type=Path)
    ap.add_argument("--bmaj", type=float, required=True, help="beam major axis")
    ap.add_argument("--bmin", type=float, required=True, help="beam minor axis")
    ap.add_argument("--bpa", type=float, default=0.0, help="position angle, degrees")
    ap.add_argument("--arcsec", action="store_true",
                    help="--bmaj/--bmin are arcseconds rather than degrees")
    ap.add_argument("--bunit", help="also set BUNIT, e.g. Jy/beam")
    ap.add_argument("--source", default="",
                    help="where the values came from, recorded as HISTORY")
    ap.add_argument("--hdu", type=int, default=0)
    ap.add_argument("--force", action="store_true",
                    help="overwrite a beam that is already present")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-verify", action="store_true",
                    help="skip the before/after data hash (it reads the file twice)")
    args = ap.parse_args()

    path = args.image
    if not path.is_file():
        die(f"no such file: {path}")

    scale = 1.0 / 3600.0 if args.arcsec else 1.0
    bmaj, bmin = args.bmaj * scale, args.bmin * scale
    if bmin > bmaj:
        die(f"BMIN ({bmin}) exceeds BMAJ ({bmaj}) -- axes look swapped")

    with fits.open(path, memmap=True) as hdul:
        hdr = hdul[args.hdu].header
        existing = {k: hdr[k] for k in BEAM_KEYS if k in hdr}
        cards_before = len(hdr)
        blocks_before = len(hdr.tostring()) / 2880

    if existing and not args.force:
        die(f"{path} already has {existing} -- pass --force to overwrite")

    print(f"{path.name}")
    print(f"  beam -> {bmaj * 3600:.4f}\" x {bmin * 3600:.4f}\" @ {args.bpa:g} deg")
    print(f"  header: {cards_before} cards, {blocks_before:.2f} block(s) of 36")

    if args.dry_run:
        print("  (dry run -- nothing written)")
        return 0

    before = None if args.no_verify else data_digest(path, args.hdu)

    t0 = time.time()
    with fits.open(path, mode="update", memmap=True) as hdul:
        hdr = hdul[args.hdu].header
        hdr["BMAJ"] = (bmaj, "beam major axis (deg)")
        hdr["BMIN"] = (bmin, "beam minor axis (deg)")
        hdr["BPA"] = (args.bpa, "beam position angle (deg)")
        if args.bunit:
            hdr["BUNIT"] = (args.bunit, "brightness unit")
        # Provenance in the file itself. A beam restored by hand is a different
        # kind of fact from one written by the imager, and six months later
        # nothing outside this HISTORY block would say which this was.
        hdr.add_history("Beam keywords restored by scripts/figures/stamp_beam.py")
        if args.source:
            hdr.add_history(f"BMAJ/BMIN/BPA taken from {args.source}")
        hdr.add_history("Montage does not propagate beam keywords through a mosaic")
        hdul.flush()
    print(f"  written in {time.time() - t0:.1f}s")

    with fits.open(path, memmap=True) as hdul:
        hdr = hdul[args.hdu].header
        got = {k: hdr.get(k) for k in BEAM_KEYS}
        blocks_after = len(hdr.tostring()) / 2880
    print(f"  header now: {len(hdr)} cards, {blocks_after:.2f} block(s)")
    if abs(got["BMAJ"] - bmaj) > 1e-15 or abs(got["BMIN"] - bmin) > 1e-15:
        die(f"readback mismatch: {got}")

    if before is not None:
        after = data_digest(path, args.hdu)
        if after != before:
            die("DATA CHANGED -- the pixel values are not what they were. "
                f"before {before[:16]} after {after[:16]}")
        print(f"  data unchanged (sha256 {after[:16]}...)")

    print("  ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
