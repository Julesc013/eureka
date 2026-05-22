from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Callable, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_design_tokens import validate_design_tokens
from scripts.validate_download_evidence_absence_compare_view_models import (
    validate_download_evidence_absence_compare_view_models,
)
from scripts.validate_need_candidate_page_view_models import validate_need_candidate_page_view_models
from scripts.validate_object_page_view_model import validate_object_page_view_model
from scripts.validate_pack_task_review_page_view_models import validate_pack_task_review_page_view_models
from scripts.validate_representation_contracts import validate_representation_contracts
from scripts.validate_renderer_parity_harness import validate_renderer_parity_harness
from scripts.validate_route_view_representation_matrix import validate_route_view_representation_matrix
from scripts.validate_search_page_view_model import validate_search_page_view_model
from scripts.validate_semantic_renderer_parity import validate_semantic_renderer_parity
from scripts.validate_source_page_view_model import validate_source_page_view_model
from scripts.validate_temporal_minimal_search import validate_temporal_minimal_search
from scripts.validate_view_model_policy_index import validate_view_model_policy_index


SCHEMA_VERSION = "0.1.0"
Validator = tuple[str, str, Callable[[Path], Mapping[str, Any]]]

VALIDATORS: tuple[Validator, ...] = (
    ("representation_contracts", "Representation contracts", validate_representation_contracts),
    ("semantic_renderer_parity", "Semantic renderer parity", validate_semantic_renderer_parity),
    ("route_view_matrix", "Route/view/representation matrix", validate_route_view_representation_matrix),
    ("search_page_view_model", "SearchPage view model", validate_search_page_view_model),
    ("object_page_view_model", "ObjectPage view model", validate_object_page_view_model),
    ("source_page_view_model", "SourcePage view model", validate_source_page_view_model),
    ("need_candidate_page_view_models", "Need and Candidate view models", validate_need_candidate_page_view_models),
    ("pack_task_review_page_view_models", "Pack, Task, and Review view models", validate_pack_task_review_page_view_models),
    (
        "download_evidence_absence_compare_view_models",
        "Download, Evidence, Absence, and Compare view models",
        validate_download_evidence_absence_compare_view_models,
    ),
    ("view_model_policy_index", "View model policy index", validate_view_model_policy_index),
    ("design_tokens", "Design tokens", validate_design_tokens),
    ("temporal_minimal_search", "Temporal Minimal Search", validate_temporal_minimal_search),
    ("renderer_parity_harness", "Renderer parity harness", validate_renderer_parity_harness),
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate all Eureka Track A contracts in deterministic order.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit compact deterministic JSON.")
    parser.add_argument("--quiet", action="store_true", help="Only print the final status in plain mode.")
    parser.add_argument("--list", action="store_true", help="List validator groups and exit.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    output = stdout or sys.stdout
    if args.list:
        for group_id, label, _function in VALIDATORS:
            output.write(f"{group_id}: {label}\n")
        return 0

    report = validate_track_a_contracts(Path(args.repo_root))
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report, quiet=args.quiet))
    return 0 if report["status"] == "valid" else 1


def validate_track_a_contracts(
    repo_root: Path = REPO_ROOT,
    *,
    validators: Sequence[Validator] = VALIDATORS,
) -> dict[str, Any]:
    root = repo_root.resolve()
    groups: list[dict[str, Any]] = []
    all_errors: list[str] = []
    all_warnings: list[str] = []

    for group_id, label, function in validators:
        try:
            report = dict(function(root))
        except Exception as exc:  # pragma: no cover - defensive path still returned deterministically.
            report = {
                "schema_version": SCHEMA_VERSION,
                "status": "invalid",
                "errors": [f"{type(exc).__name__}: {exc}"],
                "warnings": [],
            }
        status = str(report.get("status", "invalid"))
        errors = [str(error) for error in report.get("errors", [])]
        warnings = [str(warning) for warning in report.get("warnings", [])]
        groups.append(
            {
                "group_id": group_id,
                "label": label,
                "status": status,
                "error_count": len(errors),
                "warning_count": len(warnings),
                "errors": sorted(errors),
                "warnings": sorted(warnings),
            }
        )
        all_errors.extend(f"{group_id}: {error}" for error in errors)
        all_warnings.extend(f"{group_id}: {warning}" for warning in warnings)
        if status not in {"valid", "pass", "PASS"} and not errors:
            all_errors.append(f"{group_id}: status {status!r} is not valid")

    all_errors = sorted(set(all_errors))
    all_warnings = sorted(set(all_warnings))
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "valid" if not all_errors else "invalid",
        "validator_count": len(groups),
        "groups": groups,
        "errors": all_errors,
        "warnings": all_warnings,
    }


def _format_plain(report: Mapping[str, Any], *, quiet: bool) -> str:
    lines = [f"validate_track_a_contracts: {report['status']}"]
    if quiet:
        return "\n".join(lines) + "\n"
    lines.append(f"schema_version: {report['schema_version']}")
    lines.append(f"validators: {report['validator_count']}")
    for group in report.get("groups", []):
        if isinstance(group, Mapping):
            lines.append(f"- {group['group_id']}: {group['status']}")
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
