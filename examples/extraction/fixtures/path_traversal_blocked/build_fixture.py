#!/usr/bin/env python3
"""Build a tiny ZIP fixture with an intentionally unsafe member path."""

from __future__ import annotations

from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "path_traversal_blocked.zip"


def main() -> int:
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("../escape.txt", "This synthetic member exists only to test traversal blocking.\n")
        archive.writestr("safe/readme.txt", "Safe member kept beside the blocked traversal member.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
