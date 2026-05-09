#!/usr/bin/env python3
"""Build the tiny tar_basic extraction fixture in this directory."""

from __future__ import annotations

import io
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "tar_basic.tar"


def add_text(archive: tarfile.TarFile, name: str, text: str) -> None:
    data = text.encode("utf-8")
    info = tarfile.TarInfo(name)
    info.size = len(data)
    archive.addfile(info, io.BytesIO(data))


def main() -> int:
    with tarfile.open(OUT, "w") as archive:
        add_text(archive, "README.txt", "Synthetic tar fixture readme.\n")
        add_text(archive, "metadata/notes.txt", "Tar listing fixture; no payload execution.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
