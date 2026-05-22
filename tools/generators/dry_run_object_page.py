#!/usr/bin/env python3
"""Emit a hypothetical Object Page v0 JSON payload to stdout only."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence, TextIO


ALLOWED_OBJECT_KINDS = {
    "software",
    "software_version",
    "driver",
    "manual_or_documentation",
    "source_code_release",
    "package_metadata",
    "web_capture",
    "article_or_scan_segment",
    "file_inside_container",
    "compatibility_evidence",
    "source_identity",
    "collection",
    "unknown",
}
HARD_FALSE_FIELDS = {
    "runtime_object_page_implemented": False,
    "persistent_object_page_store_implemented": False,
    "object_page_generated_from_live_source": False,
    "live_source_called": False,
    "external_calls_performed": False,
    "source_cache_mutated": False,
    "evidence_ledger_mutated": False,
    "candidate_index_mutated": False,
    "candidate_promotion_performed": False,
    "public_index_mutated": False,
    "local_index_mutated": False,
    "master_index_mutated": False,
    "downloads_enabled": False,
    "uploads_enabled": False,
    "installs_enabled": False,
    "execution_enabled": False,
    "arbitrary_url_fetch_enabled": False,
    "rights_clearance_claimed": False,
    "malware_safety_claimed": False,
    "telemetry_exported": False,
}


def build_page(label: str, object_kind: str) -> dict:
    object_id = "dry-run-object-page"
    source_id = "source-dry-run-object-page"
    evidence_ref = "evidence-dry-run-object-page"
    representation_ref = "representation-dry-run-object-page"
    return {
        "schema_version": "0.1.0",
        "object_page_id": "object_page_dry_run",
        "object_page_kind": "object_page",
        "status": "dry_run_validated",
        "created_by_tool": "dry_run_object_page_v0",
        "object_identity": {
            "object_id": object_id,
            "object_kind": object_kind,
            "canonical_label": label,
            "aliases": [],
            "product_name": label,
            "vendor": "Example Vendor",
            "version": "unknown",
            "platform": "unknown",
            "architecture": "unknown",
            "artifact_type": "metadata_record",
            "identifiers": [{"identifier_kind": "dry_run_public_ref", "identifier_value": object_id}],
            "parent_object_ref": None,
            "child_object_refs": [],
            "identity_confidence": "unknown",
            "identity_status": "candidate",
            "identity_not_truth": True,
            "limitations": ["Dry-run identity only; not authoritative truth."],
        },
        "object_status": {
            "page_lane": "demo",
            "verification_status": "synthetic_example",
            "public_visibility": "public_safe_example",
            "actionability_status": "inspect_only",
            "limitations": ["Dry-run stdout only; no file is written."],
        },
        "title": label,
        "summary": "Hypothetical object page payload emitted to stdout only.",
        "versions_states_releases": [
            {
                "state_ref": "state-dry-run-1",
                "label": "Dry-run state",
                "version": "unknown",
                "platform": "unknown",
                "architecture": "unknown",
                "lifecycle_status": "unknown",
                "source_refs": [source_id],
                "evidence_refs": [evidence_ref],
                "confidence": "unknown",
                "limitations": ["Dry-run state only."],
            }
        ],
        "representations": [
            {
                "representation_ref": representation_ref,
                "representation_kind": "metadata_record",
                "label": "Dry-run metadata record",
                "source_refs": [source_id],
                "evidence_refs": [evidence_ref],
                "checksum_refs": [],
                "size_summary": "not included",
                "access_status": "metadata_only",
                "payload_included": False,
                "downloads_enabled": False,
                "limitations": ["No payload is included."],
            }
        ],
        "members": [],
        "sources": [
            {
                "source_id": source_id,
                "source_family": "dry_run",
                "source_status": "placeholder",
                "source_role": "primary",
                "source_cache_ref": None,
                "limitations": ["No source was called."],
            }
        ],
        "evidence": [
            {
                "evidence_ref": evidence_ref,
                "evidence_kind": "dry_run_metadata_observation",
                "evidence_status": "insufficient",
                "claim_summary": "Dry-run evidence exists only to validate payload shape.",
                "provenance_refs": [source_id],
                "confidence": "unknown",
                "confidence_not_truth": True,
                "limitations": ["Not accepted truth."],
            }
        ],
        "compatibility": {
            "compatibility_status": "unknown",
            "platform_refs": [],
            "operating_systems": [],
            "architectures": [],
            "runtime_requirements": [],
            "source_refs": [source_id],
            "evidence_refs": [evidence_ref],
            "confidence": "unknown",
            "limitations": ["Compatibility was not evaluated."],
        },
        "rights_risk_action_posture": {
            "rights_classification": "public_metadata_only",
            "risk_classification": "metadata_only",
            "allowed_actions": ["inspect_metadata", "view_sources", "view_evidence", "compare", "cite"],
            "disabled_actions": ["download", "install", "execute", "upload", "mirror", "arbitrary_url_fetch"],
            "downloads_enabled": False,
            "installs_enabled": False,
            "execution_enabled": False,
            "uploads_enabled": False,
            "mirroring_enabled": False,
            "arbitrary_url_fetch_enabled": False,
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "limitations": ["No action enablement or safety claim."],
        },
        "conflicts": [],
        "absence_near_misses_gaps": {
            "absence_status": "unknown",
            "global_absence_claimed": False,
            "near_misses": [],
            "gaps": [
                {
                    "gap_type": "source_cache_missing",
                    "explanation": "Dry-run does not read a source cache.",
                    "future_next_step": "Use future approved runtime outputs only.",
                    "limitations": ["No mutation is performed."],
                }
            ],
            "known_absence_page_refs": [],
            "checked_scope": ["dry-run payload builder"],
            "not_checked_scope": ["live sources", "public index", "source cache", "evidence ledger"],
            "limitations": ["No global absence claim."],
        },
        "result_card_projection": {
            "result_card_contract_ref": "contracts/api/search_result_card.v0.json",
            "can_project_to_result_card": True,
            "result_title": label,
            "result_subtitle": object_kind,
            "result_lane": "demo",
            "source_summary": "Dry-run source placeholder.",
            "evidence_summary": "Dry-run evidence placeholder.",
            "compatibility_summary": "unknown",
            "action_summary": "Inspect, compare, cite only.",
            "warnings": ["No runtime page exists."],
            "limitations": ["Projection only; public search is not mutated."],
        },
        "api_projection": {
            "response_kind": "object_page_response",
            "route_future": ["/object/{object_id}", "/api/v1/object/{object_id}"],
            "implemented_now": False,
            "compatible_with_public_search_response": True,
            "included_sections": ["identity", "sources", "evidence", "compatibility", "representations", "gaps"],
            "limitations": ["Future route only."],
        },
        "static_projection": {
            "static_demo_available": False,
            "static_demo_path": None,
            "generated_static_artifact": False,
            "no_js_required": True,
            "base_path_safe": True,
            "old_client_safe": True,
            "limitations": ["No static file is written."],
        },
        "privacy": {
            "privacy_classification": "public_safe_example",
            "contains_private_path": False,
            "contains_secret": False,
            "contains_private_url": False,
            "contains_user_identifier": False,
            "contains_ip_address": False,
            "contains_raw_private_query": False,
            "publishable": True,
            "public_aggregate_allowed": True,
            "reasons": ["Caller-provided label only."],
        },
        "limitations": ["Dry-run only.", "No runtime, no mutation, no external call."],
        "no_runtime_guarantees": {
            "runtime_object_page_implemented": False,
            "persistent_object_page_store_implemented": False,
            "object_page_generated_from_live_source": False,
            "live_source_called": False,
            "external_calls_performed": False,
        },
        "no_mutation_guarantees": {
            "source_cache_mutated": False,
            "evidence_ledger_mutated": False,
            "candidate_index_mutated": False,
            "candidate_promotion_performed": False,
            "public_index_mutated": False,
            "local_index_mutated": False,
            "master_index_mutated": False,
        },
        "notes": ["Fast learning, slow truth."],
        **HARD_FALSE_FIELDS,
    }


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", default="Synthetic Object Page", help="Public-safe label to use.")
    parser.add_argument("--object-kind", default="unknown", help="Object kind enum value.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. Plain mode also emits JSON for copy/paste simplicity.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.object_kind not in ALLOWED_OBJECT_KINDS:
        parser.error(f"--object-kind must be one of {', '.join(sorted(ALLOWED_OBJECT_KINDS))}")
    output = stdout or sys.stdout
    output.write(json.dumps(build_page(args.label, args.object_kind), indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
