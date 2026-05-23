#!/usr/bin/env python3
"""Render a read-only Workbench DOMAIN console view model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.eval.domain_packs import (
    PROJECTION_PROFILES,
    build_domain_console_view,
    load_domain_packs_from_manifest,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", required=True, help="DOMAIN id to render.")
    parser.add_argument(
        "--projection",
        choices=PROJECTION_PROFILES,
        default="operator_workbench",
        help="Projection profile.",
    )
    parser.add_argument("--manifest", default="examples/domain/domain_seed_manifest.json")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--output", help="Optional output path.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = root / manifest_path
    packs = {str(pack.get("domain_id", "")): pack for pack in load_domain_packs_from_manifest(manifest_path)}
    if args.domain not in packs:
        print(f"unknown DOMAIN id: {args.domain}", file=sys.stderr)
        return 2
    view = build_domain_console_view(packs[args.domain], args.projection)
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
        print(f"DOMAIN console view: {view['domain_id']} ({view['projection_profile']})", file=stdout)
        print(f"read_only: {view['read_only']}", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
