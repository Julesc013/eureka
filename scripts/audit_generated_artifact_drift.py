#!/usr/bin/env python3
"""Audit generated artifact drift without network access."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "R0-REMEDIATION-GENERATED-ARTIFACT-DRIFT-01"
DEFAULT_POLICY = Path("control/policies/generated_artifact_policy.json")
FORBIDDEN_OUTPUT_ROOTS = {
    ".git",
    ".env",
    "runtime",
    "contracts",
    "surfaces",
    "native",
    "crates",
    "secrets",
    ".aide.local",
    ".local",
    ".cache",
}
DEFAULT_CLASSIFIERS = (
    ("site/dist", "deployment_generated"),
    ("data/public_index", "canonical_generated"),
    ("examples/demand_dashboard", "fixture_generated"),
    ("docs/operations/public_alpha_rehearsal_evidence_v0", "historical_evidence"),
    ("control/audits", "audit_generated"),
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    policy = load_policy(root / args.policy)
    baseline = snapshot_generated_paths(root, policy)
    command_result: dict[str, Any] | None = None
    if args.command:
        completed = subprocess.run(args.command, cwd=root, text=True, capture_output=True, check=False)
        command_result = {
            "command": " ".join(args.command),
            "returncode": completed.returncode,
            "stdout_tail": completed.stdout[-2000:],
            "stderr_tail": completed.stderr[-2000:],
        }
    report = build_report(root, policy, baseline=baseline, command_result=command_result)
    if args.output:
        write_json(root, Path(args.output), report)
    if args.summary_output:
        write_text(root, Path(args.summary_output), format_summary(report))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print(format_summary(report), file=stdout)
    return 1 if args.check and report["drift_detected"] else 0


def load_policy(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "schema_version": "generated_artifact_policy.v0",
            "classifiers": [
                {"path": prefix, "artifact_class": artifact_class}
                for prefix, artifact_class in DEFAULT_CLASSIFIERS
            ],
        }
    return payload if isinstance(payload, dict) else {}


def build_report(
    root: Path,
    policy: Mapping[str, Any],
    *,
    baseline: Mapping[str, str] | None = None,
    command_result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    status_paths = parse_git_status(root)
    hash_drift = compare_snapshot(root, policy, baseline or {})
    drift_paths: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for status in status_paths:
        path = status["path"]
        artifact_class = classify_path(path, policy)
        if artifact_class == "source_input":
            continue
        item = {
            "path": path,
            "artifact_class": artifact_class,
            "change_kind": status["change_kind"],
            "suspected_source": suspected_source(path),
            "recommended_fix": recommended_fix(artifact_class),
        }
        key = (item["path"], item["change_kind"])
        if key not in seen:
            seen.add(key)
            drift_paths.append(item)
    for path, change_kind in hash_drift:
        artifact_class = classify_path(path, policy)
        item = {
            "path": path,
            "artifact_class": artifact_class,
            "change_kind": change_kind,
            "suspected_source": suspected_source(path),
            "recommended_fix": recommended_fix(artifact_class),
        }
        key = (item["path"], item["change_kind"])
        if key not in seen:
            seen.add(key)
            drift_paths.append(item)
    return {
        "schema_version": "generated_artifact_drift_report.v0",
        "task": TASK_ID,
        "status": "partial" if drift_paths else "pass",
        "drift_detected": bool(drift_paths),
        "drift_paths": drift_paths,
        "test_order_sensitive": any(item["artifact_class"] == "deployment_generated" for item in drift_paths),
        "site_dist_mutated": any(item["path"].startswith("site/dist/") or item["path"] == "site/dist" for item in drift_paths),
        "public_search_index_drift": any(item["path"].startswith("data/public_index/") for item in drift_paths),
        "dashboard_snapshot_drift": any(item["path"].startswith("examples/demand_dashboard/") for item in drift_paths),
        "public_alpha_evidence_drift": any(item["path"].startswith("docs/operations/public_alpha_rehearsal_evidence_v0/") for item in drift_paths),
        "command_result": command_result,
        "network_used": False,
        "model_provider_used": False,
    }


def parse_git_status(root: Path) -> list[dict[str, str]]:
    completed = subprocess.run(["git", "status", "--porcelain=v1"], cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return []
    paths: list[dict[str, str]] = []
    for line in completed.stdout.splitlines():
        if len(line) < 4:
            continue
        code = line[:2]
        raw = line[3:].strip().strip('"').replace("\\", "/")
        candidates = raw.split(" -> ")
        change_kind = "added" if "?" in code or "A" in code else ("deleted" if "D" in code else "modified")
        for path in candidates:
            paths.append({"path": path, "change_kind": change_kind})
    return paths


def classify_path(path: str, policy: Mapping[str, Any]) -> str:
    normalized = path.replace("\\", "/").strip("/")
    classifiers = policy.get("classifiers", [])
    if not isinstance(classifiers, list):
        classifiers = []
    for item in classifiers:
        if not isinstance(item, dict):
            continue
        prefix = str(item.get("path", "")).strip("/")
        if normalized == prefix or normalized.startswith(prefix + "/"):
            return str(item.get("artifact_class", "unknown"))
    return "source_input"


def suspected_source(path: str) -> str:
    if path.startswith("site/dist/"):
        return "static site generator or test using default deployment output"
    if path.startswith("data/public_index/"):
        return "public search index generator"
    if path.startswith("examples/demand_dashboard/"):
        return "demand dashboard snapshot checksum validation"
    if path.startswith("docs/operations/public_alpha_rehearsal_evidence_v0/"):
        return "public alpha rehearsal evidence generator"
    return "repo-local generated artifact check"


def recommended_fix(artifact_class: str) -> str:
    if artifact_class == "deployment_generated":
        return "isolate ordinary tests to temp output; regenerate canonical site/dist only through documented generator"
    if artifact_class == "canonical_generated":
        return "regenerate canonical artifact through owning repo generator and record validation"
    if artifact_class == "fixture_generated":
        return "refresh fixture checksums or move test output to tempdir"
    if artifact_class == "audit_generated":
        return "write only explicit audit generated output"
    return "classify artifact and create a bounded remediation task if unsafe"


def snapshot_generated_paths(root: Path, policy: Mapping[str, Any]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for prefix in generated_prefixes(policy):
        base = root / prefix
        if base.is_file():
            hashes[prefix] = sha256(base)
        elif base.is_dir():
            for path in base.rglob("*"):
                if path.is_file():
                    hashes[path.relative_to(root).as_posix()] = sha256(path)
    return hashes


def compare_snapshot(root: Path, policy: Mapping[str, Any], baseline: Mapping[str, str]) -> list[tuple[str, str]]:
    if not baseline:
        return []
    current = snapshot_generated_paths(root, policy)
    drift: list[tuple[str, str]] = []
    for path, before in baseline.items():
        after = current.get(path)
        if after is None:
            drift.append((path, "deleted"))
        elif after != before:
            drift.append((path, "checksum_changed"))
    for path in sorted(set(current) - set(baseline)):
        drift.append((path, "added"))
    return drift


def generated_prefixes(policy: Mapping[str, Any]) -> list[str]:
    prefixes: list[str] = []
    for item in policy.get("classifiers", []):
        if not isinstance(item, dict):
            continue
        artifact_class = item.get("artifact_class")
        if artifact_class in {"canonical_generated", "deployment_generated", "audit_generated", "fixture_generated", "temp_test_generated", "historical_evidence"}:
            prefixes.append(str(item.get("path", "")).strip("/"))
    return [prefix for prefix in prefixes if prefix]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def format_summary(report: Mapping[str, Any]) -> str:
    lines = [
        "Generated artifact drift audit",
        f"status: {report.get('status')}",
        f"drift_detected: {report.get('drift_detected')}",
        f"drift_paths: {len(report.get('drift_paths', []))}",
    ]
    for item in report.get("drift_paths", [])[:20]:
        lines.append(f"- {item.get('path')} [{item.get('artifact_class')}, {item.get('change_kind')}]")
    return "\n".join(lines)


def write_json(root: Path, target: Path, payload: Mapping[str, Any]) -> None:
    path = resolve_output(root, target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(root: Path, target: Path, text: str) -> None:
    path = resolve_output(root, target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def resolve_output(root: Path, target: Path) -> Path:
    path = target if target.is_absolute() else root / target
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return resolved
    first = relative.split("/", 1)[0]
    if first in FORBIDDEN_OUTPUT_ROOTS or relative == ".env":
        raise SystemExit(f"refusing forbidden output root: {relative}")
    return resolved


if __name__ == "__main__":
    raise SystemExit(main())
