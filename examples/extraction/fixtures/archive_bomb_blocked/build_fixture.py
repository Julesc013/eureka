#!/usr/bin/env python3
"""Build a tiny ZIP fixture that trips the compression-ratio guard."""

from __future__ import annotations

from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "archive_bomb_blocked.zip"


def main() -> int:
    repeated = "A" * 4096
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.writestr("repeated.txt", repeated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
