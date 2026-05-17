#!/usr/bin/env python3
"""Plan or explicitly copy a legacy local instance into the sibling layout."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance.errors import LocalInstancePathError
from runtime.local_appliance.paths import describe_instance_layout, resolve_instance_root, resolve_repo_root


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="from_path", required=True, help="Existing explicit instance path.")
    parser.add_argument("--to", dest="to_path", required=True, help="Target explicit instance path.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Plan only; this is the default.")
    parser.add_argument("--apply", action="store_true", help="Copy files to the target. The source is never deleted.")
    parser.add_argument("--allow-existing", action="store_true", help="Allow copying into an existing empty target directory.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else resolve_repo_root()
    try:
        source = resolve_instance_root(args.from_path, repo_root)
        target = resolve_instance_root(args.to_path, repo_root)
    except LocalInstancePathError as exc:
        result = fail_result(str(exc), args.from_path, args.to_path)
        emit(result, args.json, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2

    dry_run = not args.apply
    errors: list[str] = []
    warnings: list[str] = []
    if not source.exists():
        if args.apply:
            errors.append("source instance path does not exist")
        else:
            warnings.append("source instance path does not exist; dry-run still reports the manual migration plan")
    if target.exists() and any(target.iterdir()) and not args.allow_existing:
        message = "target exists and is not empty; use --allow-existing only after manual review"
        if dry_run:
            warnings.append(message)
        else:
            errors.append(message)
    manual_commands = [
        f"mkdir {str(target.parent)!r}",
        f"robocopy {str(source)!r} {str(target)!r} /E",
        "Validate with: python scripts/eureka_validate_instance.py --instance <target> --json",
        "After manual review, remove the old source yourself if desired; this helper never deletes it.",
    ]
    mutation_performed = False
    if not errors and args.apply:
        if target.exists() and any(target.iterdir()):
            # Existing non-empty targets require an operator-reviewed follow-up copy strategy.
            errors.append("copy into non-empty target is refused even with --allow-existing")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, target, dirs_exist_ok=args.allow_existing)
            mutation_performed = True

    result = {
        "schema_version": "eureka_instance_layout_migration_plan.v0",
        "status": "fail" if errors else "pass",
        "dry_run": dry_run,
        "apply_requested": bool(args.apply),
        "source": str(source),
        "target": str(target),
        "source_layout": describe_instance_layout(repo_root, source),
        "target_layout": describe_instance_layout(repo_root, target),
        "manual_commands": manual_commands,
        "source_deleted": False,
        "mutation_performed": mutation_performed,
        "errors": errors,
        "warnings": warnings if dry_run else warnings + ["explicit --apply was requested; source was not deleted"],
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    emit(result, args.json, stdout)
    return 0 if result["status"] == "pass" else 1


def fail_result(message: str, source: str, target: str) -> dict:
    return {
        "schema_version": "eureka_instance_layout_migration_plan.v0",
        "status": "fail",
        "dry_run": True,
        "apply_requested": False,
        "source": source,
        "target": target,
        "source_deleted": False,
        "mutation_performed": False,
        "errors": [message],
        "warnings": [],
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def emit(result: dict, as_json: bool, stdout: TextIO) -> None:
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    for command in result.get("manual_commands", []):
        print(command, file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
