#!/usr/bin/env python3
"""Smoke public alpha route metadata from committed examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.public_alpha import smoke_public_alpha_routes_from_examples  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-examples", action="store_true", help="Use committed public-alpha route metadata.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if not args.from_examples:
        parser.error("--from-examples is required")
    result = smoke_public_alpha_routes_from_examples()
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["route_smoke_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
