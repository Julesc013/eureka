#!/usr/bin/env python3
"""Resolve Eureka workspace and local appliance instance paths."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance.errors import LocalInstancePathError
from runtime.local_appliance.paths import (
    describe_instance_layout,
    resolve_default_instance_root,
    resolve_instance_root,
    resolve_instances_root,
    resolve_legacy_sibling_instance_root,
    resolve_repo_root,
    resolve_workspace_root,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Optional explicit instance root to classify.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else resolve_repo_root()
    workspace_root = resolve_workspace_root(repo_root)
    try:
        current_root = resolve_instance_root(args.instance, repo_root)
        layout = describe_instance_layout(repo_root, current_root)
        result = {
            "schema_version": "eureka_resolved_paths.v0",
            "status": "pass",
            "repo_root": str(repo_root),
            "workspace_root": str(workspace_root),
            "preferred_instances_root": str(resolve_instances_root(workspace_root)),
            "preferred_default_instance_root": str(resolve_default_instance_root(repo_root)),
            "legacy_sibling_instance_root": str(resolve_legacy_sibling_instance_root(repo_root)),
            "supplied_instance_root": str(Path(args.instance).expanduser().resolve()) if args.instance else None,
            "current_instance_root": str(current_root),
            "layout_class": layout["layout_class"],
            "warnings": layout["warnings"],
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        }
    except LocalInstancePathError as exc:
        result = {
            "schema_version": "eureka_resolved_paths.v0",
            "status": "fail",
            "repo_root": str(repo_root),
            "workspace_root": str(workspace_root),
            "preferred_instances_root": str(resolve_instances_root(workspace_root)),
            "preferred_default_instance_root": str(resolve_default_instance_root(repo_root)),
            "legacy_sibling_instance_root": str(resolve_legacy_sibling_instance_root(repo_root)),
            "supplied_instance_root": str(args.instance) if args.instance else None,
            "error": "invalid_instance_root",
            "message": str(exc),
            "warnings": [],
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        }
    emit(result, args.json, stdout)
    if result["status"] != "pass":
        print(f"ERROR: {result['message']}", file=stderr)
        return 2
    return 0


def emit(result: dict, as_json: bool, stdout: TextIO) -> None:
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    print(f"repo_root: {result['repo_root']}", file=stdout)
    print(f"current_instance_root: {result.get('current_instance_root', '')}", file=stdout)
    print(f"layout_class: {result.get('layout_class', '')}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
