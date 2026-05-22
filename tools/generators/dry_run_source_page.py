#!/usr/bin/env python3
"""Emit a hypothetical Source Page v0 JSON payload to stdout only."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Sequence, TextIO


ALLOWED_SOURCE_FAMILIES = {
    "internet_archive",
    "wayback_cdx_memento",
    "github_releases",
    "pypi",
    "npm",
    "software_heritage",
    "wikidata_open_library",
    "sourceforge",
    "local_fixture",
    "recorded_fixture",
    "manual_baseline",
    "source_pack",
    "evidence_pack",
    "local_private_future",
    "placeholder",
    "unknown",
}
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,96}$")
HARD_FALSE_FIELDS = {
    "runtime_source_page_implemented": False,
    "persistent_source_page_store_implemented": False,
    "source_page_generated_from_live_source": False,
    "connector_runtime_implemented": False,
    "connector_live_enabled": False,
    "live_source_called": False,
    "external_calls_performed": False,
    "source_sync_worker_executed": False,
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
    "source_trust_claimed": False,
    "telemetry_exported": False,
}


def build_page(source_id: str, source_family: str) -> dict:
    label = source_id.replace("-", " ").replace("_", " ").title()
    return {
        "schema_version": "0.1.0",
        "source_page_id": f"source_page_dry_run_{source_id}",
        "source_page_kind": "source_page",
        "status": "dry_run_validated",
        "created_by_tool": "dry_run_source_page_v0",
        "source_identity": {
            "source_id": source_id,
            "source_family": source_family,
            "canonical_label": label,
            "aliases": [],
            "source_homepage_ref": None,
            "source_inventory_ref": None,
            "connector_inventory_ref": None,
            "source_pack_refs": [],
            "evidence_pack_refs": [],
            "identity_status": "placeholder",
            "limitations": ["Dry-run source identity only; no source homepage was fetched."],
        },
        "source_status": {
            "status_class": "placeholder",
            "live_supported": False,
            "live_enabled": False,
            "connector_approved": False,
            "connector_runtime_implemented": False,
            "source_cache_runtime_implemented": False,
            "evidence_ledger_runtime_implemented": False,
            "public_search_live_fanout_allowed": False,
            "public_index_included": False,
            "limitations": ["Dry-run placeholder only."],
        },
        "title": label,
        "summary": "Hypothetical source page payload emitted to stdout only.",
        "coverage": {
            "coverage_depth": "placeholder",
            "covered_record_kinds": [],
            "covered_capabilities": ["inspect source metadata"],
            "uncovered_capabilities": ["live probe", "download", "mirror", "install", "execute", "upload", "arbitrary URL fetch"],
            "source_gap_types": ["source_coverage_gap"],
            "query_families_supported": [],
            "object_families_supported": [],
            "representation_families_supported": [],
            "member_access_supported": False,
            "compatibility_evidence_supported": False,
            "coverage_limitations": ["Dry-run coverage is not exhaustive."],
            "source_coverage_claim_not_exhaustive": True,
        },
        "connector_posture": {
            "connector_id": None,
            "connector_status": "no_connector",
            "connector_approval_refs": [],
            "allowed_capabilities": ["metadata posture description"],
            "forbidden_capabilities": ["live probe", "download", "mirror", "install", "execute", "upload", "arbitrary URL fetch"],
            "source_policy_review_required": True,
            "operator_approval_required": True,
            "human_approval_required": True,
            "user_agent_contact_required_future": True,
            "rate_limit_required_future": True,
            "timeout_required_future": True,
            "circuit_breaker_required_future": True,
            "limitations": ["No connector is implemented or enabled."],
        },
        "source_policy": {
            "source_policy_status": "not_reviewed",
            "source_terms_review_required": True,
            "automated_access_review_required": True,
            "rights_access_review_required": True,
            "privacy_review_required": True,
            "risk_review_required": True,
            "approval_checklist_refs": [],
            "operator_checklist_refs": [],
            "limitations": ["No policy documents were fetched."],
        },
        "source_cache_projection": {
            "source_cache_contract_ref": "contracts/source_cache/source_cache_record.v0.json",
            "source_cache_status": "contract_only",
            "source_cache_record_refs": [],
            "source_cache_record_count_policy": "none",
            "freshness_status": "not_applicable",
            "source_cache_mutation_allowed_now": False,
            "limitations": ["No source cache read or write."],
        },
        "evidence_ledger_projection": {
            "evidence_ledger_contract_ref": "contracts/evidence_ledger/evidence_ledger_record.v0.json",
            "evidence_ledger_status": "contract_only",
            "evidence_ledger_record_refs": [],
            "evidence_count_policy": "none",
            "evidence_review_status": "future",
            "evidence_ledger_mutation_allowed_now": False,
            "limitations": ["No evidence ledger read or write."],
        },
        "public_index_projection": {
            "included_in_public_index": False,
            "public_index_refs": [],
            "public_index_document_count_policy": "none",
            "indexed_fields_summary": [],
            "public_index_mutation_allowed_now": False,
            "limitations": ["Dry-run does not mutate public index."],
        },
        "public_search_projection": {
            "appears_in_public_search": False,
            "source_filter_supported_future": True,
            "result_card_source_badge_supported_future": True,
            "public_search_live_fanout_allowed": False,
            "public_search_reads_cache_future": True,
            "public_search_reads_live_connector_now": False,
            "limitations": ["Public search remains local_index_only."],
        },
        "query_intelligence_projection": {
            "search_need_refs": [],
            "probe_queue_refs": [],
            "demand_dashboard_refs": [],
            "known_absence_refs": [],
            "candidate_refs": [],
            "query_intelligence_status": "contract_only",
            "query_intelligence_mutation_allowed_now": False,
            "limitations": ["No query-intelligence mutation."],
        },
        "limitations_and_gaps": {
            "limitations": ["Dry-run only.", "No runtime route or persistence."],
            "gaps": [
                {
                    "gap_type": "source_coverage_gap",
                    "explanation": "Dry-run source has no checked coverage.",
                    "future_next_step": "Review source policy and add governed evidence before runtime planning.",
                    "limitations": ["No external call was performed."],
                }
            ],
            "source_gaps": ["source coverage unavailable"],
            "capability_gaps": ["source cache missing", "evidence ledger missing"],
            "approval_gaps": ["source policy review pending"],
            "operator_gaps": ["User-Agent/contact and rate limits pending"],
            "evidence_gaps": ["no evidence records"],
            "public_search_gaps": ["source page link future-only"],
        },
        "trust_and_provenance_caution": {
            "source_trust_claimed": False,
            "source_authority_status": "review_required",
            "provenance_summary": "Dry-run provenance is only the requested source id.",
            "provenance_refs": [],
            "source_disagreement_preserved": True,
            "limitations": ["No source trust claim."],
        },
        "rights_access_risk_posture": {
            "rights_classification": "review_required",
            "access_classification": "metadata_only",
            "risk_classification": "metadata_only",
            "allowed_actions": ["inspect_source_metadata", "view_source_limitations", "view_related_results", "view_evidence", "cite_source_page"],
            "disabled_actions": ["live_probe", "download", "mirror", "install", "execute", "upload", "arbitrary_url_fetch"],
            "downloads_enabled": False,
            "mirroring_enabled": False,
            "installs_enabled": False,
            "execution_enabled": False,
            "uploads_enabled": False,
            "arbitrary_url_fetch_enabled": False,
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "limitations": ["No action enablement."],
        },
        "result_card_source_badge_projection": {
            "source_badge_contract_ref": None,
            "can_project_to_source_badge": True,
            "badge_label": label,
            "badge_status": "placeholder",
            "badge_warnings": ["Dry-run only"],
            "badge_limitations": ["Projection only."],
            "result_card_contract_ref": "docs/reference/PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md",
            "limitations": ["No public search mutation."],
        },
        "api_projection": {
            "response_kind": "source_page_response",
            "route_future": ["/source/{source_id}", "/api/v1/source/{source_id}"],
            "implemented_now": False,
            "compatible_with_public_search_sources_response": True,
            "included_sections": ["identity", "status", "coverage", "connector_posture", "gaps"],
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
            "reasons": ["Source id is constrained to a public-safe token."],
        },
        "no_runtime_guarantees": {
            "runtime_source_page_implemented": False,
            "persistent_source_page_store_implemented": False,
            "source_page_generated_from_live_source": False,
            "connector_runtime_implemented": False,
            "connector_live_enabled": False,
            "live_source_called": False,
            "external_calls_performed": False,
            "source_sync_worker_executed": False,
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
    parser.add_argument("--source-id", default="placeholder-source", help="Public-safe source id token.")
    parser.add_argument("--source-family", default="placeholder", help="Source family enum value.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. Plain mode also emits JSON for copy/paste simplicity.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.source_family not in ALLOWED_SOURCE_FAMILIES:
        parser.error(f"--source-family must be one of {', '.join(sorted(ALLOWED_SOURCE_FAMILIES))}")
    if not SAFE_ID_RE.match(args.source_id):
        parser.error("--source-id must be a public-safe token using letters, numbers, dot, underscore, or hyphen.")
    output = stdout or sys.stdout
    output.write(json.dumps(build_page(args.source_id, args.source_family), indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
