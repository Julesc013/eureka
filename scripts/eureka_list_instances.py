#!/usr/bin/env python3
"""List local Eureka sibling instances without mutating them."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance.paths import (
    describe_instance_layout,
    resolve_instances_root,
    resolve_legacy_sibling_instance_root,
    resolve_repo_root,
    resolve_workspace_root,
)


KNOWN_ROLES = ("default", "smoke", "syn", "f0", "lan")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else resolve_repo_root()
    workspace_root = resolve_workspace_root(repo_root)
    instances_root = resolve_instances_root(workspace_root)
    instances = []
    if instances_root.is_dir():
        for path in sorted(item for item in instances_root.iterdir() if item.is_dir()):
            layout = describe_instance_layout(repo_root, path)
            instances.append(
                {
                    "name": path.name,
                    "path": str(path.resolve()),
                    "role": path.name if path.name in KNOWN_ROLES else "custom",
                    "exists": True,
                    "layout_class": layout["layout_class"],
                }
            )
    legacy_root = resolve_legacy_sibling_instance_root(repo_root)
    legacy = {
        "name": legacy_root.name,
        "path": str(legacy_root),
        "exists": legacy_root.exists(),
        "layout_class": describe_instance_layout(repo_root, legacy_root)["layout_class"],
        "role": "legacy_sibling",
    }
    result = {
        "schema_version": "eureka_instance_list.v0",
        "status": "pass",
        "repo_root": str(repo_root),
        "workspace_root": str(workspace_root),
        "instances_root": str(instances_root),
        "instances_root_exists": instances_root.is_dir(),
        "instances": instances,
        "known_roles": list(KNOWN_ROLES),
        "legacy_sibling_instance": legacy,
        "mutation_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    emit(result, args.json, stdout)
    return 0


def emit(result: dict, as_json: bool, stdout: TextIO) -> None:
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    for item in result["instances"]:
        print(f"- {item['name']}: {item['path']}", file=stdout)
    if result["legacy_sibling_instance"]["exists"]:
        print(f"legacy: {result['legacy_sibling_instance']['path']}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
