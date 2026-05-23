#!/usr/bin/env python3
"""Build the read-only G0 Workbench quality console view."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.eval.g0_quality import PROJECTION_PROFILES, build_quality_console_view, load_quality_fixture  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", default="examples/search/quality/sample_quality_fixture.json")
    parser.add_argument("--projection", choices=PROJECTION_PROFILES, default="operator_workbench")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    view = build_quality_console_view(load_quality_fixture(args.fixture), args.projection)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(view, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(view, indent=2, sort_keys=True) if args.json else f"G0 quality console {args.projection}", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
