"""Legacy-software seed batch.

This module builds deterministic fixture outputs for a legacy-software
discovery batch. It produces candidates, suppressions, trails, review packets,
needs, and handoffs, but never downloads, installs, executes, accepts truth, or
mutates reviewed/public indexes.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.candidate_store import normalize_candidate
from runtime.review.batch import (
    apply_batch_decision_preview,
    build_candidate_clusters,
    build_review_batch_packet,
    validate_batch_decision,
)
from runtime.scout import build_scout_run
from runtime.search.query_plan import archive_org_metadata_query, plan_query_to_source_actions


DEFAULT_TIMESTAMP = "2026-05-31T00:00:00Z"
BATCH_ID = "seed_batch_legacy_software_00"
DOMAIN_ID = "legacy_software"

SOURCE_FAMILIES = (
    "internet_archive_metadata",
    "github_releases_metadata",
    "package_registry_metadata",
    "software_heritage_metadata",
    "wayback_cdx_metadata",
    "manual_source_pack",
)

LEGACY_SOFTWARE_SUPPRESSIONS: tuple[dict[str, Any], ...] = (
    {
        "suppression_id": "generic_os_iso",
        "reason": "Suppress operating-system ISO results when the query asks for utilities or installers.",
        "applies_to_queries": ["legacy_software_q01"],
        "public_explanation": "OS image results are outside this software utility search.",
    },
    {
        "suppression_id": "operating_system_image",
        "reason": "Avoid treating OS install media as an app, driver, or utility candidate.",
        "applies_to_queries": ["legacy_software_q01", "legacy_software_q14"],
        "public_explanation": "Operating-system images are excluded from this seed batch.",
    },
    {
        "suppression_id": "crack",
        "reason": "Crack-related results are unsupported and unsafe for review promotion.",
        "applies_to_queries": ["*"],
        "public_explanation": "Crack-related results are blocked.",
    },
    {
        "suppression_id": "keygen",
        "reason": "Keygen-related results are unsupported and unsafe for review promotion.",
        "applies_to_queries": ["*"],
        "public_explanation": "Keygen-related results are blocked.",
    },
    {
        "suppression_id": "serial",
        "reason": "Serial-number-seeking results are unsupported and unsafe for review promotion.",
        "applies_to_queries": ["*"],
        "public_explanation": "Serial-number results are blocked.",
    },
    {
        "suppression_id": "warez",
        "reason": "Warez distribution results are unsupported.",
        "applies_to_queries": ["*"],
        "public_explanation": "Warez results are blocked.",
    },
    {
        "suppression_id": "torrent_only",
        "reason": "Torrent-only records are not useful controlled metadata leads in this batch.",
        "applies_to_queries": ["*"],
        "public_explanation": "Torrent-only leads are suppressed.",
    },
    {
        "suppression_id": "malware_suspicious",
        "reason": "Malware-looking or repackaged download metadata requires blocking or stronger review.",
        "applies_to_queries": ["*"],
        "public_explanation": "Suspicious software leads are suppressed.",
    },
    {
        "suppression_id": "fake_driver_updater",
        "reason": "Driver-updater SEO pages are not driver/support-media evidence.",
        "applies_to_queries": ["legacy_software_q03", "legacy_software_q05", "legacy_software_q12"],
        "public_explanation": "Generic driver-updater results are suppressed.",
    },
    {
        "suppression_id": "wrong_platform",
        "reason": "Wrong operating-system platform matches are not useful candidates.",
        "applies_to_queries": ["*"],
        "public_explanation": "Wrong-platform results are suppressed.",
    },
    {
        "suppression_id": "wrong_version",
        "reason": "Wrong major-version matches are not useful candidates.",
        "applies_to_queries": ["*"],
        "public_explanation": "Wrong-version results are suppressed.",
    },
    {
        "suppression_id": "web_installer_when_offline_requested",
        "reason": "Offline-installer queries should not be satisfied by web stubs.",
        "applies_to_queries": [
            "legacy_software_q02",
            "legacy_software_q06",
            "legacy_software_q08",
            "legacy_software_q11",
            "legacy_software_q12",
            "legacy_software_q16",
        ],
        "public_explanation": "Web-installer stubs are suppressed for offline-installer searches.",
    },
    {
        "suppression_id": "unrelated_modern_version",
        "reason": "Modern versions often do not support the target legacy platform.",
        "applies_to_queries": ["*"],
        "public_explanation": "Unrelated modern releases are suppressed.",
    },
    {
        "suppression_id": "source_only_mention",
        "reason": "A source-code-only mention is not an installer, driver, or support-media candidate by itself.",
        "applies_to_queries": ["*"],
        "public_explanation": "Source-only mentions need more evidence.",
    },
    {
        "suppression_id": "duplicate",
        "reason": "Duplicate metadata should collapse into review clusters.",
        "applies_to_queries": ["*"],
        "public_explanation": "Duplicate leads are clustered.",
    },
    {
        "suppression_id": "low_metadata_match",
        "reason": "Weak title-only matches need stronger metadata before promotion.",
        "applies_to_queries": ["*"],
        "public_explanation": "Low-confidence metadata matches need review.",
    },
    {
        "suppression_id": "unsafe_or_blocked",
        "reason": "Unsafe or blocked software-search results cannot be promoted.",
        "applies_to_queries": ["*"],
        "public_explanation": "Unsafe or blocked leads are not promoted.",
    },
)

LEGACY_SOFTWARE_QUERIES: tuple[dict[str, Any], ...] = (
    {
        "query_id": "legacy_software_q01",
        "raw_query": "Windows 7-compatible portable utilities, not Windows 7 ISO",
        "intent": "find_software",
        "domain_id": "legacy_software",
        "promoted_terms": ["Windows 7", "portable utilities", "compatibility", "not ISO"],
        "suppressions": ["generic_os_iso", "operating_system_image", "unrelated_modern_version"],
        "known_uncertainties": ["portable status", "compatibility evidence", "rights status"],
        "review_priority": 1,
        "fixture_source_family": "internet_archive_metadata",
    },
    {
        "query_id": "legacy_software_q02",
        "raw_query": "DirectX SDK June 2010 offline installer",
        "intent": "find_software",
        "domain_id": "legacy_software",
        "promoted_terms": ["DirectX SDK", "June 2010", "offline installer"],
        "suppressions": ["web_installer_when_offline_requested", "wrong_version"],
        "known_uncertainties": ["redistribution rights", "offline installer identity"],
        "review_priority": 1,
        "fixture_source_family": "internet_archive_metadata",
    },
    {
        "query_id": "legacy_software_q03",
        "raw_query": "StyleWriter 2500 Mac OS 8 driver",
        "intent": "find_driver_or_support_media",
        "domain_id": "driver_support_media",
        "promoted_terms": ["StyleWriter 2500", "Mac OS 8", "driver"],
        "suppressions": ["fake_driver_updater", "wrong_platform", "wrong_version"],
        "known_uncertainties": ["exact printer model", "support media provenance"],
        "review_priority": 1,
        "fixture_source_family": "manual_source_pack",
    },
    {
        "query_id": "legacy_software_q04",
        "raw_query": "Windows 98 registry repair utility",
        "intent": "find_software",
        "domain_id": "legacy_software",
        "promoted_terms": ["Windows 98", "registry repair", "utility"],
        "suppressions": ["malware_suspicious", "unrelated_modern_version"],
        "known_uncertainties": ["malware risk", "utility identity"],
        "review_priority": 3,
        "fixture_source_family": "manual_source_pack",
    },
    {
        "query_id": "legacy_software_q05",
        "raw_query": "Sound Blaster Live Windows 98 driver support CD",
        "intent": "find_driver_or_support_media",
        "domain_id": "driver_support_media",
        "promoted_terms": ["Sound Blaster Live", "Windows 98", "driver support CD"],
        "suppressions": ["fake_driver_updater", "wrong_platform", "wrong_version"],
        "known_uncertainties": ["hardware revision", "support CD identity"],
        "review_priority": 1,
        "fixture_source_family": "internet_archive_metadata",
    },
    {
        "query_id": "legacy_software_q06",
        "raw_query": "QuickTime 7 Windows XP offline installer",
        "intent": "find_software",
        "domain_id": "legacy_software",
        "promoted_terms": ["QuickTime 7", "Windows XP", "offline installer"],
        "suppressions": ["web_installer_when_offline_requested", "wrong_platform", "wrong_version"],
        "known_uncertainties": ["offline package identity", "license status"],
        "review_priority": 2,
        "fixture_source_family": "internet_archive_metadata",
    },
    {
        "query_id": "legacy_software_q07",
        "raw_query": "Winamp 5.666 full installer",
        "intent": "find_software",
        "domain_id": "legacy_software",
        "promoted_terms": ["Winamp", "5.666", "full installer"],
        "suppressions": ["wrong_version", "unrelated_modern_version"],
        "known_uncertainties": ["full installer vs stub", "mirror provenance"],
        "review_priority": 2,
        "fixture_source_family": "internet_archive_metadata",
    },
    {
        "query_id": "legacy_software_q08",
        "raw_query": "Visual C++ 2010 redistributable offline installer Windows 7",
        "intent": "find_software",
        "domain_id": "legacy_software",
        "promoted_terms": ["Visual C++ 2010", "redistributable", "offline installer", "Windows 7"],
        "suppressions": ["web_installer_when_offline_requested", "wrong_version"],
        "known_uncertainties": ["x86/x64 identity", "service pack identity"],
        "review_priority": 1,
        "fixture_source_family": "package_registry_metadata",
    },
    {
        "query_id": "legacy_software_q09",
        "raw_query": "old 7-Zip Windows 2000 compatible release",
        "intent": "find_source_release_or_package",
        "domain_id": "legacy_software",
        "promoted_terms": ["7-Zip", "Windows 2000", "compatible release"],
        "suppressions": ["wrong_platform", "unrelated_modern_version"],
        "known_uncertainties": ["last compatible version", "release provenance"],
        "review_priority": 2,
        "fixture_source_family": "github_releases_metadata",
    },
    {
        "query_id": "legacy_software_q10",
        "raw_query": "IrfanView old Windows XP compatible installer",
        "intent": "find_software",
        "domain_id": "legacy_software",
        "promoted_terms": ["IrfanView", "old", "Windows XP", "compatible installer"],
        "suppressions": ["wrong_platform", "unrelated_modern_version"],
        "known_uncertainties": ["installer provenance", "plugin bundle identity"],
        "review_priority": 2,
        "fixture_source_family": "internet_archive_metadata",
    },
    {
        "query_id": "legacy_software_q11",
        "raw_query": "Java 6 offline installer Windows XP",
        "intent": "find_software",
        "domain_id": "legacy_software",
        "promoted_terms": ["Java 6", "offline installer", "Windows XP"],
        "suppressions": ["web_installer_when_offline_requested", "wrong_version"],
        "known_uncertainties": ["update level", "offline package identity"],
        "review_priority": 2,
        "fixture_source_family": "internet_archive_metadata",
    },
    {
        "query_id": "legacy_software_q12",
        "raw_query": "Microsoft IntelliPoint Windows 7 driver offline installer",
        "intent": "find_driver_or_support_media",
        "domain_id": "driver_support_media",
        "promoted_terms": ["Microsoft IntelliPoint", "Windows 7", "driver", "offline installer"],
        "suppressions": ["fake_driver_updater", "web_installer_when_offline_requested", "wrong_platform"],
        "known_uncertainties": ["device family", "offline installer identity"],
        "review_priority": 2,
        "fixture_source_family": "wayback_cdx_metadata",
    },
    {
        "query_id": "legacy_software_q13",
        "raw_query": "PowerToys for Windows XP",
        "intent": "find_software",
        "domain_id": "legacy_software",
        "promoted_terms": ["PowerToys", "Windows XP"],
        "suppressions": ["wrong_platform", "unrelated_modern_version"],
        "known_uncertainties": ["specific toy package", "support page provenance"],
        "review_priority": 2,
        "fixture_source_family": "wayback_cdx_metadata",
    },
    {
        "query_id": "legacy_software_q14",
        "raw_query": "Windows 7 compatible file recovery utility portable",
        "intent": "find_software",
        "domain_id": "legacy_software",
        "promoted_terms": ["Windows 7", "file recovery", "portable utility"],
        "suppressions": ["operating_system_image", "malware_suspicious", "unrelated_modern_version"],
        "known_uncertainties": ["portable status", "safety review required"],
        "review_priority": 3,
        "fixture_source_family": "package_registry_metadata",
    },
    {
        "query_id": "legacy_software_q15",
        "raw_query": "legacy FTP client Windows 98 installer",
        "intent": "find_software",
        "domain_id": "legacy_software",
        "promoted_terms": ["legacy FTP client", "Windows 98", "installer"],
        "suppressions": ["wrong_platform", "malware_suspicious"],
        "known_uncertainties": ["client identity", "installer provenance"],
        "review_priority": 3,
        "fixture_source_family": "software_heritage_metadata",
    },
    {
        "query_id": "legacy_software_q16",
        "raw_query": "old PDF reader Windows 2000 compatible installer",
        "intent": "find_software",
        "domain_id": "legacy_software",
        "promoted_terms": ["old PDF reader", "Windows 2000", "compatible installer"],
        "suppressions": ["web_installer_when_offline_requested", "wrong_platform", "unrelated_modern_version"],
        "known_uncertainties": ["last compatible version", "security limitations"],
        "review_priority": 3,
        "fixture_source_family": "software_heritage_metadata",
    },
)

DEFAULT_POLICY: dict[str, Any] = {
    "seed_batch_outputs_are_not_truth": True,
    "candidates_require_review": True,
    "reviewed_index_mutation_enabled": False,
    "public_index_mutation_enabled": False,
    "master_index_mutation_enabled": False,
    "automatic_candidate_acceptance_enabled": False,
    "source_actions_bounded": True,
    "archive_org_metadata_candidates_allowed": True,
    "github_releases_metadata_fixture_allowed": True,
    "package_registry_metadata_fixture_allowed": True,
    "software_heritage_metadata_fixture_allowed": True,
    "live_metadata_optional_and_operator_gated": True,
    "raw_live_responses_committed": False,
    "downloads_enabled": False,
    "extraction_enabled": False,
    "install_execution_enabled": False,
    "model_provider_enabled": False,
    "deployment_enabled": False,
    "cracks_keygens_serials_supported": False,
    "malware_clean_claims_allowed": False,
}


def load_legacy_software_query_set(policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    queries: list[dict[str, Any]] = []
    for item in LEGACY_SOFTWARE_QUERIES:
        queries.append(
            {
                "schema_version": "seed_batch_query.v0",
                "batch_id": BATCH_ID,
                "query_id": item["query_id"],
                "raw_query": item["raw_query"],
                "intent": item["intent"],
                "domain_id": item["domain_id"],
                "expected_source_families": list(SOURCE_FAMILIES),
                "promoted_terms": list(item["promoted_terms"]),
                "suppressions": list(item["suppressions"]),
                "expected_candidate_kinds": [
                    "source_metadata_candidate",
                    "artifact_candidate",
                    "source_lead",
                    "review_seed",
                ],
                "known_uncertainties": list(item["known_uncertainties"]),
                "review_priority": int(item["review_priority"]),
                "review_required": True,
                "accepted_truth": False,
                "created_at": DEFAULT_TIMESTAMP,
            }
        )
    return queries


def build_legacy_software_query_plans(
    query_set: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    plans: list[dict[str, Any]] = []
    for query in query_set:
        raw_query = _text(query.get("raw_query"))
        planner_plan = plan_query_to_source_actions(raw_query)
        plan_id = _stable_id("legacy_seed_query_plan", query.get("query_id"), raw_query)
        archive_query = archive_org_metadata_query(planner_plan)
        if not archive_query or "crack" not in archive_query:
            archive_query = _legacy_archive_query(raw_query)
        plans.append(
            {
                "schema_version": "seed_batch_query_plan.v0",
                "batch_id": BATCH_ID,
                "query_id": _text(query.get("query_id")),
                "plan_id": plan_id,
                "raw_query": raw_query,
                "intent": _text(query.get("intent")),
                "domain_id": _text(query.get("domain_id")) or DOMAIN_ID,
                "planner_plan_id": planner_plan["plan_id"],
                "planner_intent": planner_plan["intent"],
                "planner_domain_pack": planner_plan["domain_pack"],
                "planner_plan": planner_plan,
                "source_query_rewrites": {
                    "internet_archive_metadata": archive_query,
                    "archive_org_metadata": archive_query,
                    "github_releases_metadata": raw_query,
                    "package_registry_metadata": raw_query,
                    "software_heritage_metadata": raw_query,
                    "wayback_cdx_metadata": raw_query,
                    "manual_source_pack": raw_query,
                },
                "candidate_suppressions": list(query.get("suppressions") or []),
                "review_required": True,
                "accepted_truth": False,
                "created_at": DEFAULT_TIMESTAMP,
                **_false_boundaries(),
            }
        )
    return plans


def build_legacy_software_source_plans(
    query_plans: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    family_modes = (
        ("internet_archive_metadata", "allowed", "fixture_metadata_candidates"),
        ("github_releases_metadata", "fixture", "fixture_release_descriptor"),
        ("package_registry_metadata", "fixture", "fixture_registry_descriptor"),
        ("software_heritage_metadata", "fixture", "fixture_archive_descriptor"),
        ("wayback_cdx_metadata", "planned", "capture_availability_descriptor"),
        ("manual_source_pack", "allowed", "fixture_source_pack_replay"),
    )
    source_plans: list[dict[str, Any]] = []
    for plan in query_plans:
        for family, status, execution_mode in family_modes:
            source_plans.append(
                {
                    "schema_version": "seed_batch_source_plan.v0",
                    "batch_id": BATCH_ID,
                    "source_plan_id": _stable_id("legacy_seed_source_plan", plan.get("plan_id"), family),
                    "query_id": _text(plan.get("query_id")),
                    "query_plan_ref": _text(plan.get("plan_id")),
                    "source_family": family,
                    "status": status,
                    "execution_mode": execution_mode,
                    "source_query": _text((plan.get("source_query_rewrites") or {}).get(family)),
                    "bounded": True,
                    "metadata_only": True,
                    "candidate_only": True,
                    "no_downloads": True,
                    "no_package_download": True,
                    "no_blob_fetch": True,
                    "install_execution_enabled": False,
                    "review_required": True,
                    "accepted_truth": False,
                    "created_at": DEFAULT_TIMESTAMP,
                    **_false_boundaries(),
                }
            )
    return source_plans


def run_legacy_software_fixture_candidates(
    query_plans: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    query_by_id = {item["query_id"]: item for item in LEGACY_SOFTWARE_QUERIES}
    candidates: list[dict[str, Any]] = []
    for index, plan in enumerate(query_plans, start=1):
        query_id = _text(plan.get("query_id"))
        query_def = query_by_id.get(query_id, {})
        source_family = _text(query_def.get("fixture_source_family")) or "internet_archive_metadata"
        slug = _slug(_text(plan.get("raw_query")))
        raw = {
            "schema_version": "legacy_software_metadata_candidate.v0",
            "candidate_id": f"seed_legacy_software_{query_id}_candidate",
            "candidate_status": "needs_review",
            "candidate_kind": "source_metadata_candidate",
            "candidate_title": f"{plan['raw_query']} fixture metadata lead",
            "candidate_summary": "Fixture-derived metadata candidate for legacy-software discovery.",
            "source_locator": _source_locator(source_family, index, slug),
            "source_family": source_family,
            "matched_query": plan["raw_query"],
            "query_plan_ref": plan["plan_id"],
            "source_action_ref": _stable_id("legacy_seed_source_action", plan["plan_id"], source_family),
            "source_observation_ref": _stable_id("legacy_seed_source_observation", BATCH_ID, query_id),
            "domain_id": _text(plan.get("domain_id")) or DOMAIN_ID,
            "confidence_label": "medium" if index <= 10 else "low",
            "match_reasons": [
                "fixture_legacy_software_seed",
                f"{source_family}_candidate",
                "requires_operator_review",
            ],
            "suppressions": list(plan.get("candidate_suppressions") or []),
            "limitations": [
                "fixture_derived",
                "candidate_not_reviewed_truth",
                "review_required_for_promotion",
                "no_download",
                "no_extraction",
                "no_install",
                "no_execute",
                "no_auto_promotion",
                "no_malware_clean_claim",
            ],
            "action_posture": {
                "allowed_actions": ["inspect", "view_source", "view_provenance", "read"],
                "blocked_actions": [
                    "download",
                    "install_handoff",
                    "execute",
                    "upload",
                    "extract",
                    "promote",
                    "package_download",
                ],
                "future_gated_actions": ["create_review_handoff", "update_candidate_state"],
                "public_mutation_enabled": False,
                "accepted_truth": False,
            },
            "accepted_truth": False,
            "review_required": True,
            "download_performed": False,
            "extraction_executed": False,
            "install_execution_enabled": False,
        }
        candidates.append(normalize_candidate(raw, _planner_compatible_plan(plan), merged_policy))
    return candidates


def run_legacy_software_archive_org_metadata_candidates(
    query_plans: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
    *,
    operator_approved_live_metadata: bool = False,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "seed_batch_archive_org_metadata_run.v0",
        "batch_id": BATCH_ID,
        "mode": "operator_approved_live_metadata" if operator_approved_live_metadata else "dry_run_planned",
        "query_count": len(query_plans),
        "operator_live_metadata_run_performed": False,
        "live_metadata_status": "not_run_operator_gate_required",
        "redacted_summary_only": True,
        "raw_live_response_committed": False,
        "candidate_records": [],
        "notes": [
            "Fixture mode is the default closeout lane.",
            "A future operator-approved live metadata pilot must remain metadata-only and must not commit raw responses.",
        ],
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def normalize_legacy_software_candidates(
    candidate_outputs: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    normalized = []
    for candidate in candidate_outputs:
        item = dict(candidate)
        item["accepted_truth"] = False
        item["reviewed_record_ref"] = None
        normalized.append(item)
    return normalized


def apply_legacy_software_suppressions(
    candidates: Sequence[Mapping[str, Any]],
    suppressions: Sequence[Mapping[str, Any]] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    suppression_records = list(suppressions or build_legacy_software_suppression_records())
    by_id = {item["suppression_id"]: item for item in suppression_records}
    applied: list[dict[str, Any]] = []
    for candidate in candidates:
        item = copy.deepcopy(dict(candidate))
        query_id = _candidate_query_id(item)
        suppression_ids = _text_list(item.get("suppressions"))
        suppression_ids.extend(
            suppression["suppression_id"]
            for suppression in suppression_records
            if _suppression_applies(suppression, query_id)
            and suppression["suppression_id"] in {"crack", "keygen", "serial", "warez", "torrent_only", "unsafe_or_blocked"}
        )
        unique_ids = sorted(set(suppression_ids))
        item["suppressions"] = unique_ids
        item["applied_suppressions"] = [
            {
                "suppression_id": suppression_id,
                "public_explanation": _text(by_id.get(suppression_id, {}).get("public_explanation")),
                "review_override_allowed": bool(by_id.get(suppression_id, {}).get("review_override_allowed", False)),
            }
            for suppression_id in unique_ids
        ]
        item["suppression_action_posture"] = {
            "blocked_actions": ["download", "install_handoff", "execute", "package_download", "promote"],
            "review_required": True,
            "accepted_truth": False,
        }
        item["accepted_truth"] = False
        item["reviewed_record_ref"] = None
        applied.append(item)
    return applied


def build_legacy_software_suppression_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for suppression in LEGACY_SOFTWARE_SUPPRESSIONS:
        records.append(
            {
                "schema_version": "legacy_software_suppression.v0",
                "suppression_id": suppression["suppression_id"],
                "reason": suppression["reason"],
                "applies_to_queries": list(suppression["applies_to_queries"]),
                "public_explanation": suppression["public_explanation"],
                "action_posture": {
                    "blocked_actions": ["download", "install_handoff", "execute", "package_download", "promote"],
                    "allowed_actions": ["inspect", "view_source", "view_provenance", "read"],
                },
                "review_override_allowed": False,
                "accepted_truth": False,
            }
        )
    return records


def build_legacy_software_candidate_index(
    candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    records = [copy.deepcopy(dict(candidate)) for candidate in candidates]
    return {
        "schema_version": "seed_batch_candidate_index.v0",
        "batch_id": BATCH_ID,
        "store_mode": "seed_batch_fixture",
        "candidate_count": len(records),
        "candidates": records,
        "candidate_refs": [_text(candidate.get("candidate_id")) for candidate in records],
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_legacy_software_scout_trails(
    candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_index = build_legacy_software_candidate_index(candidates, merged_policy)
    runs = [build_scout_run(candidate["candidate_id"], candidate_index) for candidate in candidates]
    return {
        "schema_version": "seed_batch_scout_trails.v0",
        "batch_id": BATCH_ID,
        "scout_runs": runs,
        "scout_refs": [run["scout_run_id"] for run in runs],
        "relation_count": sum(len(run.get("relations", [])) for run in runs),
        "related_path_count": sum(len(run.get("related_paths", [])) for run in runs),
        "workunit_seed_count": sum(len(run.get("workunit_seeds", [])) for run in runs),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_legacy_software_review_packets(
    candidates: Sequence[Mapping[str, Any]],
    scout_outputs: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    relations = [
        relation
        for run in scout_outputs.get("scout_runs", [])
        for relation in run.get("relations", [])
        if isinstance(relation, Mapping)
    ]
    clusters = build_candidate_clusters(candidates, relations)
    packet = build_review_batch_packet(clusters)
    decision = validate_batch_decision(
        packet,
        "accept_local_reviewed_preview",
        {"projection_profile": "operator_workbench", "dry_run": True},
    )
    preview = apply_batch_decision_preview(packet, decision)
    return {
        "schema_version": "seed_batch_review_packets.v0",
        "batch_id": BATCH_ID,
        "review_batch_packet": packet,
        "review_batch_refs": [packet["review_batch_id"]],
        "decision_preview": preview,
        "promotion_preview_refs": [item["preview_id"] for item in preview.get("promotion_previews", [])],
        "local_apply_handoff_refs": [preview["local_apply_handoff"]["handoff_id"]],
        "snapshot_refresh_handoff_refs": [preview["snapshot_refresh_handoff"]["handoff_id"]],
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_legacy_software_known_needs_and_absences(
    query_plans: Sequence[Mapping[str, Any]],
    candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_query_ids = {_candidate_query_id(candidate) for candidate in candidates}
    known_needs = []
    absences = []
    for plan in query_plans:
        query_id = _text(plan.get("query_id"))
        known_needs.append(
            {
                "schema_version": "seed_batch_known_need.v0",
                "need_id": _stable_id("legacy_seed_known_need", query_id, "software_safety_review"),
                "query_id": query_id,
                "need_kind": "software_safety_and_provenance_review",
                "summary": "Operator must verify identity, platform, version, rights, provenance, and safety posture before promotion.",
                "candidate_refs": [candidate["candidate_id"] for candidate in candidates if _candidate_query_id(candidate) == query_id],
                "review_required": True,
                "accepted_truth": False,
            }
        )
        if query_id not in candidate_query_ids:
            absences.append(
                {
                    "schema_version": "seed_batch_absence_summary.v0",
                    "absence_id": _stable_id("legacy_seed_absence", query_id),
                    "query_id": query_id,
                    "absence_kind": "no_fixture_candidate",
                    "summary": "No fixture candidate was produced for this query.",
                    "review_required": True,
                    "accepted_truth": False,
                }
            )
    if not absences:
        absences.append(
            {
                "schema_version": "seed_batch_absence_summary.v0",
                "absence_id": _stable_id("legacy_seed_absence", BATCH_ID, "distribution_actions_absent"),
                "absence_kind": "download_install_execute_absent",
                "summary": "Fixture candidates exist, but download, install, execute, reviewed truth, and public index records are intentionally absent.",
                "review_required": True,
                "accepted_truth": False,
            }
        )
    return {
        "schema_version": "seed_batch_need_absence_packet.v0",
        "batch_id": BATCH_ID,
        "known_needs": known_needs,
        "absence_summaries": absences,
        "known_need_refs": [item["need_id"] for item in known_needs],
        "absence_refs": [item["absence_id"] for item in absences],
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_legacy_software_snapshot_refresh_handoff(
    review_packets: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    handoff = copy.deepcopy(review_packets["decision_preview"]["snapshot_refresh_handoff"])
    return {
        "schema_version": "seed_batch_snapshot_refresh_handoff.v0",
        "batch_id": BATCH_ID,
        "snapshot_refresh_handoff": handoff,
        "snapshot_refresh_handoff_refs": [handoff["handoff_id"]],
        "snapshot_refresh_executed": False,
        "requires_separate_snapshot_refresh_gate": True,
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_legacy_software_public_alpha_reassess_inputs(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "seed_batch_public_alpha_reassess_input.v0",
        "batch_id": BATCH_ID,
        "public_alpha_reassess_id": _stable_id("public_alpha_reassess_input", BATCH_ID),
        "candidate_count": int(result.get("candidate_count") or 0),
        "query_count": int(result.get("query_count") or 0),
        "review_batch_refs": list(result.get("review_batch_refs") or []),
        "snapshot_refresh_handoff_refs": list(result.get("snapshot_refresh_handoff_refs") or []),
        "reassess_note": "Use after review/local-apply/snapshot gates; this seed batch itself is not public launch readiness or software safety approval.",
        "public_launch_readiness_claimed": False,
        "production_readiness_claimed": False,
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_legacy_software_boundary_report(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    return {
        "schema_version": "seed_batch_boundary_report.v0",
        "batch_id": BATCH_ID,
        "seed_batch_outputs_are_not_truth": bool(merged_policy.get("seed_batch_outputs_are_not_truth", True)),
        "candidates_require_review": bool(merged_policy.get("candidates_require_review", True)),
        "operator_live_metadata_run_performed": bool(result.get("operator_live_metadata_run_performed", False)),
        "raw_live_response_committed": False,
        "cracks_keygens_serials_supported": False,
        "malware_clean_claims_created": False,
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def run_seed_batch_legacy_software(
    policy: Mapping[str, Any] | None = None,
    *,
    fixture: bool = True,
    archive_org_metadata: bool = False,
    operator_approved_live_metadata: bool = False,
    write_examples: bool = False,
) -> dict[str, Any]:
    if fixture or not archive_org_metadata:
        return run_legacy_software_fixture(policy, write_examples=write_examples)
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    query_set = load_legacy_software_query_set(merged_policy)
    query_plans = build_legacy_software_query_plans(query_set, merged_policy)
    metadata_plan = run_legacy_software_archive_org_metadata_candidates(
        query_plans,
        merged_policy,
        operator_approved_live_metadata=operator_approved_live_metadata,
    )
    return {
        "schema_version": "seed_batch_legacy_software_run.v0",
        "batch_id": BATCH_ID,
        "domain_id": DOMAIN_ID,
        "mode": metadata_plan["mode"],
        "query_set": query_set,
        "query_plans": query_plans,
        "archive_org_metadata_plan": metadata_plan,
        "query_count": len(query_set),
        "candidate_count": 0,
        "fixture_seed_batch_passed": False,
        "operator_live_metadata_run_performed": False,
        "raw_live_response_committed": False,
        "limitations": _limitations(),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def run_legacy_software_fixture(
    policy: Mapping[str, Any] | None = None,
    *,
    write_examples: bool = False,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    query_set = load_legacy_software_query_set(merged_policy)
    query_plans = build_legacy_software_query_plans(query_set, merged_policy)
    source_plans = build_legacy_software_source_plans(query_plans, merged_policy)
    raw_candidates = run_legacy_software_fixture_candidates(query_plans, merged_policy)
    candidates = normalize_legacy_software_candidates(raw_candidates, merged_policy)
    candidates = apply_legacy_software_suppressions(candidates, build_legacy_software_suppression_records(), merged_policy)
    candidate_index = build_legacy_software_candidate_index(candidates, merged_policy)
    scout_trails = build_legacy_software_scout_trails(candidates, merged_policy)
    review_packets = build_legacy_software_review_packets(candidates, scout_trails, merged_policy)
    need_absence = build_legacy_software_known_needs_and_absences(query_plans, candidates, merged_policy)
    snapshot_handoff = build_legacy_software_snapshot_refresh_handoff(review_packets, merged_policy)
    result: dict[str, Any] = {
        "schema_version": "seed_batch_legacy_software_run.v0",
        "batch_id": BATCH_ID,
        "domain_id": DOMAIN_ID,
        "mode": "fixture",
        "query_set": query_set,
        "query_plans": query_plans,
        "source_plans": source_plans,
        "suppressions": build_legacy_software_suppression_records(),
        "candidate_summaries": [_candidate_summary(candidate) for candidate in candidates],
        "candidate_index": candidate_index,
        "scout_trails": scout_trails,
        "review_packets": review_packets,
        "known_needs": need_absence["known_needs"],
        "absence_summaries": need_absence["absence_summaries"],
        "snapshot_refresh_handoff": snapshot_handoff,
        "query_count": len(query_set),
        "candidate_count": len(candidates),
        "source_plan_refs": [item["source_plan_id"] for item in source_plans],
        "candidate_refs": [candidate["candidate_id"] for candidate in candidates],
        "scout_refs": list(scout_trails["scout_refs"]),
        "review_batch_refs": list(review_packets["review_batch_refs"]),
        "known_need_refs": list(need_absence["known_need_refs"]),
        "absence_refs": list(need_absence["absence_refs"]),
        "snapshot_refresh_handoff_refs": list(snapshot_handoff["snapshot_refresh_handoff_refs"]),
        "public_alpha_reassess_refs": [],
        "fixture_seed_batch_passed": True,
        "operator_live_metadata_run_performed": False,
        "cracks_keygens_serials_supported": False,
        "malware_clean_claims_created": False,
        "limitations": _limitations(),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }
    public_alpha = build_legacy_software_public_alpha_reassess_inputs(result, merged_policy)
    result["public_alpha_reassess_input"] = public_alpha
    result["public_alpha_reassess_refs"] = [public_alpha["public_alpha_reassess_id"]]
    result["boundary_report"] = build_legacy_software_boundary_report(result, merged_policy)
    if write_examples:
        write_legacy_software_examples(result)
        result["examples_written"] = True
    else:
        result["examples_written"] = False
    return result


def write_legacy_software_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_legacy_software_fixture(write_examples=False))
    repo_root = Path(__file__).resolve().parents[2]
    base = root or repo_root / "examples" / "seed_batches" / "legacy_software"
    base.mkdir(parents=True, exist_ok=True)
    files = {
        "seed_batch_result.json": _result_summary(payload),
        "query_set.json": payload["query_set"],
        "query_plans.json": payload["query_plans"],
        "source_plans.json": payload["source_plans"],
        "suppressions.json": payload["suppressions"],
        "candidate_summaries.json": payload["candidate_summaries"],
        "candidate_index.json": payload["candidate_index"],
        "scout_trails.json": _scout_summary(payload["scout_trails"]),
        "review_batch_packet.json": payload["review_packets"]["review_batch_packet"],
        "known_needs.json": payload["known_needs"],
        "absence_summaries.json": payload["absence_summaries"],
        "snapshot_refresh_handoff.json": payload["snapshot_refresh_handoff"],
        "public_alpha_reassess_input.json": payload["public_alpha_reassess_input"],
        "boundary_report.json": payload["boundary_report"],
    }
    written = []
    for name, content in files.items():
        path = base / name
        path.write_text(json.dumps(content, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(str(path.relative_to(repo_root)))
    mirrors = {
        "examples/query_plans/legacy_software/query_plans.json": payload["query_plans"],
        "examples/candidates/legacy_software/candidate_summaries.json": payload["candidate_summaries"],
        "examples/candidates/legacy_software/candidate_index.json": payload["candidate_index"],
        "examples/scout/legacy_software/scout_trails.json": _scout_summary(payload["scout_trails"]),
        "examples/review_batch/legacy_software/review_batch_packet.json": payload["review_packets"]["review_batch_packet"],
        "examples/public_alpha/legacy_software/public_alpha_reassess_input.json": payload["public_alpha_reassess_input"],
    }
    for rel_path, content in mirrors.items():
        path = repo_root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(rel_path)
    return written


def _planner_compatible_plan(seed_plan: Mapping[str, Any]) -> dict[str, Any]:
    planner_plan = copy.deepcopy(seed_plan.get("planner_plan") or {})
    planner_plan["plan_id"] = seed_plan["plan_id"]
    planner_plan["domain_pack"] = _text(seed_plan.get("domain_id")) or DOMAIN_ID
    planner_plan["source_families"] = list(SOURCE_FAMILIES)
    planner_plan["source_actions"] = [
        {
            "source_family": family,
            "action_kind": "metadata_descriptor",
            "candidate_only": True,
            "review_required": True,
            "accepted_truth": False,
        }
        for family in SOURCE_FAMILIES
    ]
    return planner_plan


def _legacy_archive_query(raw_query: str) -> str:
    return (
        '(mediatype:software OR mediatype:texts OR mediatype:collection) '
        f'({_text(raw_query)} OR "offline installer" OR "portable" OR "driver" OR "support CD") '
        '-iso -crack -keygen -serial -warez -torrent -"driver updater"'
    )[:500]


def _source_locator(source_family: str, index: int, slug: str) -> dict[str, str]:
    if source_family == "internet_archive_metadata":
        return {
            "locator_kind": "archive_org_details_page",
            "url": f"https://archive.org/details/seed_legacy_software_{index:02d}_{slug}",
        }
    return {
        "locator_kind": "fixture_metadata_descriptor",
        "descriptor_ref": f"fixture://{source_family}/seed_legacy_software_{index:02d}_{slug}",
    }


def _candidate_summary(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "seed_batch_candidate_summary.v0",
        "batch_id": BATCH_ID,
        "candidate_id": _text(candidate.get("candidate_id")),
        "query_id": _candidate_query_id(candidate),
        "title": _text(candidate.get("title")),
        "source_family": _text(candidate.get("source_family")),
        "source_locator": copy.deepcopy(candidate.get("source_locator") if isinstance(candidate.get("source_locator"), Mapping) else {}),
        "domain_id": _text(candidate.get("domain_id")),
        "confidence_label": _text(candidate.get("confidence_label")),
        "fixture_derived": "fixture_derived" in list(candidate.get("limitations") or []),
        "suppressions": _text_list(candidate.get("suppressions")),
        "applied_suppressions": list(candidate.get("applied_suppressions") or []),
        "blocked_actions": ["download", "install_handoff", "execute", "package_download", "promote"],
        "review_required": True,
        "accepted_truth": False,
    }


def _result_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "seed_batch_legacy_software_run_summary.v0",
        "batch_id": payload.get("batch_id"),
        "domain_id": payload.get("domain_id"),
        "mode": payload.get("mode"),
        "query_count": payload.get("query_count"),
        "candidate_count": payload.get("candidate_count"),
        "source_plan_refs": list(payload.get("source_plan_refs") or []),
        "candidate_refs": list(payload.get("candidate_refs") or []),
        "scout_refs": list(payload.get("scout_refs") or []),
        "review_batch_refs": list(payload.get("review_batch_refs") or []),
        "known_need_refs": list(payload.get("known_need_refs") or []),
        "absence_refs": list(payload.get("absence_refs") or []),
        "snapshot_refresh_handoff_refs": list(payload.get("snapshot_refresh_handoff_refs") or []),
        "public_alpha_reassess_refs": list(payload.get("public_alpha_reassess_refs") or []),
        "fixture_seed_batch_passed": bool(payload.get("fixture_seed_batch_passed")),
        "operator_live_metadata_run_performed": False,
        "cracks_keygens_serials_supported": False,
        "malware_clean_claims_created": False,
        "limitations": list(payload.get("limitations") or []),
        "review_required": True,
        "accepted_truth": False,
        **_false_boundaries(),
    }


def _scout_summary(scout_trails: Mapping[str, Any]) -> dict[str, Any]:
    runs = scout_trails.get("scout_runs") or []
    return {
        "schema_version": "seed_batch_scout_trails_summary.v0",
        "batch_id": scout_trails.get("batch_id"),
        "scout_refs": list(scout_trails.get("scout_refs") or []),
        "run_count": len(runs),
        "relation_count": scout_trails.get("relation_count", 0),
        "related_path_count": scout_trails.get("related_path_count", 0),
        "workunit_seed_count": scout_trails.get("workunit_seed_count", 0),
        "sample_runs": [
            {
                "scout_run_id": run.get("scout_run_id"),
                "seed_candidate_id": run.get("seed_candidate_id"),
                "relation_count": run.get("relation_count", 0),
                "candidate_refs": list(run.get("candidate_refs") or [])[:6],
                "accepted_truth": False,
                "review_required": True,
            }
            for run in runs[:3]
        ],
        "review_required": True,
        "accepted_truth": False,
        **_false_boundaries(),
    }


def _candidate_query_id(candidate: Mapping[str, Any]) -> str:
    candidate_id = _text(candidate.get("candidate_id"))
    match = re.search(r"(legacy_software_q\d{2})", candidate_id)
    return match.group(1) if match else ""


def _suppression_applies(suppression: Mapping[str, Any], query_id: str) -> bool:
    applies = _text_list(suppression.get("applies_to_queries"))
    return "*" in applies or query_id in applies


def _limitations() -> list[str]:
    return [
        "seed_batch_outputs_are_not_truth",
        "fixture_mode_default",
        "review_required_before_promotion",
        "local_apply_is_separate_gate",
        "snapshot_refresh_is_separate_gate",
        "no_download",
        "no_extraction",
        "no_install",
        "no_execute",
        "no_public_launch_claim",
        "no_software_safety_claim",
    ]


def _false_boundaries() -> dict[str, bool]:
    return {
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "public_mutation_enabled": False,
        "operator_instance_mutated": False,
        "raw_live_response_committed": False,
        "download_performed": False,
        "extraction_executed": False,
        "install_execution_enabled": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _slug(value: str) -> str:
    slug = "_".join(re.findall(r"[a-z0-9]+", value.casefold()))
    return slug[:80] or "legacy_software"


def _text(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, (int, float)):
        return str(value)
    return ""


def _text_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [_text(value)]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [_text(item) for item in value if _text(item)]
    return []


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(parts, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"{prefix}:{digest}"


def _policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    if isinstance(policy, Mapping):
        merged.update(policy)
    return merged


def _assert_policy(policy: Mapping[str, Any]) -> None:
    required_true = {
        "seed_batch_outputs_are_not_truth",
        "candidates_require_review",
        "source_actions_bounded",
        "archive_org_metadata_candidates_allowed",
        "github_releases_metadata_fixture_allowed",
        "package_registry_metadata_fixture_allowed",
        "software_heritage_metadata_fixture_allowed",
        "live_metadata_optional_and_operator_gated",
    }
    missing = sorted(key for key in required_true if not bool(policy.get(key)))
    if missing:
        raise PermissionError(f"legacy seed batch policy missing required safety rules: {', '.join(missing)}")
    forbidden_true = {
        "reviewed_index_mutation_enabled",
        "public_index_mutation_enabled",
        "master_index_mutation_enabled",
        "automatic_candidate_acceptance_enabled",
        "raw_live_responses_committed",
        "downloads_enabled",
        "extraction_enabled",
        "install_execution_enabled",
        "model_provider_enabled",
        "deployment_enabled",
        "cracks_keygens_serials_supported",
        "malware_clean_claims_allowed",
    }
    enabled = sorted(key for key in forbidden_true if bool(policy.get(key)))
    if enabled:
        raise PermissionError(f"legacy seed batch policy enables forbidden behavior: {', '.join(enabled)}")
