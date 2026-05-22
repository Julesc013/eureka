#!/usr/bin/env python3
"""Render a read-only Workbench SCOUT console view model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_eval.scout_schema import (  # noqa: E402
    PROJECTION_PROFILES,
    build_scout_console_view,
    load_scout_example_records,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="examples/scout/scout_seed_manifest.json")
    parser.add_argument(
        "--projection",
        choices=PROJECTION_PROFILES,
        default="operator_workbench",
        help="Projection profile.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--output", help="Optional output path.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    records = load_scout_example_records(root)
    view = build_scout_console_view(records, args.projection)
    text = json.dumps(view, indent=2, sort_keys=True)

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(text, file=stdout)
    else:
        print(f"SCOUT console view: {view['projection_profile']}", file=stdout)
        print(f"read_only: {view['read_only']}", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
