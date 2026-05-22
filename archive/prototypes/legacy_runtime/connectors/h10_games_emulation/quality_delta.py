"""Offline H10 games/emulation quality delta helpers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.normalizer_common import H10_SOURCE_IDS
from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.review_integration import (
    REVIEW_SEED_KEYS,
    detect_h10_review_product_boundary_violations,
    detect_h10_review_truth_boundary_violations,
)

FORBIDDEN_TRUE_KEYS = {
    "automatic_future_connector_approval", "compatibility_correctness",
    "compatibility_correctness_claimed", "content_safety", "content_safety_claimed",
    "disc_authenticity_claimed", "disc_authenticity_verified", "emulator_compatibility_verified",
    "exhaustive_global_coverage", "future_connector_auto_approval", "game_identity_verified",
    "hashset_correctness_verified", "installability_claimed", "installability_verified",
    "legal_acquisition_claimed", "legal_acquisition_verified", "malware_safety",
    "malware_safety_claimed", "playability_claimed", "playability_verified",
    "privacy_safety", "privacy_safety_claimed", "production_games_emulation_coverage",
    "production_readiness_claimed", "production_search_quality", "release_identity_verified",
    "rights_clearance", "rights_clearance_claimed", "rom_authenticity_claimed",
    "rom_authenticity_verified", "verified_authenticity", "verified_authenticity_claimed",
}


def build_h10_quality_delta(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    review = dict(inputs.get("review_integration_result") or inputs)
    sources = list(review.get("sources") or [])
    blocked_sources = list(review.get("blocked_sources") or [])
    fixture_outputs = list(review.get("used_fixture_outputs") or [])
    live_outputs = list(review.get("used_live_probe_outputs") or [])
    known_gaps = _known_gaps(review)
    metrics = {
        "source_count": len(sources) or len(H10_SOURCE_IDS),
        "fixture_sources_count": len({item.get("source_id") for item in fixture_outputs if item.get("source_id")}) or len(sources),
        "live_probe_sources_count": len({item.get("source_id") for item in live_outputs if item.get("status") == "live_probe_completed"}),
        "blocked_sources_count": len(blocked_sources),
        "normalized_record_count": len(review.get("source_cache_review_seeds", [])),
        "game_software_identity_candidate_count": len(review.get("game_software_identity_review_seeds", [])),
        "platform_release_edition_candidate_count": len(review.get("platform_release_edition_review_seeds", [])),
        "emulator_compatibility_candidate_count": len(review.get("emulator_compatibility_review_seeds", [])),
        "preservation_hashset_candidate_count": len(review.get("preservation_hashset_review_seeds", [])),
        "rom_disc_media_identity_candidate_count": len(review.get("rom_disc_media_identity_review_seeds", [])),
        "game_relation_candidate_count": len(review.get("game_relation_review_seeds", [])),
        "emulator_action_candidate_count": len(review.get("emulator_action_candidate_review_seeds", [])),
        "games_rights_safety_candidate_count": len(review.get("games_rights_safety_review_seeds", [])),
        "source_cache_candidate_count": len(review.get("source_cache_review_seeds", [])),
        "evidence_candidate_preview_count": len(review.get("evidence_candidate_review_seeds", [])),
        "review_seed_count": sum(len(review.get(key, [])) for key in REVIEW_SEED_KEYS),
        "coverage_preview_count": len(review.get("coverage_update_previews", [])),
        "scorecard_update_count": len(review.get("scorecard_updates", [])),
        "known_gap_count": len(known_gaps),
        "blocker_count": 0,
        "warning_count": len(review.get("warnings", [])) + (1 if blocked_sources else 0),
    }
    delta = {
        "schema_version": "h10_games_emulation_quality_delta_report.v0",
        "quality_delta_id": f"h10.quality_delta.{_digest(review)[:12]}.v0",
        "wave_id": "H10",
        "comparison_scope": "fixture_review_and_blocked_live_probe_evidence",
        **metrics,
        "per_source_deltas": [_per_source_delta(source_id, review, fixture_outputs, live_outputs, blocked_sources) for source_id in sorted(set(sources) or set(H10_SOURCE_IDS))],
        "limitations": [
            "Quality delta measures H10 review readiness only.",
            "Blocked live probes do not prove endpoint behavior.",
            "Games/emulation metadata is not game identity, release identity, emulator compatibility, hash-set correctness, ROM or disc authenticity, legal acquisition, playability, installability, rights clearance, malware safety, privacy safety, content safety, production coverage, or production quality proof.",
        ],
        "forbidden_claims": [
            "production_search_quality", "production_games_emulation_coverage",
            "exhaustive_global_coverage", "game_identity_verified",
            "release_identity_verified", "emulator_compatibility_verified",
            "hashset_correctness_verified", "rom_authenticity_verified",
            "disc_authenticity_verified", "legal_acquisition_verified",
            "playability_verified", "installability_verified", "rights_clearance",
            "malware_safety", "content_safety", "privacy_safety",
            "verified_authenticity", "automatic_future_connector_approval",
        ],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H10 quality delta is operational review evidence only."],
    }
    errors = detect_h10_quality_overclaim(delta, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return delta


def summarize_h10_quality_delta(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = detect_h10_quality_overclaim(delta, policy)
    return {
        "schema_version": "h10_quality_delta_summary.v0",
        "status": "pass" if not errors else "invalid",
        "quality_delta_id": delta.get("quality_delta_id"),
        "source_count": delta.get("source_count", 0),
        "fixture_sources_count": delta.get("fixture_sources_count", 0),
        "live_probe_sources_count": delta.get("live_probe_sources_count", 0),
        "blocked_sources_count": delta.get("blocked_sources_count", 0),
        "game_software_identity_candidate_count": delta.get("game_software_identity_candidate_count", 0),
        "platform_release_edition_candidate_count": delta.get("platform_release_edition_candidate_count", 0),
        "emulator_compatibility_candidate_count": delta.get("emulator_compatibility_candidate_count", 0),
        "preservation_hashset_candidate_count": delta.get("preservation_hashset_candidate_count", 0),
        "rom_disc_media_identity_candidate_count": delta.get("rom_disc_media_identity_candidate_count", 0),
        "game_relation_candidate_count": delta.get("game_relation_candidate_count", 0),
        "emulator_action_candidate_count": delta.get("emulator_action_candidate_count", 0),
        "games_rights_safety_candidate_count": delta.get("games_rights_safety_candidate_count", 0),
        "review_seed_count": delta.get("review_seed_count", 0),
        "known_gap_count": delta.get("known_gap_count", 0),
        "blocker_count": delta.get("blocker_count", 0),
        "claims_game_identity_verified": False,
        "claims_release_identity_verified": False,
        "claims_emulator_compatibility_verified": False,
        "claims_hashset_correctness_verified": False,
        "claims_rom_authenticity": False,
        "claims_disc_authenticity": False,
        "claims_legal_acquisition": False,
        "claims_playability": False,
        "claims_installability": False,
        "claims_rights_clearance": False,
        "claims_malware_safety": False,
        "claims_content_safety": False,
        "claims_privacy_safety": False,
        "claims_verified_authenticity": False,
        "claims_production_readiness": False,
        "overclaim_errors": errors,
    }


def detect_h10_quality_overclaim(delta: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors = [f"quality overclaim: {path}=true" for path, key, value in _iter_key_values(delta) if key in FORBIDDEN_TRUE_KEYS and value is True]
    errors.extend(detect_h10_review_truth_boundary_violations(delta, policy))
    errors.extend(detect_h10_review_product_boundary_violations(delta, policy))
    return sorted(dict.fromkeys(errors))


def _per_source_delta(source_id: str, review: Mapping[str, Any], fixture_outputs: list[Mapping[str, Any]], live_outputs: list[Mapping[str, Any]], blocked_sources: list[str]) -> dict[str, Any]:
    represented = source_id in review.get("sources", [])
    return {
        "source_id": source_id,
        "fixture_output_integrated": any(item.get("source_id") == source_id for item in fixture_outputs) or represented,
        "live_probe_completed": any(item.get("source_id") == source_id and item.get("status") == "live_probe_completed" for item in live_outputs),
        "live_probe_blocked": source_id in blocked_sources,
        "game_software_identity_review_seed_created": represented,
        "platform_release_edition_review_seed_created": represented,
        "emulator_compatibility_review_seed_created": represented,
        "preservation_hashset_review_seed_created": represented,
        "rom_disc_media_identity_review_seed_created": represented,
        "game_relation_review_seed_created": represented,
        "emulator_action_candidate_review_seed_created": represented,
        "games_rights_safety_review_seed_created": represented,
        "source_cache_review_seed_created": represented,
        "evidence_review_seed_created": represented,
        "limitations": ["Fixture/local review only; not accepted source, evidence, candidate, game/release/platform/emulator/hash-set/ROM-disc/relation/action/rights/safety, or production proof."],
    }


def _known_gaps(review: Mapping[str, Any]) -> list[str]:
    gaps: list[str] = []
    if review.get("blocked_sources"):
        gaps.append("operator_approval_missing_for_live_metadata_probes")
    if len(review.get("source_cache_review_seeds", [])) < len(H10_SOURCE_IDS):
        gaps.append("not_all_sources_have_review_seeds")
    if not any(item.get("status") == "live_probe_completed" for item in review.get("used_live_probe_outputs", [])):
        gaps.append("approved_live_probe_outputs_not_available")
    return sorted(dict.fromkeys(gaps))


def _truth_boundary() -> dict[str, bool]:
    return {
        "quality_delta_is_public_truth": False,
        "production_search_quality": False,
        "production_games_emulation_coverage": False,
        "exhaustive_global_coverage": False,
        "game_identity_verified": False,
        "release_identity_verified": False,
        "emulator_compatibility_verified": False,
        "hashset_correctness_verified": False,
        "rom_authenticity_verified": False,
        "disc_authenticity_verified": False,
        "legal_acquisition_verified": False,
        "playability_verified": False,
        "installability_verified": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "content_safety_claimed": False,
        "privacy_safety_claimed": False,
        "verified_authenticity_claimed": False,
        "production_readiness_claimed": False,
        "automatic_future_connector_approval": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_execution": False,
        "enabled_acquisition_actions": False,
        "enabled_crawling": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _iter_key_values(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, inner in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield path, str(key), inner
            yield from _iter_key_values(inner, path)
    elif isinstance(value, list):
        for index, inner in enumerate(value):
            yield from _iter_key_values(inner, f"{prefix}[{index}]")


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()
