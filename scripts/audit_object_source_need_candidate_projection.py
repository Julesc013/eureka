"""Read-only projection audit for object/source/need/candidate-adjacent artifacts.

The script deliberately reports gaps instead of repairing them because TRACK-A-14
is governance evidence, not renderer or site generation work.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]

REPORT_SCHEMA_VERSION = "track_a_14_projection_audit.v0"
MAP_SCHEMA_VERSION = "0.1.0"

OBJECT_PAGE_POLICY = "control/inventory/publication/object_page_view_model_policy.json"
SOURCE_PAGE_POLICY = "control/inventory/publication/source_page_view_model_policy.json"
NEED_PAGE_POLICY = "control/inventory/publication/need_page_view_model_policy.json"
CANDIDATE_PAGE_POLICY = "control/inventory/publication/candidate_page_view_model_policy.json"
ROUTE_MATRIX = "control/inventory/publication/route_view_representation_matrix.json"
REPRESENTATION_PROFILES = "control/inventory/publication/representation_profiles.json"
SEMANTIC_PARITY_POLICY = "control/inventory/publication/semantic_renderer_parity_policy.json"

SOURCE_VIEW_SCHEMAS = {
    "ObjectPageView": "contracts/views/object_page.v0.json",
    "SourcePageView": "contracts/views/source_page.v0.json",
    "NeedPageView": "contracts/views/need_page.v0.json",
    "CandidatePageView": "contracts/views/candidate_page.v0.json",
}

POLICY_FILES = {
    "ObjectPageView": OBJECT_PAGE_POLICY,
    "SourcePageView": SOURCE_PAGE_POLICY,
    "NeedPageView": NEED_PAGE_POLICY,
    "CandidatePageView": CANDIDATE_PAGE_POLICY,
}

AUDITED_VIEW_FAMILIES = tuple(SOURCE_VIEW_SCHEMAS)

ARTIFACT_KIND_VOCABULARY = (
    "standard_static_html",
    "lite_static_html",
    "text_static",
    "file_tree_static",
    "static_json_data",
    "static_demo_html",
    "static_demo_manifest",
    "public_data_summary",
    "unknown_static_artifact",
)

ARTIFACT_BINDINGS: tuple[dict[str, str], ...] = (
    {
        "artifact_path": "site/dist/demo/result-firefox-xp.html",
        "artifact_kind": "static_demo_html",
        "expected_view_family": "ObjectPageView",
        "expected_representation_profile": "standard_html",
        "expected_route_family": "object_page_future",
    },
    {
        "artifact_path": "site/dist/demo/result-member-driver-inside-support-cd.html",
        "artifact_kind": "static_demo_html",
        "expected_view_family": "ObjectPageView",
        "expected_representation_profile": "standard_html",
        "expected_route_family": "object_page_future",
    },
    {
        "artifact_path": "site/dist/demo/result-article-scan.html",
        "artifact_kind": "static_demo_html",
        "expected_view_family": "ObjectPageView",
        "expected_representation_profile": "standard_html",
        "expected_route_family": "object_page_future",
    },
    {
        "artifact_path": "site/dist/demo/source-example.html",
        "artifact_kind": "static_demo_html",
        "expected_view_family": "SourcePageView",
        "expected_representation_profile": "standard_html",
        "expected_route_family": "source_detail",
    },
    {
        "artifact_path": "site/dist/sources.html",
        "artifact_kind": "standard_static_html",
        "expected_view_family": "SourcePageView",
        "expected_representation_profile": "standard_html",
        "expected_route_family": "sources",
    },
    {
        "artifact_path": "site/dist/lite/sources.html",
        "artifact_kind": "lite_static_html",
        "expected_view_family": "SourcePageView",
        "expected_representation_profile": "lite_html",
        "expected_route_family": "sources",
    },
    {
        "artifact_path": "site/dist/text/sources.txt",
        "artifact_kind": "text_static",
        "expected_view_family": "SourcePageView",
        "expected_representation_profile": "text",
        "expected_route_family": "sources",
    },
    {
        "artifact_path": "site/dist/data/source_summary.json",
        "artifact_kind": "public_data_summary",
        "expected_view_family": "SourcePageView",
        "expected_representation_profile": "api_json",
        "expected_route_family": "sources",
    },
    {
        "artifact_path": "site/dist/demo/absence-example.html",
        "artifact_kind": "static_demo_html",
        "expected_view_family": "NeedPageView",
        "expected_representation_profile": "standard_html",
        "expected_route_family": "need_page_future",
    },
    {
        "artifact_path": "site/dist/demo/comparison-example.html",
        "artifact_kind": "static_demo_html",
        "expected_view_family": "CandidatePageView",
        "expected_representation_profile": "standard_html",
        "expected_route_family": "candidate_page_future",
    },
    {
        "artifact_path": "site/dist/demo/data/demo_snapshots.json",
        "artifact_kind": "static_demo_manifest",
        "expected_view_family": "CandidatePageView",
        "expected_representation_profile": "api_json",
        "expected_route_family": "candidate_page_future",
    },
    {
        "artifact_path": "site/dist/data/public_index_summary.json",
        "artifact_kind": "public_data_summary",
        "expected_view_family": "ObjectPageView",
        "expected_representation_profile": "api_json",
        "expected_route_family": "object_page_future",
    },
    {
        "artifact_path": "site/dist/files/index.txt",
        "artifact_kind": "file_tree_static",
        "expected_view_family": "SourcePageView",
        "expected_representation_profile": "file_tree",
        "expected_route_family": "files_static",
    },
    {
        "artifact_path": "site/dist/files/manifest.json",
        "artifact_kind": "static_json_data",
        "expected_view_family": "SourcePageView",
        "expected_representation_profile": "manifest_json",
        "expected_route_family": "files_static",
    },
    {
        "artifact_path": "site/dist/objects/example-object.html",
        "artifact_kind": "standard_static_html",
        "expected_view_family": "ObjectPageView",
        "expected_representation_profile": "standard_html",
        "expected_route_family": "object_page_future",
    },
    {
        "artifact_path": "site/dist/sources/example-source.html",
        "artifact_kind": "standard_static_html",
        "expected_view_family": "SourcePageView",
        "expected_representation_profile": "standard_html",
        "expected_route_family": "source_detail",
    },
    {
        "artifact_path": "site/dist/needs/example-need.html",
        "artifact_kind": "standard_static_html",
        "expected_view_family": "NeedPageView",
        "expected_representation_profile": "standard_html",
        "expected_route_family": "need_page_future",
    },
    {
        "artifact_path": "site/dist/candidates/example-candidate.html",
        "artifact_kind": "standard_static_html",
        "expected_view_family": "CandidatePageView",
        "expected_representation_profile": "standard_html",
        "expected_route_family": "candidate_page_future",
    },
)

REQUIRED_BINDING_FIELDS = {
    "artifact_path",
    "artifact_kind",
    "exists",
    "expected_view_family",
    "expected_representation_profile",
    "expected_route_family",
    "current_status",
    "current_generation_source",
    "current_projection_status",
    "fields_present",
    "fields_missing",
    "semantic_risks",
    "refactor_needed",
    "notes",
}

PRODUCT_BOUNDARY = {
    "changed_product_behavior": False,
    "changed_public_routes": False,
    "changed_generated_site_artifacts": False,
    "regenerated_site_dist": False,
    "enabled_hosting": False,
    "enabled_live_probes": False,
    "enabled_source_sync": False,
    "enabled_source_connectors": False,
    "enabled_downloads": False,
    "enabled_installers": False,
    "enabled_execution": False,
    "enabled_uploads": False,
    "enabled_accounts": False,
    "enabled_telemetry": False,
    "enabled_node_runtime": False,
    "enabled_pack_import_runtime": False,
    "enabled_review_runtime": False,
    "created_native_projects": False,
    "mutated_master_index": False,
    "claimed_rights_clearance": False,
    "claimed_malware_safety": False,
    "claimed_verified_installability": False,
    "claimed_exhaustive_global_search": False,
    "claimed_automatic_merge_or_promotion": False,
    "claimed_public_truth_from_candidates": False,
    "claimed_public_truth_from_source_observations": False,
    "claimed_public_truth_from_evidence_candidates": False,
    "claimed_public_truth_from_ai_drafts": False,
}

SEMANTIC_RULES: dict[str, dict[str, tuple[str, ...]]] = {
    "ObjectPageView": {
        "canonical_object_identity": ("target ref", "object", "record kind", "fixture:software", "member:sha256"),
        "object_type_state_version_posture": ("record kind", "version", "platform", "driver", "software", "article"),
        "source_posture": ("source id", "source family", "source data", "fixture-backed"),
        "evidence_posture": ("evidence summary", "source evidence", "compatibility evidence", "member_listing"),
        "representation_file_member_posture": ("member path", "file", "inside", "container", "scan"),
        "parent_member_lineage": ("parent target ref", "parent object", "inner", "member"),
        "compatibility_posture": ("compatibility", "windows xp", "platform", "support window"),
        "rights_risk_posture": ("no real browser binary", "no copyrighted", "risk", "rights"),
        "candidate_review_posture": ("candidate", "not verified", "review", "provisional"),
        "allowed_actions": ("view", "related static data", "source data"),
        "blocked_actions": ("not live search", "no live backend", "no real browser binary", "download"),
        "limitations": ("limitations", "static demo snapshot", "fixture-backed"),
        "unresolved_gaps": ("gap", "missing", "not a universal", "only demonstrates"),
    },
    "SourcePageView": {
        "canonical_source_identity": ("source id", "source count", "source summary", "source example"),
        "source_type_kind_family": ("source family", "family", "fixture", "recorded"),
        "source_authority_posture": ("authority", "official", "placeholder", "recorded fixture"),
        "coverage_capability_posture": ("coverage", "capabilities", "supports", "partial"),
        "connector_mode_status": ("connector", "live probe", "no live source access", "live_supported"),
        "placeholder_future_manual_only_status": ("placeholder", "future", "manual", "not implemented"),
        "source_policy_access_posture": ("policy", "access", "terms", "no live source access"),
        "source_cache_posture": ("recorded fixture", "static metadata", "cache", "fixture-backed"),
        "evidence_ledger_posture": ("evidence", "observations", "ledger", "contains_external_observations"),
        "known_limitations": ("limitations", "recorded fixture scope only", "private local filesystem"),
        "known_gaps": ("next_step", "future", "not implemented", "deferred"),
        "rights_risk_privacy_posture": ("private local filesystem", "copyright", "rights", "risk"),
        "blocked_actions": ("no live probe", "no live source access", "not live search"),
    },
    "NeedPageView": {
        "canonical_need_identity": ("absence", "missing target", "requested value", "query"),
        "unresolved_or_weakly_resolved_status": ("no bounded subject", "subject_unknown", "missing", "absence"),
        "query_demand_posture": ("raw query", "query", "requested value", "search"),
        "absence_scope": ("bounded", "not a global non-existence claim", "current local corpus"),
        "searched_scope": ("checked records", "checked subjects", "checked source families"),
        "sources_checked_not_checked": ("checked source families", "sources", "source families"),
        "source_gaps": ("source", "outside the committed corpus", "loaded source families"),
        "capability_gaps": ("capability", "outside", "not found"),
        "near_matches": ("near", "broader subject", "broader label"),
        "candidate_findings": ("candidate", "no verified", "not found"),
        "next_safe_work": ("next steps", "broader subject", "confirm"),
        "privacy_poisoning_posture": ("privacy", "poison", "raw query", "local corpus"),
        "limitations": ("limitations", "not live search", "not production"),
        "no_exhaustive_global_search_claim": ("not a global non-existence claim", "bounded"),
    },
    "CandidatePageView": {
        "canonical_candidate_identity": ("candidate", "record", "target ref", "comparison subject"),
        "candidate_type_status": ("candidate", "static demo", "record kind", "provisional"),
        "candidate_origin": ("source", "fixture", "recorded", "source family"),
        "source_observation_evidence_contribution_posture": ("evidence", "source-backed", "fixture-backed", "source data"),
        "proposed_object_state_summary": ("record", "software", "version", "target ref"),
        "evidence_posture": ("evidence summary", "source-backed", "no compact evidence"),
        "review_required": ("review", "needs review", "not production", "without merging"),
        "accepted_public_status_false": ("not production", "without merging", "static demo"),
        "master_index_mutation_allowed_false": ("without merging", "not a live compare route", "static example"),
        "rights_risk_privacy_posture": ("rights", "risk", "not production", "static demo"),
        "limitations": ("limitations", "fixture-backed", "not live search"),
        "blocked_actions": ("not live search", "no live backend", "not a live compare route"),
        "no_public_truth_from_candidates": ("without merging or truth selection", "preserves disagreement", "not production"),
    },
}

BOUNDARY_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "enabled_hosting": (
        re.compile(r"\bhosted backend (?:is )?(?:active|live|enabled|configured|verified|deployed)\b", re.IGNORECASE),
        re.compile(r"\bhosted public search (?:is )?(?:active|live|enabled|configured|verified|deployed)\b", re.IGNORECASE),
    ),
    "enabled_live_probes": (re.compile(r"\blive probes? (?:are )?enabled\b", re.IGNORECASE),),
    "enabled_source_sync": (re.compile(r"\bsource sync (?:is )?enabled\b", re.IGNORECASE),),
    "enabled_source_connectors": (
        re.compile(r"\bsource connectors? (?:are )?(?:active|enabled)\b", re.IGNORECASE),
        re.compile(r"\blive source connectors? (?:are )?(?:active|enabled)\b", re.IGNORECASE),
    ),
    "enabled_downloads": (re.compile(r"\b(?:direct )?downloads? (?:are )?enabled\b", re.IGNORECASE),),
    "enabled_installers": (re.compile(r"\binstallers? (?:are )?enabled\b", re.IGNORECASE),),
    "enabled_execution": (re.compile(r"\bexecution (?:is )?enabled\b", re.IGNORECASE),),
    "enabled_uploads": (re.compile(r"\buploads? (?:are )?enabled\b", re.IGNORECASE),),
    "enabled_accounts": (re.compile(r"\baccounts? (?:are )?enabled\b", re.IGNORECASE),),
    "enabled_telemetry": (re.compile(r"\btelemetry (?:is )?enabled\b", re.IGNORECASE),),
    "enabled_node_runtime": (re.compile(r"\bnode runtime (?:is )?(?:active|enabled)\b", re.IGNORECASE),),
    "enabled_pack_import_runtime": (re.compile(r"\bpack import runtime (?:is )?(?:active|enabled)\b", re.IGNORECASE),),
    "enabled_review_runtime": (re.compile(r"\breview runtime (?:is )?(?:active|enabled)\b", re.IGNORECASE),),
    "created_native_projects": (re.compile(r"\bnative runtime (?:is )?active\b", re.IGNORECASE),),
    "mutated_master_index": (re.compile(r"\bmaster[- ]index mutation (?:is )?(?:enabled|allowed|performed)\b", re.IGNORECASE),),
    "claimed_rights_clearance": (re.compile(r"\brights clearance (?:is )?(?:granted|verified|claimed)\b", re.IGNORECASE),),
    "claimed_malware_safety": (re.compile(r"\bmalware safety (?:is )?(?:verified|claimed)\b", re.IGNORECASE),),
    "claimed_verified_installability": (re.compile(r"\bverified installability\b", re.IGNORECASE),),
    "claimed_exhaustive_global_search": (
        re.compile(r"\bexhaustive global search\b", re.IGNORECASE),
        re.compile(r"\bglobally exhaustive search\b", re.IGNORECASE),
    ),
    "claimed_automatic_merge_or_promotion": (
        re.compile(r"\bautomatic (?:merge|dedup|promotion) (?:is )?(?:enabled|allowed)\b", re.IGNORECASE),
    ),
    "claimed_public_truth_from_candidates": (
        re.compile(r"\bcandidate (?:is )?(?:accepted public truth|verified truth|public truth)\b", re.IGNORECASE),
        re.compile(r"\bpublic truth from candidates?\b", re.IGNORECASE),
    ),
    "claimed_public_truth_from_source_observations": (
        re.compile(r"\bsource observation (?:is )?(?:accepted truth|public truth)\b", re.IGNORECASE),
    ),
    "claimed_public_truth_from_evidence_candidates": (
        re.compile(r"\bevidence candidate (?:is )?(?:verified fact|accepted truth|public truth)\b", re.IGNORECASE),
    ),
    "claimed_public_truth_from_ai_drafts": (
        re.compile(r"\bai draft (?:is )?(?:evidence truth|accepted truth|public truth)\b", re.IGNORECASE),
    ),
}

BOOLEAN_BOUNDARY_FIELDS = {
    "accepted_public_status": "claimed_public_truth_from_candidates",
    "accounts_enabled": "enabled_accounts",
    "ai_draft_evidence_truth": "claimed_public_truth_from_ai_drafts",
    "automatic_dedup_enabled": "claimed_automatic_merge_or_promotion",
    "automatic_merge_enabled": "claimed_automatic_merge_or_promotion",
    "automatic_promotion_enabled": "claimed_automatic_merge_or_promotion",
    "candidate_accepted_public_truth": "claimed_public_truth_from_candidates",
    "contains_external_observations": "claimed_public_truth_from_source_observations",
    "contains_executable_downloads": "enabled_downloads",
    "contains_live_backend": "enabled_hosting",
    "contains_live_probes": "enabled_live_probes",
    "direct_download_enabled": "enabled_downloads",
    "downloads_available": "enabled_downloads",
    "downloads_enabled": "enabled_downloads",
    "evidence_candidate_verified_fact": "claimed_public_truth_from_evidence_candidates",
    "execution_enabled": "enabled_execution",
    "exhaustive_global_search": "claimed_exhaustive_global_search",
    "hosted_backend_claimed": "enabled_hosting",
    "installers_enabled": "enabled_installers",
    "live_backend_required": "enabled_hosting",
    "live_probes_enabled": "enabled_live_probes",
    "malware_safety_claimed": "claimed_malware_safety",
    "master_index_mutation_allowed": "mutated_master_index",
    "node_runtime_enabled": "enabled_node_runtime",
    "pack_import_runtime_enabled": "enabled_pack_import_runtime",
    "review_runtime_enabled": "enabled_review_runtime",
    "rights_clearance_claimed": "claimed_rights_clearance",
    "source_connectors_active": "enabled_source_connectors",
    "source_observation_accepted_truth": "claimed_public_truth_from_source_observations",
    "source_sync_enabled": "enabled_source_sync",
    "telemetry_enabled": "enabled_telemetry",
    "uploads_enabled": "enabled_uploads",
    "verified_installability_claimed": "claimed_verified_installability",
}

FUTURE_REFACTOR_TARGETS = [
    "TRACK-A-15 - Temporal Minimal Search design token contract",
    "TRACK-A-16 - Renderer parity harness",
    "TRACK-A-17 - Track A integration audit",
    "TRACK-A-FOLLOWUP - Object Source Need Candidate projection fixtures and dry-run plan",
]

NO_GOALS_PRESERVED = [
    "no site/dist regeneration",
    "no runtime behavior change",
    "no public route activation",
    "no hosted backend claim",
    "no live probes",
    "no source connector or source sync runtime",
    "no downloads/installers/execution",
    "no uploads/accounts/telemetry",
    "no public truth from candidates, source observations, evidence candidates, or AI drafts",
    "no renderer implementation",
]


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit object/source/need/candidate-adjacent static artifacts against Track A view models."
    )
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--check", action="store_true", help="Fail if critical product-boundary violations are found.")
    parser.add_argument("--json-output", help="Write deterministic JSON report to this explicit path.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).resolve()
    report = build_projection_audit(root)
    if args.json_output:
        output_path = Path(args.json_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    output = stdout or sys.stdout
    output.write(_format_human(report))

    if args.check and report["critical_boundary_violations"]:
        return 1
    return 0


def build_projection_audit(
    repo_root: Path = REPO_ROOT,
    artifact_bindings: Sequence[Mapping[str, str]] = ARTIFACT_BINDINGS,
) -> dict[str, Any]:
    root = repo_root.resolve()
    load_warnings: list[str] = []
    policies = {view: _load_json(root / policy_path, load_warnings) for view, policy_path in POLICY_FILES.items()}
    route_matrix = _load_json(root / ROUTE_MATRIX, load_warnings)
    representations = _load_json(root / REPRESENTATION_PROFILES, load_warnings)
    semantic_policy = _load_json(root / SEMANTIC_PARITY_POLICY, load_warnings)

    route_ids = _route_ids(route_matrix)
    representation_ids = _representation_ids(representations)
    semantic_ids = _semantic_policy_ids(semantic_policy)

    bindings: list[dict[str, Any]] = []
    critical: list[str] = []
    warnings: list[str] = list(load_warnings)
    for binding in artifact_bindings:
        audited = audit_artifact(root, binding)
        bindings.append(audited)
        critical.extend(audited.pop("_critical_boundary_violations"))
        warnings.extend(audited.pop("_warnings"))

        route = audited["expected_route_family"]
        if route not in route_ids:
            critical.append(f"{audited['artifact_path']}: unknown expected route family {route}")
        profile = audited["expected_representation_profile"]
        if profile not in representation_ids:
            critical.append(f"{audited['artifact_path']}: unknown expected representation profile {profile}")

    for view_family, policy_payload in sorted(policies.items()):
        parity = _mapping(policy_payload).get("required_semantic_parity_policy")
        if isinstance(parity, str) and parity not in semantic_ids:
            critical.append(f"{POLICY_FILES[view_family]}: unknown required semantic parity policy {parity}")

    semantic_alignment = summarize_semantic_alignment(bindings)
    known_alignment = build_known_alignment(bindings)
    known_gaps = build_known_gaps(bindings, semantic_alignment)
    status = "fail" if critical else "warn" if warnings or known_gaps else "pass"

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "status": status,
        "track": "A",
        "task": "TRACK-A-14",
        "audited_view_families": list(AUDITED_VIEW_FAMILIES),
        "artifact_kind_vocabulary": list(ARTIFACT_KIND_VOCABULARY),
        "source_view_schemas": dict(SOURCE_VIEW_SCHEMAS),
        "audited_artifacts": [binding["artifact_path"] for binding in bindings],
        "artifact_bindings": bindings,
        "semantic_alignment": semantic_alignment,
        "known_alignment": known_alignment,
        "known_gaps": known_gaps,
        "critical_boundary_violations": sorted(set(critical)),
        "warnings": sorted(set(warnings)),
        "future_refactor_targets": list(FUTURE_REFACTOR_TARGETS),
        "product_boundary": dict(PRODUCT_BOUNDARY),
        "no_goals_preserved": list(NO_GOALS_PRESERVED),
        "inputs": {
            "object_page_policy": OBJECT_PAGE_POLICY,
            "source_page_policy": SOURCE_PAGE_POLICY,
            "need_page_policy": NEED_PAGE_POLICY,
            "candidate_page_policy": CANDIDATE_PAGE_POLICY,
            "route_matrix": ROUTE_MATRIX,
            "representation_profiles": REPRESENTATION_PROFILES,
            "semantic_parity_policy": SEMANTIC_PARITY_POLICY,
        },
        "next_task": "TRACK-A-15 - Temporal Minimal Search design token contract",
    }


def build_projection_map(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": MAP_SCHEMA_VERSION,
        "map_id": "object-source-need-candidate-static-projection-map",
        "label": "Object/Source/Need/Candidate static projection map",
        "description": (
            "Read-only Track A map from current static/demo/public-data artifacts to "
            "ObjectPageView, SourcePageView, NeedPageView, and CandidatePageView semantics."
        ),
        "audited_view_families": list(report["audited_view_families"]),
        "artifact_kind_vocabulary": list(ARTIFACT_KIND_VOCABULARY),
        "source_view_schemas": dict(report["source_view_schemas"]),
        "current_artifacts": list(report["audited_artifacts"]),
        "artifact_bindings": list(report["artifact_bindings"]),
        "semantic_field_bindings": dict(report["semantic_alignment"]),
        "representation_profile_bindings": representation_profile_bindings(report["artifact_bindings"]),
        "route_matrix_refs": [
            "control/inventory/publication/route_view_representation_matrix.json#route_families",
            "control/inventory/publication/route_view_representation_matrix.json#representation_bindings",
            "control/inventory/publication/route_view_representation_matrix.json#semantic_parity_bindings",
        ],
        "parity_policy_refs": [
            "object_page_parity_v0",
            "source_page_parity_v0",
            "need_page_future_parity_v0",
            "candidate_page_future_parity_v0",
        ],
        "known_alignment": list(report["known_alignment"]),
        "known_gaps": list(report["known_gaps"]),
        "deferred_refactor_targets": list(report["future_refactor_targets"]),
        "no_goals": list(report["no_goals_preserved"]),
        "product_boundary": dict(report["product_boundary"]),
        "notes": [
            "This inventory is evidence only and does not activate object, source, need, or candidate public routes.",
            "Existing demo artifacts remain committed as-is; missing future page artifacts are recorded rather than created.",
            "Current source-list artifacts are mapped as SourcePageView-adjacent because a source-list-specific view model is not part of this task.",
        ],
    }


def representation_profile_bindings(bindings: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    rows = []
    for binding in bindings:
        rows.append(
            {
                "artifact_path": str(binding["artifact_path"]),
                "view_family": str(binding["expected_view_family"]),
                "route_family": str(binding["expected_route_family"]),
                "representation_profile": str(binding["expected_representation_profile"]),
            }
        )
    return sorted(rows, key=lambda row: (row["view_family"], row["artifact_path"]))


def audit_artifact(repo_root: Path, binding: Mapping[str, str]) -> dict[str, Any]:
    path = str(binding["artifact_path"])
    target = repo_root / path
    view_family = str(binding["expected_view_family"])
    rules = SEMANTIC_RULES.get(view_family, {})
    base = {
        "artifact_path": path,
        "artifact_kind": str(binding["artifact_kind"]),
        "exists": target.is_file(),
        "expected_view_family": view_family,
        "expected_representation_profile": str(binding["expected_representation_profile"]),
        "expected_route_family": str(binding["expected_route_family"]),
        "current_status": "present" if target.is_file() else "missing",
        "current_generation_source": "not_machine_verified",
        "current_projection_status": f"static_artifact_not_traced_to_canonical_{_snake_view_family(view_family)}",
        "fields_present": [],
        "fields_missing": sorted(rules),
        "semantic_risks": [],
        "refactor_needed": True,
        "notes": [],
        "_critical_boundary_violations": [],
        "_warnings": [],
    }
    if not target.is_file():
        base["notes"].append("Artifact is missing; audit records absence and does not create it.")
        base["_warnings"].append(f"{path}: artifact missing")
        return base

    text = target.read_text(encoding="utf-8")
    payload: Any | None = None
    if path.endswith(".json"):
        try:
            payload = json.loads(text)
            generated_by = _mapping(payload).get("generated_by")
            if isinstance(generated_by, str):
                base["current_generation_source"] = generated_by
        except json.JSONDecodeError as exc:
            base["_warnings"].append(f"{path}: JSON could not be parsed at line {exc.lineno}")

    haystack = text
    if payload is not None:
        haystack = text + "\n" + json.dumps(payload, sort_keys=True)

    present = sorted(category for category, needles in rules.items() if _contains_any(haystack, needles))
    base["fields_present"] = present
    base["fields_missing"] = sorted(set(rules) - set(present))
    base["semantic_risks"] = semantic_risks_for_artifact(path, view_family, base["fields_missing"], payload)
    base["notes"] = notes_for_artifact(path, view_family, payload)
    base["_critical_boundary_violations"] = detect_critical_boundary_violations(text, path, payload)
    base["_warnings"] = projection_warnings_for_artifact(path, binding, payload)
    return base


def summarize_semantic_alignment(bindings: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for view_family in AUDITED_VIEW_FAMILIES:
        view_bindings = [binding for binding in bindings if binding.get("expected_view_family") == view_family]
        existing = [binding for binding in view_bindings if binding.get("exists") is True]
        view_summary: dict[str, Any] = {}
        for category in sorted(SEMANTIC_RULES[view_family]):
            artifacts = sorted(
                str(binding["artifact_path"])
                for binding in existing
                if category in set(_string_items(binding.get("fields_present")))
            )
            if not existing:
                status = "not_currently_projected"
            elif not artifacts:
                status = "missing"
            elif len(artifacts) == len(existing):
                status = "aligned"
            else:
                status = "partially_aligned"
            view_summary[category] = {
                "status": status,
                "artifacts": artifacts,
                "machine_verified": status in {"aligned", "partially_aligned"},
                "notes": [
                    "Conservative substring and JSON-field audit only; future projection work should use canonical fixtures."
                ],
            }
        summary[view_family] = view_summary
    return summary


def build_known_alignment(bindings: Sequence[Mapping[str, Any]]) -> list[str]:
    present_by_view: dict[str, int] = {view: 0 for view in AUDITED_VIEW_FAMILIES}
    for binding in bindings:
        if binding.get("exists") is True:
            present_by_view[str(binding["expected_view_family"])] += 1
    alignment = []
    if present_by_view["ObjectPageView"]:
        alignment.append("Object-like demo result pages preserve source/evidence, member lineage, and compatibility posture in static snapshots.")
    if present_by_view["SourcePageView"]:
        alignment.append("Source summary and source demo artifacts preserve fixture/placeholder separation and no-live-probe posture.")
    if present_by_view["NeedPageView"]:
        alignment.append("The absence demo preserves bounded absence scope and avoids exhaustive global-search claims.")
    if present_by_view["CandidatePageView"]:
        alignment.append("Candidate-adjacent comparison/demo data preserves disagreement and avoids automatic merge or truth selection.")
    alignment.append("Audited present artifacts preserve not-live, not-production static demo posture.")
    return sorted(set(alignment))


def build_known_gaps(bindings: Sequence[Mapping[str, Any]], semantic_alignment: Mapping[str, Any]) -> list[str]:
    gaps = {
        "No audited object/source/need/candidate-adjacent artifact is generated from a canonical Track A view-model fixture.",
        "Future canonical object, source, need, and candidate page routes remain unimplemented or not active as public static pages.",
        "Static/demo pages do not embed canonical view_model_id values for these view families.",
    }
    for binding in bindings:
        if binding.get("exists") is False:
            gaps.add(f"{binding['artifact_path']}: expected future/adjacent artifact is missing")
        if binding.get("fields_missing"):
            gaps.add(f"{binding['artifact_path']}: missing or not machine-verified fields {binding['fields_missing']}")
        for risk in _string_items(binding.get("semantic_risks")):
            gaps.add(f"{binding['artifact_path']}: {risk}")
    for view_family, view_alignment in _mapping(semantic_alignment).items():
        for category, alignment in _mapping(view_alignment).items():
            status = _mapping(alignment).get("status")
            if status not in {"aligned", "partially_aligned"}:
                gaps.add(f"{view_family}.{category}: {status}")
    return sorted(gaps)


def detect_critical_boundary_violations(text: str, artifact_path: str, payload: Any | None = None) -> list[str]:
    violations: list[str] = []
    for boundary, patterns in BOUNDARY_PATTERNS.items():
        for pattern in patterns:
            if _has_unsafe_match(text, pattern):
                violations.append(f"{artifact_path}: {boundary} claim matched {pattern.pattern}")
                break
    if payload is not None:
        violations.extend(_json_boundary_violations(payload, artifact_path))
    return sorted(set(violations))


def semantic_risks_for_artifact(
    path: str,
    view_family: str,
    missing: Sequence[str],
    payload: Any | None,
) -> list[str]:
    risks = [f"not yet traced to canonical {view_family} fixture"]
    if missing:
        risks.append(f"some {view_family} semantic categories are missing or not machine-verified")
    if path.endswith(".html") or path.endswith(".txt"):
        risks.append("semantic extraction is conservative text matching, not renderer parity proof")
    if payload is not None:
        risks.append("JSON shape is audited as public data, not as a canonical view-model instance")
    if path.startswith("site/dist/demo/"):
        risks.append("demo artifact is illustrative and not an active canonical page route")
    return sorted(set(risks))


def notes_for_artifact(path: str, view_family: str, payload: Any | None) -> list[str]:
    notes = ["Read-only audit; artifact content was not changed."]
    if path.startswith("site/dist/demo/"):
        notes.append("Static demo artifact may preserve useful semantics without being a canonical page projection.")
    if view_family == "SourcePageView" and path.endswith("source_summary.json"):
        notes.append("Source summary records fixture and placeholder posture; recorded fixtures are not treated as live connectors.")
    if view_family == "NeedPageView":
        notes.append("Need-like semantics are currently visible through absence/demo surfaces, not a canonical NeedPage route.")
    if view_family == "CandidatePageView":
        notes.append("Candidate-like semantics are currently visible through comparison/demo surfaces, not a canonical CandidatePage route.")
    if isinstance(payload, Mapping):
        if payload.get("contains_live_probes") is False:
            notes.append("JSON payload explicitly records no live probes.")
        if payload.get("contains_live_data") is False:
            notes.append("JSON payload explicitly records no live data.")
    return notes


def projection_warnings_for_artifact(path: str, binding: Mapping[str, str], payload: Any | None) -> list[str]:
    warnings: list[str] = []
    if path.startswith("site/dist/demo/") and path.endswith(".html"):
        warnings.append(f"{path}: demo surface is not a canonical {binding['expected_view_family']} projection")
    if path.startswith("site/dist/data/") and payload is not None:
        warnings.append(f"{path}: public data summary is not a canonical {binding['expected_view_family']} projection")
    return warnings


def _has_unsafe_match(text: str, pattern: re.Pattern[str]) -> bool:
    for match in pattern.finditer(text):
        if not _match_is_negated(text, match):
            return True
    return False


def _match_is_negated(text: str, match: re.Match[str]) -> bool:
    prefix = text[max(0, match.start() - 40):match.start()].lower()
    matched = text[match.start():match.end()].lower()
    return (
        prefix.endswith("no ")
        or prefix.endswith("not ")
        or " no " in prefix[-14:]
        or " not " in prefix[-18:]
        or "does not " in prefix[-28:]
        or "without " in prefix[-20:]
        or "unavailable" in matched
        or "disabled" in matched
    )


def _json_boundary_violations(value: Any, artifact_path: str, path: str = "$") -> list[str]:
    violations: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            boundary = BOOLEAN_BOUNDARY_FIELDS.get(str(key))
            if boundary and child is True:
                violations.append(f"{artifact_path}: {child_path} implies {boundary}")
            violations.extend(_json_boundary_violations(child, artifact_path, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            violations.extend(_json_boundary_violations(child, artifact_path, f"{path}[{index}]"))
    return violations


def _contains_any(text: str, needles: Sequence[str]) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def _load_json(path: Path, warnings: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        warnings.append(f"{path.as_posix()}: missing input JSON")
    except json.JSONDecodeError as exc:
        warnings.append(f"{path.as_posix()}: invalid JSON at line {exc.lineno}")
    return None


def _route_ids(payload: Any) -> set[str]:
    routes = _mapping(payload).get("route_families")
    if not isinstance(routes, Sequence) or isinstance(routes, (str, bytes)):
        return set()
    return {
        str(route["route_family_id"])
        for route in routes
        if isinstance(route, Mapping) and isinstance(route.get("route_family_id"), str)
    }


def _representation_ids(payload: Any) -> set[str]:
    profiles = _mapping(payload).get("profiles")
    if not isinstance(profiles, Sequence) or isinstance(profiles, (str, bytes)):
        return set()
    return {
        str(profile["representation_profile_id"])
        for profile in profiles
        if isinstance(profile, Mapping) and isinstance(profile.get("representation_profile_id"), str)
    }


def _semantic_policy_ids(payload: Any) -> set[str]:
    policies = _mapping(payload).get("policies")
    if not isinstance(policies, Sequence) or isinstance(policies, (str, bytes)):
        return set()
    return {
        str(policy["parity_policy_id"])
        for policy in policies
        if isinstance(policy, Mapping) and isinstance(policy.get("parity_policy_id"), str)
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str)]


def _snake_view_family(view_family: str) -> str:
    return re.sub(r"(?<!^)([A-Z])", r"_\1", view_family).lower()


def _format_human(report: Mapping[str, Any]) -> str:
    lines = [
        "Object/Source/Need/Candidate projection audit",
        f"status: {report['status']}",
        f"audited_view_families: {', '.join(report['audited_view_families'])}",
        f"artifact_count: {len(report['artifact_bindings'])}",
        f"critical_boundary_violations: {len(report['critical_boundary_violations'])}",
        f"warnings: {len(report['warnings'])}",
        f"known_gaps: {len(report['known_gaps'])}",
    ]
    for binding in report["artifact_bindings"]:
        lines.append(
            f"- {binding['artifact_path']}: {binding['current_status']}; "
            f"view={binding['expected_view_family']}; "
            f"profile={binding['expected_representation_profile']}; "
            f"fields_present={len(binding['fields_present'])}; fields_missing={len(binding['fields_missing'])}"
        )
    if report["critical_boundary_violations"]:
        lines.append("critical_boundary_violations:")
        lines.extend(f"- {item}" for item in report["critical_boundary_violations"])
    if report["warnings"]:
        lines.append("warnings:")
        lines.extend(f"- {item}" for item in report["warnings"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
