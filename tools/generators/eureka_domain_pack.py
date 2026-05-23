#!/usr/bin/env python3
"""List and validate DOMAIN seed packs."""

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
    load_domain_packs_from_manifest,
    load_domain_seed_manifest,
    validate_domain_pack,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="examples/domain/domain_seed_manifest.json")
    parser.add_argument("--list", action="store_true", help="List DOMAIN seed pack ids.")
    parser.add_argument("--validate", action="store_true", help="Validate every pack in the manifest.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = root / manifest_path
    manifest = load_domain_seed_manifest(manifest_path)
    packs = load_domain_packs_from_manifest(manifest_path)
    reports = [validate_domain_pack(pack) for pack in packs] if args.validate else []
    result = {
        "schema_version": "domain_pack_cli_result.v0",
        "manifest": str(manifest_path.relative_to(root) if manifest_path.is_relative_to(root) else manifest_path),
        "domain_ids": [str(pack.get("domain_id", "")) for pack in packs],
        "domain_count": len(packs),
        "manifest_seed_status": manifest.get("seed_status", ""),
        "validation_requested": bool(args.validate),
        "validation_passed": all(report["status"] == "valid" for report in reports) if reports else None,
        "validation_reports": reports,
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    elif args.list:
        for domain_id in result["domain_ids"]:
            print(domain_id, file=stdout)
    else:
        print("DOMAIN seed packs", file=stdout)
        print(f"count: {result['domain_count']}", file=stdout)
        if args.validate:
            print(f"validation_passed: {result['validation_passed']}", file=stdout)
    return 0 if not reports or bool(result["validation_passed"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
