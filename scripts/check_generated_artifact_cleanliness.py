#!/usr/bin/env python3
"""Check that generated artifact roots have no uncommitted drift."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = Path("control/policies/generated_artifact_policy.json")
TASK_ID = "R0-REMEDIATION-GENERATED-ARTIFACT-DRIFT-01"


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    policy = load_policy(root / args.policy)
    result = check_cleanliness(root, policy)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("Generated artifact cleanliness", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"generated_drift_count: {len(result['generated_drift_paths'])}", file=stdout)
    return 1 if args.check and result["status"] != "pass" else 0


def check_cleanliness(root: Path, policy: Mapping[str, Any]) -> dict[str, Any]:
    status_paths = git_status(root)
    generated_drift: list[dict[str, str]] = []
    forbidden_untracked: list[str] = []
    for item in status_paths:
        artifact_class = classify_path(item["path"], policy)
        if artifact_class == "source_input":
            continue
        drift = dict(item)
        drift["artifact_class"] = artifact_class
        generated_drift.append(drift)
        if item["change_kind"] == "added" and artifact_class in {"deployment_generated", "canonical_generated"}:
            forbidden_untracked.append(item["path"])
    return {
        "schema_version": "generated_artifact_cleanliness.v0",
        "task": TASK_ID,
        "status": "pass" if not generated_drift and not forbidden_untracked else "fail",
        "generated_drift_paths": generated_drift,
        "forbidden_untracked_generated_outputs": forbidden_untracked,
        "site_dist_mutated": any(item["path"].startswith("site/dist/") or item["path"] == "site/dist" for item in generated_drift),
        "public_search_index_drift": any(item["path"].startswith("data/public_index/") for item in generated_drift),
        "dashboard_snapshot_drift": any(item["path"].startswith("examples/demand_dashboard/") for item in generated_drift),
        "public_alpha_evidence_drift": any(item["path"].startswith("docs/operations/public_alpha_rehearsal_evidence_v0/") for item in generated_drift),
        "network_used": False,
        "model_provider_used": False,
    }


def git_status(root: Path) -> list[dict[str, str]]:
    completed = subprocess.run(["git", "status", "--porcelain=v1"], cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return []
    paths: list[dict[str, str]] = []
    for line in completed.stdout.splitlines():
        if len(line) < 4:
            continue
        code = line[:2]
        raw = line[3:].strip().strip('"').replace("\\", "/")
        change_kind = "added" if "?" in code or "A" in code else ("deleted" if "D" in code else "modified")
        for path in raw.split(" -> "):
            paths.append({"path": path, "change_kind": change_kind})
    return paths


def load_policy(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"classifiers": []}
    return payload if isinstance(payload, dict) else {"classifiers": []}


def classify_path(path: str, policy: Mapping[str, Any]) -> str:
    normalized = path.replace("\\", "/").strip("/")
    for item in policy.get("classifiers", []):
        if not isinstance(item, dict):
            continue
        prefix = str(item.get("path", "")).strip("/")
        if normalized == prefix or normalized.startswith(prefix + "/"):
            return str(item.get("artifact_class", "unknown"))
    return "source_input"


if __name__ == "__main__":
    raise SystemExit(main())
