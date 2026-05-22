#!/usr/bin/env python3
"""Evaluate a WorkUnit against an explicit Eureka node policy.

The script is local-only and report-only. It reads committed or explicit JSON
inputs, prints a deterministic summary, and writes a report only when an output
path is provided.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_foundry import node_policy_evaluator


DEFAULT_CAPABILITY_MATRIX = REPO_ROOT / "control/inventory/nodes/node_capability_matrix.json"

EXAMPLE_INPUTS = {
    "local_private_allowed": {
        "node_manifest": "examples/nodes/local_private_node_v0/eureka_node_manifest.json",
        "node_policy": "examples/nodes/policies/local_private_node_policy_v0.json",
        "workunit": "examples/work_units/search_need_review_v0/work_unit.json",
    },
    "source_lead_allowed": {
        "node_manifest": "examples/nodes/local_autonomous_dry_run_node_v0/eureka_node_manifest.json",
        "node_policy": "examples/nodes/policies/local_autonomous_dry_run_node_policy_v0.json",
        "workunit": "examples/work_units/source_lead_inspection_v0/work_unit.json",
    },
    "policy_blocked": {
        "node_manifest": "examples/nodes/local_autonomous_dry_run_node_v0/eureka_node_manifest.json",
        "node_policy": "examples/nodes/policies/local_autonomous_dry_run_node_policy_v0.json",
        "workunit": "examples/work_units/policy_blocked_work_unit_v0/work_unit.json",
    },
    "future_metadata_probe_gated": {
        "node_manifest": "examples/nodes/institution_node_future_v0/eureka_node_manifest.json",
        "node_policy": "examples/nodes/policies/institution_node_future_policy_v0.json",
        "workunit": "examples/work_units/approved_metadata_probe_future_v0/work_unit.json",
    },
}

FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "runtime",
    "contracts",
    "control/inventory/publication",
    "control/master_index",
    "master_index",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def output_path_allowed(path: Path) -> bool:
    """Return true when an explicit report output path is policy-compliant."""

    resolved = path.resolve()
    rel = _repo_relative(resolved)
    for forbidden in FORBIDDEN_OUTPUT_ROOTS:
        if rel == forbidden or rel.startswith(f"{forbidden}/"):
            return False
    if rel.startswith("control/audits/") and "/generated/" in f"/{rel}/":
        return True
    if rel.startswith("examples/node_policy_evaluations/") and rel.endswith("/evaluation_result.json"):
        return True
    temp_root = Path(tempfile.gettempdir()).resolve()
    try:
        resolved.relative_to(temp_root)
        return True
    except ValueError:
        return False


def build_result(args: argparse.Namespace) -> dict[str, Any]:
    node_manifest_path = Path(args.node_manifest)
    node_policy_path = Path(args.node_policy)
    workunit_path = Path(args.workunit)
    capability_matrix_path = Path(args.capability_matrix)
    node_manifest = node_policy_evaluator.load_node_manifest(node_manifest_path)
    node_policy = node_policy_evaluator.load_node_policy(node_policy_path)
    workunit = node_policy_evaluator.load_workunit(workunit_path)
    capability_matrix = node_policy_evaluator.load_capability_matrix(capability_matrix_path)
    return node_policy_evaluator.build_node_policy_evaluation_result(
        {
            "node_manifest": node_manifest,
            "node_policy": node_policy,
            "workunit": workunit,
            "capability_matrix": capability_matrix,
            "node_manifest_path": _repo_relative(node_manifest_path),
            "node_policy_path": _repo_relative(node_policy_path),
            "workunit_path": _repo_relative(workunit_path),
        }
    )


def write_output(path: Path, result: dict[str, Any], summary_path: Path | None = None) -> None:
    if not output_path_allowed(path):
        raise ValueError(f"output path is forbidden by policy: {_repo_relative(path)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if summary_path:
        if not output_path_allowed(summary_path):
            raise ValueError(f"summary output path is forbidden by policy: {_repo_relative(summary_path)}")
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            node_policy_evaluator.summarize_node_policy_evaluation(result),
            encoding="utf-8",
        )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node-manifest", help="Explicit node manifest JSON")
    parser.add_argument("--node-policy", help="Explicit node policy JSON")
    parser.add_argument("--workunit", help="Explicit WorkUnit JSON")
    parser.add_argument("--capability-matrix", default=str(DEFAULT_CAPABILITY_MATRIX))
    parser.add_argument("--output", help="Optional explicit evaluation result path")
    parser.add_argument("--summary-output", help="Optional explicit summary path")
    parser.add_argument("--check", action="store_true", help="Validate inputs and report without requiring a write")
    parser.add_argument("--json", action="store_true", help="Print JSON result to stdout")
    parser.add_argument("--list-examples", action="store_true", help="List safe committed example input triples")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None, stdout: Any | None = None, stderr: Any | None = None) -> int:
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    args = parse_args(argv or sys.argv[1:])
    if args.list_examples:
        for name in sorted(EXAMPLE_INPUTS):
            item = EXAMPLE_INPUTS[name]
            print(f"{name}: {item['node_manifest']} | {item['node_policy']} | {item['workunit']}", file=stdout)
        return 0

    missing = [flag for flag, value in (
        ("--node-manifest", args.node_manifest),
        ("--node-policy", args.node_policy),
        ("--workunit", args.workunit),
    ) if not value]
    if missing:
        print(f"missing required arguments: {', '.join(missing)}", file=stderr)
        return 2

    try:
        result = build_result(args)
        errors = node_policy_evaluator.validate_node_policy_evaluation_result(result)
        if errors:
            print("node policy evaluation validation failed:", file=stderr)
            for error in errors:
                print(f"- {error}", file=stderr)
            return 1
        if args.output:
            write_output(Path(args.output), result, Path(args.summary_output) if args.summary_output else None)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        else:
            print(node_policy_evaluator.summarize_node_policy_evaluation(result), end="", file=stdout)
        return 0
    except Exception as exc:  # deterministic CLI boundary
        print(f"node policy evaluation failed: {exc}", file=stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
