#!/usr/bin/env python3
"""Audit H4 code/source/release wave artifacts offline."""

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

from runtime.connectors.h4_code_source_release.normalizer_common import H4_SOURCE_IDS  # noqa: E402
from runtime.connectors.h4_code_source_release.quality_delta import build_h4_quality_delta  # noqa: E402
from runtime.connectors.h4_code_source_release.review_integration import (  # noqa: E402
    build_h4_review_integration_result,
    detect_h4_review_product_boundary_violations,
    detect_h4_review_truth_boundary_violations,
    load_h4_code_source_outputs,
)
from runtime.connectors.h4_code_source_release.wave_postmortem import (  # noqa: E402
    build_h4_connector_wave_postmortem,
    build_h4_integration_audit,
    build_h4_next_phase_recommendation,
)

AUDIT_DIR = Path("control/audits/h4-bundle-04-code-source-review-quality-audit-v0")
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
    "repository_clone",
    "repository_clones",
    "repository_mirror",
    "repository_mirrors",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json-output", help="Optional audit JSON output path.")
    parser.add_argument("--summary-output", help="Optional audit Markdown output path.")
    args = parser.parse_args(argv)
    try:
        audit = build_wave_audit(REPO_ROOT)
        if args.json_output and not args.check:
            write_json(args.json_output, audit)
        if args.summary_output and not args.check:
            write_text(args.summary_output, render_summary(audit))
        if audit["h4_exit_gate"] in {"FAIL", "PARTIAL", "BLOCKED"}:
            status = "partial" if audit["h4_exit_gate"] == "PARTIAL" else "blocked"
        else:
            status = "pass"
        print("H4 code/source/release wave audit", file=stdout)
        print(f"status: {status}", file=stdout)
        print(f"h4_exit_gate: {audit['h4_exit_gate']}", file=stdout)
        print(f"next_phase_recommendation: {audit['next_phase_recommendation']}", file=stdout)
        print(f"source_count: {len(audit['audited_sources'])}", file=stdout)
        print(f"wrote_files: {str(bool((args.json_output or args.summary_output) and not args.check)).lower()}", file=stdout)
        return 0 if status == "pass" else 1
    except Exception as exc:  # noqa: BLE001
        print("H4 code/source/release wave audit", file=stdout)
        print("status: invalid", file=stdout)
        print(f"ERROR: {exc}", file=stdout)
        return 1


def build_wave_audit(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    required_paths = [
        "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/h4_bundle_01_report.json",
        "control/audits/h4-bundle-02-code-source-fixture-runtime-v0/h4_bundle_02_report.json",
        "control/audits/h4-bundle-03-code-source-live-probes-v0/h4_bundle_03_report.json",
        "control/audits/h4-bundle-04-code-source-review-quality-audit-v0/h4_bundle_04_report.json",
        "examples/connectors/h4_code_source_release/replay_results",
        "examples/connectors/h4_code_source_release/live_probe_results",
    ]
    for rel in required_paths:
        if not (root / rel).exists():
            errors.append(f"missing artifact: {rel}")
    replay_paths = sorted((root / "examples/connectors/h4_code_source_release/replay_results").glob("*.json"))
    live_paths = sorted((root / "examples/connectors/h4_code_source_release/live_probe_results").glob("*.json"))
    outputs = load_h4_code_source_outputs([*replay_paths, *live_paths])
    review = build_h4_review_integration_result({"outputs": outputs, "input_refs": [rel_path(path) for path in [*replay_paths, *live_paths]]})
    delta = build_h4_quality_delta({"review_integration_result": review})
    postmortem = build_h4_connector_wave_postmortem(review, delta)
    recommendation = build_h4_next_phase_recommendation(postmortem)
    audit = build_h4_integration_audit(review, delta, postmortem, recommendation)
    if set(audit.get("audited_sources", [])) != set(H4_SOURCE_IDS):
        errors.append("audited sources must match all ten H4 source IDs")
    errors.extend(detect_h4_review_truth_boundary_violations(audit))
    errors.extend(detect_h4_review_product_boundary_violations(audit))
    if errors:
        audit["h4_exit_gate"] = "PARTIAL"
        audit["next_phase_recommendation"] = "NEEDS_REMEDIATION"
        audit["blockers"] = sorted(dict.fromkeys(audit.get("blockers", []) + errors))
    return audit


def render_summary(audit: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# H4 Integration Audit Summary",
            "",
            f"- h4_exit_gate: `{audit.get('h4_exit_gate')}`",
            f"- next_phase_recommendation: `{audit.get('next_phase_recommendation')}`",
            f"- audited_sources: `{len(audit.get('audited_sources', []))}`",
            "- repository_clone: `false`",
            "- source_archive_downloads: `false`",
            "- release_asset_downloads: `false`",
            "- git_commands: `false`",
            "- build_tools: `false`",
            "- install_execute: `false`",
            "",
        ]
    )


def write_json(path_text: str, payload: Mapping[str, Any]) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path_text: str, text: str) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _safe_output_path(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    repo_resolved = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo_resolved).as_posix()
        rel_lower = rel.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("control/audits/") and (rel_lower.endswith(".json") or rel_lower.endswith(".md")):
            return resolved
        raise ValueError(f"refusing output outside approved H4 audit roots: {rel}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside repository approved roots or temp directory: {resolved}") from temp_exc


def rel_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
