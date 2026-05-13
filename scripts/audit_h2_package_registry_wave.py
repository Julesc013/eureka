#!/usr/bin/env python3
"""Audit H2 package-registry wave integration artifacts offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control.prototypes.legacy_runtime.connectors.h2_package_registries.normalizer_common import H2_SOURCE_IDS  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h2_package_registries.quality_delta import build_h2_quality_delta, summarize_h2_quality_delta  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h2_package_registries.review_integration import summarize_h2_review_integration  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h2_package_registries.wave_postmortem import (  # noqa: E402
    apply_missing_source_gate,
    build_h2_connector_wave_postmortem,
    build_h2_integration_audit,
    build_h2_next_phase_recommendation,
)


AUDIT_DIR = Path("control/audits/h2-bundle-04-package-review-quality-audit-v0")
REVIEW_DIR = Path("examples/connectors/h2_package_registries/review_integration")
FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "data/public_index",
    "runtime",
    "contracts",
    "control/inventory/publication",
    "control/inventory/sources",
    "data/master_index",
    "master_index",
    "package_cache",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json-output", help="Optional audit JSON output path.")
    parser.add_argument("--summary-output", help="Optional markdown summary output path.")
    args = parser.parse_args(argv)
    try:
        artifacts = build_current_audit()
        if not args.check:
            if args.json_output:
                _write_json(args.json_output, artifacts["integration_audit"])
            if args.summary_output:
                _write_text(args.summary_output, render_summary_markdown(artifacts))
        print("H2 package registry wave audit", file=stdout)
        print(f"status: {artifacts['integration_audit']['h2_exit_gate']}", file=stdout)
        print(f"next_phase_recommendation: {artifacts['integration_audit']['next_phase_recommendation']}", file=stdout)
        print(f"audited_source_count: {len(artifacts['integration_audit']['audited_sources'])}", file=stdout)
        print(f"wrote_files: {str(bool(not args.check and (args.json_output or args.summary_output))).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001 - deterministic CLI validation surface.
        print("H2 package registry wave audit", file=stdout)
        print("status: invalid", file=stdout)
        print(f"ERROR: {exc}", file=stdout)
        return 1


def build_current_audit() -> dict[str, Any]:
    review = _load_json(REPO_ROOT / REVIEW_DIR / "h2_review_integration_result_v0.json")
    delta_path = REPO_ROOT / REVIEW_DIR / "h2_quality_delta_report_v0.json"
    delta = _load_json(delta_path) if delta_path.is_file() else build_h2_quality_delta({"review_integration_result": review})
    postmortem_path = REPO_ROOT / REVIEW_DIR / "h2_connector_wave_postmortem_v0.json"
    postmortem = _load_json(postmortem_path) if postmortem_path.is_file() else build_h2_connector_wave_postmortem(review, delta)
    recommendation_path = REPO_ROOT / REVIEW_DIR / "h2_next_phase_recommendation_v0.json"
    recommendation = _load_json(recommendation_path) if recommendation_path.is_file() else build_h2_next_phase_recommendation(postmortem)
    integration_audit = build_h2_integration_audit(review, delta, postmortem, recommendation)
    apply_missing_source_gate(integration_audit)
    return {
        "review_integration_result": review,
        "quality_delta": delta,
        "postmortem": postmortem,
        "recommendation": recommendation,
        "integration_audit": integration_audit,
        "review_summary": summarize_h2_review_integration(review),
        "quality_summary": summarize_h2_quality_delta(delta),
    }


def render_summary_markdown(artifacts: Mapping[str, Any]) -> str:
    audit = artifacts["integration_audit"]
    return "\n".join(
        [
            "# H2 Integration Audit Summary",
            "",
            f"- h2_exit_gate: `{audit.get('h2_exit_gate')}`",
            f"- next_phase_recommendation: `{audit.get('next_phase_recommendation')}`",
            f"- audited_sources: `{len(audit.get('audited_sources', []))}`",
            "- package_identity_truth_accepted: `false`",
            "- dependency_correctness_accepted: `false`",
            "- package_downloads: `false`",
            "- package_manager_invocation: `false`",
            "- install_execute: `false`",
            "- public_index_mutated: `false`",
            "- master_index_mutated: `false`",
            "- recommended_next_task: `H3-BUNDLE-01 - OS package archive source-family policy packs`",
            "",
        ]
    )


def _load_json(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"{path} must contain a JSON object")
    return dict(payload)


def _write_json(path_text: str, payload: Mapping[str, Any]) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path_text: str, text: str) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _safe_output_path(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    repo_resolved = REPO_ROOT.resolve()
    try:
        rel_path = resolved.relative_to(repo_resolved).as_posix()
        rel_lower = rel_path.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        raise ValueError(f"refusing output outside approved H2 audit generated roots: {rel_path}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside repository approved roots or temp directory: {resolved}") from temp_exc


if __name__ == "__main__":
    raise SystemExit(main())
