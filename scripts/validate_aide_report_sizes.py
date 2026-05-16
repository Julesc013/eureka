from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCAN_ROOTS = [
    ".aide/reports",
    ".aide/context",
    ".aide/evals/runs",
    ".aide/changelog",
    ".aide/quality",
    ".aide/repo",
]

RAW_FORBIDDEN_MARKERS = [
    "raw_prompt_body",
    "raw_response_body",
    "begin private key",
    "openai_api_key",
    "anthropic_api_key",
    "deepseek_api_key",
    "sk-ant",
]


def _read_policy_number(policy_text: str, key: str, default: float) -> float:
    for line in policy_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(f"{key}:"):
            value = stripped.split(":", 1)[1].strip()
            try:
                return float(value)
            except ValueError:
                return default
    return default


def load_thresholds(repo_root: Path) -> dict[str, float]:
    policy_path = repo_root / ".aide/policies/report-size.yaml"
    text = policy_path.read_text(encoding="utf-8") if policy_path.exists() else ""
    return {
        "warning_threshold_mb": _read_policy_number(text, "warning_threshold_mb", 25.0),
        "hard_threshold_mb": _read_policy_number(text, "hard_threshold_mb", 50.0),
        "preferred_max_report_mb": _read_policy_number(text, "preferred_max_report_mb", 10.0),
        "shard_hard_threshold_mb": _read_policy_number(text, "shard_hard_threshold_mb", 25.0),
    }


def rel_path(repo_root: Path, path: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def scan_files(repo_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for root in SCAN_ROOTS:
        base = repo_root / root
        if not base.exists():
            continue
        for path in sorted(item for item in base.rglob("*") if item.is_file()):
            size = path.stat().st_size
            rows.append(
                {
                    "path": rel_path(repo_root, path),
                    "size_bytes": size,
                    "size_mb": round(size / (1024 * 1024), 3),
                }
            )
    return rows


def text_contains_forbidden_markers(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return []
    return [marker for marker in RAW_FORBIDDEN_MARKERS if marker in text]


def validate_ledger_shards(repo_root: Path, thresholds: dict[str, float]) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    ledger_path = repo_root / ".aide/reports/file-quality-ledger.json"
    if not ledger_path.exists():
        errors.append("file-quality ledger is missing without replacement")
        return errors, warnings, {"ledger_present": False}
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"file-quality ledger JSON is invalid: {exc}")
        return errors, warnings, {"ledger_present": True}
    summary = {
        "ledger_present": True,
        "record_storage": ledger.get("record_storage", "inline"),
        "record_count": ledger.get("record_count", len(ledger.get("records", [])) if isinstance(ledger.get("records"), list) else 0),
        "shard_count": 0,
        "ledger_size_bytes": ledger_path.stat().st_size,
    }
    if ledger_path.stat().st_size > int(thresholds["preferred_max_report_mb"] * 1024 * 1024):
        errors.append("file-quality-ledger.json is not compact")
    if ledger.get("record_storage") != "sharded":
        errors.append("file-quality ledger is not using sharded record storage")
        return errors, warnings, summary
    shards = ledger.get("record_shards", [])
    if not isinstance(shards, list) or not shards:
        errors.append("file-quality ledger shard index is empty")
        return errors, warnings, summary
    expected_names = [f"file-quality-ledger-{index:04d}.json" for index in range(1, len(shards) + 1)]
    total_records = 0
    shard_hard_bytes = int(thresholds["shard_hard_threshold_mb"] * 1024 * 1024)
    for index, entry in enumerate(shards):
        if not isinstance(entry, dict):
            errors.append(f"ledger shard entry {index} is not an object")
            continue
        path_value = entry.get("path")
        if not isinstance(path_value, str):
            errors.append(f"ledger shard entry {index} missing path")
            continue
        if Path(path_value).name != expected_names[index]:
            errors.append(f"ledger shard entry {index} is not deterministically named")
        shard_path = repo_root / path_value
        if not shard_path.exists():
            errors.append(f"ledger shard missing: {path_value}")
            continue
        shard_size = shard_path.stat().st_size
        if shard_size > shard_hard_bytes:
            errors.append(f"ledger shard above hard threshold: {path_value}")
        try:
            shard = json.loads(shard_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"ledger shard invalid JSON {path_value}: {exc}")
            continue
        records = shard.get("records", [])
        if not isinstance(records, list):
            errors.append(f"ledger shard records not list: {path_value}")
            continue
        total_records += len(records)
    summary["shard_count"] = len(shards)
    summary["records_in_shards"] = total_records
    if total_records != summary["record_count"]:
        errors.append("ledger shard record total does not match index record_count")
    return errors, warnings, summary


def validate(repo_root: Path) -> dict[str, Any]:
    thresholds = load_thresholds(repo_root)
    files = scan_files(repo_root)
    hard_bytes = int(thresholds["hard_threshold_mb"] * 1024 * 1024)
    warning_bytes = int(thresholds["warning_threshold_mb"] * 1024 * 1024)
    errors: list[str] = []
    warnings: list[str] = []
    oversized = [row for row in files if row["size_bytes"] > hard_bytes]
    warning_files = [row for row in files if warning_bytes < row["size_bytes"] <= hard_bytes]
    for row in oversized:
        errors.append(f"file above hard threshold: {row['path']}")
    for row in warning_files:
        warnings.append(f"file above warning threshold: {row['path']}")
    for row in files:
        suffix = Path(str(row["path"])).suffix.lower()
        if suffix in {".zip", ".gz", ".7z", ".rar"}:
            errors.append(f"opaque compressed report is forbidden: {row['path']}")
        markers = text_contains_forbidden_markers(repo_root / str(row["path"]))
        if markers:
            errors.append(f"forbidden raw/secret marker in {row['path']}: {', '.join(markers)}")
    ledger_errors, ledger_warnings, ledger_summary = validate_ledger_shards(repo_root, thresholds)
    errors.extend(ledger_errors)
    warnings.extend(ledger_warnings)
    largest = max(files, key=lambda row: int(row["size_bytes"]), default={"path": "", "size_bytes": 0, "size_mb": 0.0})
    return {
        "schema_version": "aide_report_size_validation.v0",
        "status": "fail" if errors else "pass",
        "thresholds": thresholds,
        "file_count": len(files),
        "largest_file": largest,
        "hard_threshold_violations": oversized,
        "warning_threshold_files": warning_files,
        "ledger": ledger_summary,
        "warnings": warnings,
        "errors": errors,
        "product_behavior_changed": False,
        "provider_model_network_calls_used": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "deployment_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate bounded AIDE report artifact sizes.")
    parser.add_argument("--repo-root", default=".", help="Repository root to scan.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    result = validate(repo_root)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("AIDE report size validation")
        print(f"result: {result['status'].upper()}")
        print(f"largest_file: {result['largest_file'].get('path', '')}")
        print(f"errors: {len(result['errors'])}")
        print(f"warnings: {len(result['warnings'])}")
        for error in result["errors"]:
            print(f"- FAIL {error}")
        for warning in result["warnings"]:
            print(f"- WARN {warning}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
