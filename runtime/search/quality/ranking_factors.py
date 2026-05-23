"""Deterministic ranking factor helpers for shadow-only scoring."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def score_exact_identifier_match(item: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> float:
    query_identifiers = set(_strings((context or {}).get("identifiers") or (context or {}).get("query_identifiers")))
    item_identifiers = set(_strings(item.get("identifiers")))
    return 1.0 if query_identifiers and query_identifiers.intersection(item_identifiers) else 0.0


def score_title_or_name_match(item: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> float:
    query_terms = _normalized_terms((context or {}).get("query_terms") or (context or {}).get("query_text"))
    title_terms = _normalized_terms(item.get("title") or item.get("name") or item.get("candidate_label"))
    if not query_terms or not title_terms:
        return 0.0
    overlap = len(set(query_terms).intersection(title_terms))
    return min(1.0, overlap / max(len(set(query_terms)), 1))


def score_version_match(item: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> float:
    wanted = _norm((context or {}).get("version") or (context or {}).get("version_or_state"))
    current = _norm(item.get("version") or item.get("version_or_state"))
    return 1.0 if wanted and current and wanted == current else 0.0


def score_platform_or_compatibility_match(item: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> float:
    wanted = _norm((context or {}).get("platform") or (context or {}).get("platform_or_context"))
    current = _norm(item.get("platform") or item.get("platform_or_context"))
    return 1.0 if wanted and current and wanted == current else 0.0


def score_source_trust_lane(item: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> float:
    lane = _norm(item.get("source_trust_lane") or item.get("source_lane"))
    return {"reviewed_fixture": 0.8, "source_cache_preview": 0.5, "candidate_only": 0.3, "policy_blocked": 0.0}.get(lane, 0.2)


def score_evidence_support(item: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> float:
    level = _norm(item.get("evidence_support_level") or item.get("evidence_support"))
    return {"strong_fixture": 0.8, "metadata_fixture": 0.55, "weak_fixture": 0.25, "none": 0.0}.get(level, 0.0)


def score_review_status(item: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> float:
    status = _norm(item.get("review_status"))
    return {"reviewed_fixture": 0.6, "review_seeded": 0.35, "needs_review": 0.15, "blocked": -0.4}.get(status, 0.0)


def score_extraction_member_match(item: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> float:
    return 0.35 if item.get("extraction_member_match") is True or item.get("member_match") is True else 0.0


def score_manifest_match(item: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> float:
    return 0.4 if item.get("manifest_match") is True else 0.0


def score_near_miss_penalty(item: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> float:
    return -0.75 if item.get("near_miss") is True or item.get("near_miss_type") else 0.0


def score_known_absence_signal(item: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> float:
    return -0.2 if item.get("known_absence") is True else 0.0


def score_rights_risk_penalty(item: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> float:
    risks = item.get("risk_flags") or item.get("rights_risk_flags") or []
    return -0.2 * len(risks) if isinstance(risks, list) else 0.0


def score_policy_block_penalty(item: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> float:
    return -1.0 if item.get("policy_blocked") is True or item.get("ranking_shadow_status") == "blocked_by_policy" else 0.0


def score_temporal_fit(item: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> float:
    wanted = str((context or {}).get("year") or "")
    current = str(item.get("year") or item.get("date_or_timestamp") or "")
    return 0.2 if wanted and wanted in current else 0.0


def score_completeness_signal(item: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> float:
    fields = item.get("completeness_fields") or []
    if isinstance(fields, list):
        return min(0.5, len([value for value in fields if value]) * 0.1)
    return 0.0


FACTOR_SCORERS = {
    "exact_identifier_match": score_exact_identifier_match,
    "title_or_name_match": score_title_or_name_match,
    "version_match": score_version_match,
    "platform_or_compatibility_match": score_platform_or_compatibility_match,
    "source_trust_lane": score_source_trust_lane,
    "evidence_support": score_evidence_support,
    "review_status": score_review_status,
    "extraction_member_match": score_extraction_member_match,
    "manifest_match": score_manifest_match,
    "near_miss_penalty": score_near_miss_penalty,
    "known_absence_signal": score_known_absence_signal,
    "rights_risk_penalty": score_rights_risk_penalty,
    "policy_block_penalty": score_policy_block_penalty,
    "recency_or_temporal_fit": score_temporal_fit,
    "completeness_signal": score_completeness_signal,
}


def _strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_norm(item) for item in value if _norm(item)]
    text = _norm(value)
    return [text] if text else []


def _normalized_terms(value: Any) -> list[str]:
    text = _norm(value)
    return [part for part in text.replace("-", " ").replace("_", " ").split() if part]


def _norm(value: Any) -> str:
    return str(value or "").strip().casefold()
