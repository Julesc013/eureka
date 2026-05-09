#!/usr/bin/env python3
"""Build the tiny zip_basic extraction fixture in this directory."""

from __future__ import annotations

from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "zip_basic.zip"


def main() -> int:
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("README.txt", "Synthetic fixture readme for Tier 0 and Tier 1 listing.\n")
        archive.writestr("docs/notes.txt", "No executable payloads, downloads, or private data.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
