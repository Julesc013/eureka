#!/usr/bin/env python3
"""Build the tiny zip_manifest extraction fixture in this directory."""

from __future__ import annotations

import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "zip_manifest.zip"


def main() -> int:
    manifest = {
        "name": "synthetic-eureka-fixture",
        "version": "0.0.1",
        "description": "Fixture manifest for extraction candidate previews.",
        "files": ["README.txt", "package.json"],
    }
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("README.txt", "Synthetic fixture with a manifest-like member.\n")
        archive.writestr("package.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
