#!/usr/bin/env python3
"""Validate IA-BUNDLE-00 readiness polish artifacts without external calls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = Path("control/audits/ia-bundle-00-readiness-polish-v0")
REPORT_REL = AUDIT_DIR / "ia_bundle_00_report.json"
TASK_PACKET_REL = Path(".aide/context/latest-task-packet.md")
EVIDENCE_INDEX_REL = Path("contracts/evidence/evidence_contract_index.v0.json")
REQUIRED_AUDIT_FILES = {
    "README.md",
    "ia_bundle_00_report.json",
    "track_b_warning_closure.md",
    "evidence_contract_location_decision.md",
    "ia_connector_readiness_checklist.md",
    "ia_bundle_sequence.md",
    "validation.md",
}
PRODUCT_BOUNDARY_KEYS = {
    "changed_product_behavior",
    "called_external_source",
    "enabled_live_probes",
    "enabled_source_sync",
    "enabled_source_connectors",
    "enabled_downloads",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "enabled_hosting",
    "enabled_pack_import",
    "enabled_hosted_review",
    "mutated_source_cache",
    "mutated_evidence_ledger",
    "mutated_candidate_index",
    "mutated_public_index",
    "mutated_master_index",
}
TRUTH_BOUNDARY_KEYS = {
    "accepted_evidence_truth",
    "accepted_candidate_truth",
    "accepted_public_truth",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_search",
    "claimed_production_readiness",
}
IA_GATE_FALSE_KEYS = {
    "source_policy_approved",
    "user_agent_contact_decided",
    "allowed_endpoints_decided",
    "forbidden_endpoints_decided",
    "rate_limit_decided",
    "timeout_retry_decided",
    "cache_ttl_decided",
    "kill_switch_decided",
    "fixture_normalizer_implemented",
    "metadata_only_live_probe_approved",
    "live_probe_enabled",
    "connector_runtime_enabled",
}
CHECKLIST_PHRASES = (
    "IA-BUNDLE-00 does not approve source access",
    "IA-BUNDLE-00 does not perform external calls",
    "IA-BUNDLE-00 does not enable a connector",
    "source policy approval required",
    "User-Agent/contact decision required",
    "metadata-only live probe pending",
    "reviewed-index dry-run pending",
)
SEQUENCE_PHRASES = (
    "IA-BUNDLE-01 - IA Metadata Connector Foundation",
    "IA-BUNDLE-02 - IA Bounded Metadata Live Probe",
    "IA-BUNDLE-03 - IA Reviewed-Index Dry-Run And Postmortem",
    "source family",
    "source capability ladder",
    "source policy gate",
    "fixture/replay harness",
    "live-probe envelope",
    "source cache",
    "evidence candidate bridge",
    "review queue",
    "coverage ledger future",
    "connector scorecard future",
)


def load_json(path: Path, errors: list[str]) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - deterministic validator output.
        errors.append(f"invalid JSON: {rel(path)}: {exc}")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"JSON must be an object: {rel(path)}")
        return {}
    return payload


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def require_file(root: Path, relative: Path, errors: list[str]) -> Path:
    path = root / relative
    if not path.is_file():
        errors.append(f"missing required file: {relative.as_posix()}")
    return path


def require_phrases(path: Path, phrases: Sequence[str], errors: list[str]) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            errors.append(f"{rel(path)} missing required phrase: {phrase}")


def require_mapping(payload: Mapping[str, Any], key: str, errors: list[str]) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        errors.append(f"report.{key} must be an object")
        return {}
    return value


def require_false_fields(section: Mapping[str, Any], keys: set[str], label: str, errors: list[str]) -> None:
    for key in sorted(keys):
        if section.get(key) is not False:
            errors.append(f"{label}.{key} must be false")


def validate_task_packet(root: Path, errors: list[str]) -> None:
    path = require_file(root, TASK_PACKET_REL, errors)
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    phase = section_body(text, "PHASE")
    goal = section_body(text, "GOAL")
    allowed_ia_progression_markers = {
        "IA-BUNDLE-01",
        "IA-BUNDLE-02",
        "IA-BUNDLE-03",
    }
    allowed_later_track_prefixes = (
        "H0-BUNDLE-",
        "H1-BUNDLE-",
        "H1-APPROVAL-",
        "F-BUNDLE-",
        "G-BUNDLE-",
        "I-BUNDLE-",
        "J0-BUNDLE-",
        "D-BUNDLE-",
        "C-BUNDLE-",
        "E-BUNDLE-",
        "MVP-ALPHA-",
        "PUBLIC-ALPHA-",
        "LOCAL-MVP-",
    )
    if not any(marker in text for marker in allowed_ia_progression_markers) and not any(
        marker in text for marker in allowed_later_track_prefixes
    ):
        errors.append("latest task packet must point the main development lane to IA-BUNDLE-01 or a later IA/H/F/G/I/J0/D/C/E/MVP task")
    if "HUMAN-OBS-REVIEW-01" not in text or "parallel side-lane" not in text:
        errors.append("latest task packet must preserve HUMAN-OBS-REVIEW-01 as a parallel side-lane")
    if "SYNC-BASELINE-01" in phase or "SYNC-BASELINE-01" in goal:
        errors.append("latest task packet must not present SYNC-BASELINE-01 as the active implementation task")
    if "IA-BUNDLE-00" in phase and "IA-BUNDLE-01" not in phase:
        errors.append("latest task packet phase must be refreshed beyond IA-BUNDLE-00")


def section_body(text: str, section: str) -> str:
    marker = f"## {section}"
    start = text.find(marker)
    if start < 0:
        return ""
    start = text.find("\n", start)
    if start < 0:
        return ""
    next_section = text.find("\n## ", start + 1)
    if next_section < 0:
        next_section = len(text)
    return text[start:next_section]


def validate_evidence_contract_location(root: Path, report: Mapping[str, Any], errors: list[str]) -> None:
    decision = require_mapping(report, "evidence_contract_location", errors)
    value = decision.get("decision")
    if value not in {"created_contracts_evidence", "classified_existing_location", "deferred_to_h0"}:
        errors.append("report.evidence_contract_location.decision is invalid")
        return
    if value == "created_contracts_evidence":
        require_file(root, Path("contracts/evidence/README.md"), errors)
        index_path = require_file(root, EVIDENCE_INDEX_REL, errors)
        if index_path.is_file():
            index = load_json(index_path, errors)
            boundary = require_mapping(index, "boundary", errors)
            require_false_fields(
                boundary,
                {
                    "evidence_runtime_implemented",
                    "source_cache_write_enabled",
                    "evidence_ledger_write_enabled",
                    "candidate_acceptance_enabled",
                    "evidence_truth_acceptance_enabled",
                    "public_truth_acceptance_enabled",
                    "public_index_mutation_allowed",
                    "master_index_mutation_allowed",
                    "live_source_access_allowed",
                    "telemetry_enabled",
                    "credentials_configured",
                },
                "contracts/evidence boundary",
                errors,
            )


def validate_report(root: Path, errors: list[str]) -> Mapping[str, Any]:
    report_path = require_file(root, REPORT_REL, errors)
    if not report_path.is_file():
        return {}
    report = load_json(report_path, errors)
    if report.get("schema_version") != "ia_bundle_00_report.v0":
        errors.append("report.schema_version must be ia_bundle_00_report.v0")
    if report.get("task") != "IA-BUNDLE-00":
        errors.append("report.task must be IA-BUNDLE-00")
    if report.get("track") != "IA":
        errors.append("report.track must be IA")
    if report.get("first_connector_readiness_after") not in {
        "READY_FOR_IA_BUNDLE_01",
        "READY_WITH_WARNINGS",
        "NEEDS_REMEDIATION",
    }:
        errors.append("report.first_connector_readiness_after is invalid")
    side_lanes = require_mapping(report, "side_lanes", errors)
    if side_lanes.get("human_obs_review") != "parallel_side_lane":
        errors.append("report.side_lanes.human_obs_review must be parallel_side_lane")
    gates = require_mapping(report, "ia_gates", errors)
    require_false_fields(gates, IA_GATE_FALSE_KEYS, "report.ia_gates", errors)
    product = require_mapping(report, "product_boundary", errors)
    require_false_fields(product, PRODUCT_BOUNDARY_KEYS, "report.product_boundary", errors)
    truth = require_mapping(report, "truth_boundary", errors)
    require_false_fields(truth, TRUTH_BOUNDARY_KEYS, "report.truth_boundary", errors)
    if report.get("next_task") != "IA-BUNDLE-01 - IA metadata connector foundation":
        errors.append("report.next_task must be IA-BUNDLE-01 - IA metadata connector foundation")
    validate_evidence_contract_location(root, report, errors)
    return report


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    audit_dir = root / AUDIT_DIR
    if not audit_dir.is_dir():
        errors.append(f"missing audit directory: {AUDIT_DIR.as_posix()}")
    else:
        present = {path.name for path in audit_dir.iterdir() if path.is_file()}
        missing = sorted(REQUIRED_AUDIT_FILES - present)
        if missing:
            errors.append(f"audit pack missing files: {', '.join(missing)}")
    checklist = require_file(root, AUDIT_DIR / "ia_connector_readiness_checklist.md", errors)
    sequence = require_file(root, AUDIT_DIR / "ia_bundle_sequence.md", errors)
    require_file(root, AUDIT_DIR / "track_b_warning_closure.md", errors)
    require_file(root, AUDIT_DIR / "evidence_contract_location_decision.md", errors)
    require_phrases(checklist, CHECKLIST_PHRASES, errors)
    require_phrases(sequence, SEQUENCE_PHRASES, errors)
    validate_task_packet(root, errors)
    validate_report(root, errors)
    return {
        "status": "valid" if not errors else "invalid",
        "task": "IA-BUNDLE-00",
        "audit_dir": AUDIT_DIR.as_posix(),
        "errors": errors,
    }


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    report = validate_repo(Path(args.repo_root))
    if args.json:
        print(json.dumps(report, indent=2), file=stdout)
    else:
        print(f"status: {report['status']}", file=stdout)
        for error in report["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
