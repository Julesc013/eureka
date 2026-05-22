#!/usr/bin/env python3
"""Create a new explicit local Eureka instance when requested."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eureka_init_instance import emit_result, error_result, initialize_instance
from runtime.local_appliance.paths import resolve_instances_root, resolve_repo_root, resolve_workspace_root


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit instance root to create. Preferred default: ../instances/default.")
    parser.add_argument("--name", help="Instance name under --instances-root or ../instances.")
    parser.add_argument("--instances-root", help="Instances root used with --name. Preferred root: ../instances.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    parser.add_argument("--dry-run", action="store_true", help="Report planned creation without writing files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else resolve_repo_root()
    if args.instance:
        instance = Path(args.instance)
    elif args.name:
        root = Path(args.instances_root).expanduser().resolve() if args.instances_root else resolve_instances_root(resolve_workspace_root(repo_root))
        instance = root / args.name
    else:
        result = error_result("missing_instance", "--instance or --name is required")
        emit_result(result, args.json, None, stdout)
        print("ERROR: --instance or --name is required", file=stderr)
        return 2
    result = initialize_instance(instance, dry_run=args.dry_run)
    result["schema_version"] = "eureka_new_instance_result.v0"
    result["requested_name"] = args.name
    emit_result(result, args.json, None, stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
