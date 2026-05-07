from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.generate_static_searchpage_projection import DEFAULT_OUTPUT_ROOT, PROJECTION_TARGETS, validate_output_root


SCHEMA_VERSION = "0.1.0"
REPORT_SCHEMA_VERSION = "track_a_13_projection_dry_run.v0"
HANDOFF_SCHEMA_VERSION = "track_a_13_search_handoff_preview.v0"
REQUIRED_HANDOFF_FIELDS = {
    "schema_version",
    "source_view_model",
    "route_family",
    "representation_profile",
    "search_mode",
    "public_runtime_posture",
    "query",
    "result_summary",
    "results",
    "limitations",
    "blocked_actions",
    "product_boundary",
    "generated_from",
    "notes",
}
REQUIRED_FALSE_HANDOFF_BOUNDARY = {
    "hosted_backend_claimed",
    "live_probes_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "accounts_enabled",
    "telemetry_enabled",
}
REQUIRED_REPORT_BOUNDARY_FALSE = {
    "changed_product_behavior",
    "changed_public_routes",
    "changed_generated_site_artifacts",
    "regenerated_site_dist",
    "enabled_hosting",
    "enabled_live_probes",
    "enabled_source_sync",
    "enabled_source_connectors",
    "enabled_downloads",
    "enabled_installers",
    "enabled_execution",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "created_native_projects",
    "mutated_master_index",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_automatic_merge_or_promotion",
}
REQUIRED_LABELS = (
    "Search",
    "Query",
    "Mode/Posture",
    "Result Summary",
    "Results",
    "Source/Evidence",
    "Risk/Rights",
    "Compatibility",
    "Limitations",
    "Blocked Actions",
    "Next Safe Actions",
)
BOUNDARY_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "enabled_hosting": (
        re.compile(r"\bhosted backend (?:is )?(?:active|live|enabled|configured|deployed)\b", re.IGNORECASE),
        re.compile(r"\bhosted public search (?:is )?(?:active|live|enabled|configured|deployed)\b", re.IGNORECASE),
    ),
    "enabled_live_probes": (re.compile(r"\blive probes? (?:are )?enabled\b", re.IGNORECASE),),
    "enabled_downloads": (re.compile(r"\b(?:direct )?downloads? (?:are )?enabled\b", re.IGNORECASE),),
    "enabled_installers": (re.compile(r"\binstallers? (?:are )?enabled\b", re.IGNORECASE),),
    "enabled_execution": (re.compile(r"\bexecution (?:is )?enabled\b", re.IGNORECASE),),
    "enabled_uploads": (re.compile(r"\buploads? (?:are )?enabled\b", re.IGNORECASE),),
    "enabled_accounts": (re.compile(r"\baccounts? (?:are )?enabled\b", re.IGNORECASE),),
    "enabled_telemetry": (re.compile(r"\btelemetry (?:is )?enabled\b", re.IGNORECASE),),
    "claimed_rights_clearance": (re.compile(r"\brights clearance (?:is )?(?:granted|verified|claimed)\b", re.IGNORECASE),),
    "claimed_malware_safety": (re.compile(r"\bmalware safety (?:is )?(?:verified|claimed)\b", re.IGNORECASE),),
    "claimed_verified_installability": (re.compile(r"\bverified installability\b", re.IGNORECASE),),
    "claimed_exhaustive_global_search": (re.compile(r"\bexhaustive global search\b", re.IGNORECASE),),
    "claimed_automatic_merge_or_promotion": (
        re.compile(r"\bautomatic (?:merge|dedup|promotion) (?:is )?(?:enabled|allowed)\b", re.IGNORECASE),
    ),
    "claimed_accepted_public_truth": (re.compile(r"\baccepted public truth\b", re.IGNORECASE),),
}
JSON_TRUE_BOUNDARY_FIELDS = {
    "accepted_public_status": "claimed_accepted_public_truth",
    "accounts_enabled": "enabled_accounts",
    "automatic_merge_enabled": "claimed_automatic_merge_or_promotion",
    "automatic_promotion_enabled": "claimed_automatic_merge_or_promotion",
    "direct_download_enabled": "enabled_downloads",
    "downloads_enabled": "enabled_downloads",
    "execution_enabled": "enabled_execution",
    "hosted_backend_claimed": "enabled_hosting",
    "live_probes_enabled": "enabled_live_probes",
    "malware_safety_claimed": "claimed_malware_safety",
    "rights_clearance_claimed": "claimed_rights_clearance",
    "telemetry_enabled": "enabled_telemetry",
    "uploads_enabled": "enabled_uploads",
    "verified_installability_claimed": "claimed_verified_installability",
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate TRACK-A-13 static SearchPage dry-run outputs.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT, help="Generated output root.")
    parser.add_argument("--report-path", help="Projection dry-run report path.")
    parser.add_argument("--parity-path", help="Semantic parity report path.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).resolve()
    output_root = _resolve_repo_path(Path(args.output_root), root)
    report_path = _resolve_repo_path(Path(args.report_path), root) if args.report_path else output_root.parent / "projection_dry_run_report.json"
    parity_path = _resolve_repo_path(Path(args.parity_path), root) if args.parity_path else output_root.parent / "semantic_parity_report.md"
    report = validate_static_searchpage_projection_dry_run(
        repo_root=root,
        output_root=output_root,
        report_path=report_path,
        parity_path=parity_path,
    )
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_static_searchpage_projection_dry_run(
    *,
    repo_root: Path = REPO_ROOT,
    output_root: Path | None = None,
    report_path: Path | None = None,
    parity_path: Path | None = None,
) -> dict[str, Any]:
    root = repo_root.resolve()
    generated_root = _resolve_repo_path(output_root or Path(DEFAULT_OUTPUT_ROOT), root)
    report_file = _resolve_repo_path(report_path or generated_root.parent / "projection_dry_run_report.json", root)
    parity_file = _resolve_repo_path(parity_path or generated_root.parent / "semantic_parity_report.md", root)
    errors: list[str] = []
    warnings: list[str] = []

    try:
        validate_output_root(generated_root, root)
    except ValueError as exc:
        errors.append(str(exc))

    generated_paths = [generated_root / target["filename"] for target in PROJECTION_TARGETS]
    for path in generated_paths:
        if not path.is_file():
            errors.append(f"{_rel(path, root)}: generated file missing")
        if _is_relative_to(path, root / "site" / "dist"):
            errors.append(f"{_rel(path, root)}: generated file is under site/dist")

    handoff_path = generated_root / "search_handoff.json"
    handoff = _load_json(handoff_path, errors, root)
    if isinstance(handoff, Mapping):
        _validate_handoff(handoff, errors)

    for target in ("search.standard.html", "search.lite.html", "search.txt"):
        path = generated_root / target
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for label in REQUIRED_LABELS:
                if label not in text:
                    errors.append(f"{_rel(path, root)}: missing semantic label {label!r}")

    for path in generated_paths:
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            errors.extend(detect_forbidden_claims(text, _rel(path, root)))
            if path.suffix == ".json":
                payload = _load_json(path, errors, root)
                if payload is not None:
                    errors.extend(_json_boundary_violations(payload, _rel(path, root)))

    report = _load_json(report_file, errors, root)
    if isinstance(report, Mapping):
        if report.get("schema_version") != REPORT_SCHEMA_VERSION:
            errors.append(f"{_rel(report_file, root)}: schema_version must be {REPORT_SCHEMA_VERSION}")
        if report.get("status") not in {"pass", "warn"}:
            errors.append(f"{_rel(report_file, root)}: status must be pass or warn")
        boundary = report.get("product_boundary")
        if not isinstance(boundary, Mapping):
            errors.append(f"{_rel(report_file, root)}: product_boundary must be an object")
        else:
            for key in sorted(REQUIRED_REPORT_BOUNDARY_FALSE):
                if boundary.get(key) is not False:
                    errors.append(f"{_rel(report_file, root)}: product_boundary.{key} must be false")

    if not parity_file.is_file():
        errors.append(f"{_rel(parity_file, root)}: semantic parity report missing")
    else:
        parity_text = parity_file.read_text(encoding="utf-8")
        for category in ("route_identity", "query_identity", "public_runtime_posture", "blocked_actions"):
            if category not in parity_text:
                errors.append(f"{_rel(parity_file, root)}: missing parity category {category}")

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "valid" if not errors else "invalid",
        "output_root": _rel(generated_root, root),
        "report_path": _rel(report_file, root),
        "parity_path": _rel(parity_file, root),
        "generated_files_checked": [_rel(path, root) for path in generated_paths],
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def detect_forbidden_claims(text: str, label: str) -> list[str]:
    violations: list[str] = []
    for boundary, patterns in BOUNDARY_PATTERNS.items():
        for pattern in patterns:
            if _has_unsafe_match(text, pattern):
                violations.append(f"{label}: {boundary} claim matched {pattern.pattern}")
                break
    return sorted(set(violations))


def _validate_handoff(handoff: Mapping[str, Any], errors: list[str]) -> None:
    missing = REQUIRED_HANDOFF_FIELDS - set(handoff)
    if missing:
        errors.append(f"search_handoff.json: missing fields {sorted(missing)}")
    if handoff.get("schema_version") != HANDOFF_SCHEMA_VERSION:
        errors.append(f"search_handoff.json: schema_version must be {HANDOFF_SCHEMA_VERSION}")
    boundary = handoff.get("product_boundary")
    if not isinstance(boundary, Mapping):
        errors.append("search_handoff.json: product_boundary must be an object")
    else:
        for key in sorted(REQUIRED_FALSE_HANDOFF_BOUNDARY):
            if boundary.get(key) is not False:
                errors.append(f"search_handoff.json: product_boundary.{key} must be false")
    runtime = handoff.get("public_runtime_posture")
    if not isinstance(runtime, Mapping):
        errors.append("search_handoff.json: public_runtime_posture must be an object")
    else:
        for key in sorted(REQUIRED_FALSE_HANDOFF_BOUNDARY):
            if runtime.get(key) is not False:
                errors.append(f"search_handoff.json: public_runtime_posture.{key} must be false")


def _json_boundary_violations(value: Any, label: str, path: str = "$") -> list[str]:
    violations: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            boundary = JSON_TRUE_BOUNDARY_FIELDS.get(str(key))
            if boundary and child is True:
                violations.append(f"{label}: {child_path} implies {boundary}")
            violations.extend(_json_boundary_violations(child, label, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            violations.extend(_json_boundary_violations(child, label, f"{path}[{index}]"))
    return violations


def _has_unsafe_match(text: str, pattern: re.Pattern[str]) -> bool:
    for match in pattern.finditer(text):
        if not _match_is_negated(text, match):
            return True
    return False


def _match_is_negated(text: str, match: re.Match[str]) -> bool:
    prefix = text[max(0, match.start() - 40):match.start()].lower()
    matched = text[match.start():match.end()].lower()
    return (
        " no " in f" {prefix}"
        or " not " in f" {prefix}"
        or "without " in prefix
        or "unavailable" in matched
        or "disabled" in matched
        or "not " in matched
    )


def _load_json(path: Path, errors: list[str], repo_root: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path, repo_root)}: JSON file missing")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path, repo_root)}: invalid JSON at line {exc.lineno}: {exc.msg}")
    return None


def _resolve_repo_path(path: Path, repo_root: Path) -> Path:
    return path.resolve() if path.is_absolute() else (repo_root / path).resolve()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"validate_static_searchpage_projection_dry_run: {report['status']}",
        f"schema_version: {report['schema_version']}",
        f"output_root: {report['output_root']}",
        f"files: {len(report['generated_files_checked'])}",
    ]
    errors = report.get("errors", [])
    if errors:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in errors)
    warnings = report.get("warnings", [])
    if warnings:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in warnings)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
