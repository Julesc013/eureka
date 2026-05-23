"""Read-only deterministic G0 quality helpers.

G0 scores, explains, and groups fixture records. It never accepts evidence,
merges identity, calls providers, probes sources, or mutates indexes.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXED_CREATED_AT = "2026-05-22T00:00:00Z"

PROJECTION_PROFILES: tuple[str, ...] = (
    "operator_workbench",
    "public_web",
    "native_desktop_read_only",
)

REQUIRED_SCORE_SIGNALS: tuple[str, ...] = (
    "exact_title_match",
    "identifier_match",
    "alias_match",
    "domain_fit",
    "platform_fit",
    "version_fit",
    "source_trust_prior",
    "metadata_completeness",
    "provenance_strength",
    "evidence_support",
    "reviewed_status",
    "candidate_status",
    "source_cache_age",
    "file_manifest_relevance",
    "member_path_relevance",
    "scout_relation_strength",
    "domain_promote_rule_match",
    "domain_suppression_rule_match",
    "rights_risk_penalty",
    "safety_risk_penalty",
    "duplicate_penalty",
    "near_miss_penalty",
    "user_cost_penalty",
    "blocked_action_penalty",
)

REQUIRED_EXPLANATION_FACTORS: tuple[str, ...] = (
    "matched_query_term",
    "matched_alias",
    "matched_identifier",
    "matched_domain_hint",
    "matched_source_family",
    "matched_metadata_field",
    "matched_member_path",
    "matched_scout_relation",
    "reviewed_local_result",
    "provisional_candidate",
    "source_cache_only",
    "needs_review",
    "blocked_action",
    "known_absence",
    "near_miss",
    "duplicate_candidate",
    "uncertain_provenance",
    "rights_unknown",
    "safety_unknown",
)

REQUIRED_IDENTITY_GROUP_TYPES: tuple[str, ...] = (
    "same_object_candidate",
    "same_version_candidate",
    "same_release_candidate",
    "same_representation_candidate",
    "mirror_candidate",
    "duplicate_candidate",
    "near_miss_candidate",
    "wrong_platform_candidate",
    "wrong_version_candidate",
    "parent_bundle_candidate",
    "member_candidate",
    "related_but_distinct_candidate",
)

REQUIRED_USER_COST_CLASSES: tuple[str, ...] = (
    "direct_reviewed_result",
    "provisional_candidate_needs_review",
    "source_cache_hit_needs_evidence",
    "parent_bundle_known_member_unknown",
    "member_path_known",
    "file_manifest_only",
    "mention_only",
    "known_absence",
    "blocked_by_policy",
    "deferred_extraction_needed",
    "source_probe_needed",
    "manual_research_needed",
)

BLOCKED_ACTIONS: tuple[str, ...] = (
    "accept_evidence",
    "accept_identity_merge",
    "create_reviewed_record",
    "mutate_source_cache",
    "mutate_evidence_ledger",
    "mutate_candidate_index",
    "mutate_review_queue",
    "mutate_master_index",
    "mutate_public_index",
    "live_source_call",
    "source_probe",
    "download",
    "upload",
    "extract",
    "execute",
    "install",
    "emulate",
    "call_model_provider",
    "public_fanout",
    "deploy",
)


class G0QualityError(ValueError):
    """Raised when a G0 fixture or projection is invalid."""


def load_quality_fixture(path: str | Path) -> dict[str, Any]:
    """Load one deterministic G0 quality fixture."""
    return json.loads(_resolve_path(path).read_text(encoding="utf-8"))


def validate_score_signal(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one score signal record."""
    errors: list[str] = []
    signal_id = str(record.get("signal_id", ""))
    required = (
        "schema_version",
        "record_type",
        "signal_id",
        "description",
        "positive_or_negative",
        "score",
        "allowed_inputs",
        "required_explanation",
        "can_affect_public_projection",
        "review_required",
        "accepted_truth",
        "non_claims",
    )
    for field in required:
        if field not in record:
            errors.append(f"{signal_id or '<unknown>'}: missing required field {field}.")
    if record.get("schema_version") != "score_signal.v0":
        errors.append(f"{signal_id or '<unknown>'}: schema_version must be score_signal.v0.")
    if record.get("record_type") != "score_signal":
        errors.append(f"{signal_id or '<unknown>'}: record_type must be score_signal.")
    if record.get("accepted_truth") is not False:
        errors.append(f"{signal_id or '<unknown>'}: accepted_truth must be false.")
    if record.get("review_required") is not True:
        errors.append(f"{signal_id or '<unknown>'}: review_required must be true.")
    _assert_non_claims(record, errors, signal_id or "score_signal")
    return _report("score_signal_validation_report.v0", signal_id, errors)


def build_score_breakdown(
    result_record: Mapping[str, Any],
    query_context: Mapping[str, Any],
    domain_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic score decomposition for one fixture result."""
    domain_context = domain_context or {}
    result_ref = str(result_record.get("result_ref", "g0_result_unknown"))
    terms = _token_set(str(query_context.get("query_text", "")))
    title_tokens = _token_set(str(result_record.get("title", "")))
    aliases = " ".join(_string_list(result_record.get("aliases")))
    identifiers = " ".join(_string_list(result_record.get("identifiers")))
    promote_terms = set(_normalize_list(domain_context.get("promote_terms")))
    suppress_terms = set(_normalize_list(domain_context.get("suppress_terms")))
    source_preferences = set(_normalize_list(domain_context.get("source_preferences")))
    blocked_actions = _string_list(result_record.get("blocked_actions"))
    target_platform = str(query_context.get("target_platform", ""))
    result_platform = str(result_record.get("platform", ""))

    signal_inputs: list[tuple[str, float, str, str]] = [
        ("exact_title_match", 0.18 if terms and terms.issubset(title_tokens) else 0.0, "positive", "query terms match title"),
        ("identifier_match", 0.14 if _any_token_in_text(terms, identifiers) else 0.0, "positive", "query term matches identifier"),
        ("alias_match", 0.10 if _any_token_in_text(terms, aliases) else 0.0, "positive", "query term matches alias"),
        ("domain_fit", 0.12 if result_record.get("domain_id") == query_context.get("domain_id") else 0.0, "positive", "result domain matches query domain"),
        ("platform_fit", 0.10 if target_platform and target_platform == result_platform else -0.08 if target_platform and result_platform else 0.0, "positive", "platform compatibility compared"),
        ("version_fit", 0.05 if str(result_record.get("version", "")) and str(result_record.get("version")) in str(query_context.get("query_text", "")) else 0.0, "positive", "version token considered"),
        ("source_trust_prior", _trust_score(result_record), "positive", "source trust prior is fixture-only"),
        ("metadata_completeness", 0.10 * _float(result_record.get("metadata_completeness"), 0.0), "positive", "metadata completeness included"),
        ("provenance_strength", 0.10 * _float(result_record.get("provenance_strength"), 0.0), "positive", "provenance strength included"),
        ("evidence_support", 0.08 if _list(result_record.get("evidence_refs")) else 0.0, "positive", "evidence refs are counted as refs only, not accepted here"),
        ("reviewed_status", 0.10 if result_record.get("review_state") == "reviewed_fixture" else 0.0, "positive", "reviewed fixture posture considered"),
        ("candidate_status", 0.04 if result_record.get("review_state") in {"candidate", "needs_review"} else 0.0, "positive", "candidate posture considered"),
        ("source_cache_age", 0.02 if result_record.get("result_kind") == "source_cache_hit" else 0.0, "positive", "source cache fixture considered"),
        ("file_manifest_relevance", 0.05 if result_record.get("result_kind") == "f0_member_manifest" else 0.0, "positive", "F0 manifest relevance considered"),
        ("member_path_relevance", 0.05 if _list(result_record.get("member_paths")) else 0.0, "positive", "member path relevance considered"),
        ("scout_relation_strength", 0.05 if _list(result_record.get("scout_relations")) else 0.0, "positive", "SCOUT relation strength considered"),
        ("domain_promote_rule_match", 0.04 if promote_terms.intersection(title_tokens) else 0.0, "positive", "DOMAIN promote terms considered"),
        ("domain_suppression_rule_match", -0.10 if suppress_terms.intersection(title_tokens) else 0.0, "negative", "DOMAIN suppress terms considered"),
        ("rights_risk_penalty", -0.04 if result_record.get("rights_risk") in {"unknown", "high"} else 0.0, "negative", "rights uncertainty penalty considered"),
        ("safety_risk_penalty", -0.04 if result_record.get("safety_risk") in {"unknown", "high"} else 0.0, "negative", "safety uncertainty penalty considered"),
        ("duplicate_penalty", -0.04 if result_record.get("duplicate_candidate") else 0.0, "negative", "duplicate candidate penalty considered"),
        ("near_miss_penalty", -0.12 if _is_near_miss(result_record, query_context) else 0.0, "negative", "near miss penalty considered"),
        ("user_cost_penalty", -0.04 * _user_cost_weight(result_record), "negative", "estimated user effort penalty considered"),
        ("blocked_action_penalty", -0.02 * min(len(blocked_actions), 5), "negative", "blocked actions remain visible"),
    ]
    if result_record.get("source_family") in source_preferences:
        signal_inputs.append(("source_family_preference", 0.04, "positive", "preferred source family matched"))

    signals = [
        _score_signal(signal_id, result_ref, score, polarity, explanation)
        for signal_id, score, polarity, explanation in signal_inputs
    ]
    total_score = round(max(0.0, min(1.0, 0.50 + sum(_float(signal.get("score"), 0.0) for signal in signals))), 6)
    return {
        "schema_version": "score_breakdown.v0",
        "record_type": "score_breakdown",
        "score_breakdown_id": _stable_id("g0_score_breakdown", result_ref),
        "created_at": FIXED_CREATED_AT,
        "source_context": {"source_kind": "g0_quality_fixture"},
        "query_context": dict(query_context),
        "result_ref": result_ref,
        "domain_id": str(result_record.get("domain_id", query_context.get("domain_id", ""))),
        "score": total_score,
        "confidence": _confidence(total_score, result_record),
        "signals": signals,
        "positive_signal_count": len([signal for signal in signals if signal["score"] > 0]),
        "negative_signal_count": len([signal for signal in signals if signal["score"] < 0]),
        "explanation": "Deterministic fixture score with visible decomposition.",
        "uncertainty": _uncertainty(result_record),
        "limitations": [
            "score is not evidence",
            "score does not mutate ranking, search, or indexes",
            "fixture-only deterministic estimate",
        ],
        "accepted_truth": False,
        "review_required": True,
        "non_claims": _default_non_claims(),
    }


def build_explanation_packet(score_breakdown: Mapping[str, Any], result_record: Mapping[str, Any]) -> dict[str, Any]:
    """Build an explanation packet for one scored result."""
    result_ref = str(score_breakdown.get("result_ref") or result_record.get("result_ref", "g0_result_unknown"))
    top_positive = [signal for signal in _list(score_breakdown.get("signals")) if isinstance(signal, Mapping) and _float(signal.get("score"), 0.0) > 0]
    top_negative = [signal for signal in _list(score_breakdown.get("signals")) if isinstance(signal, Mapping) and _float(signal.get("score"), 0.0) < 0]
    blocked = sorted(set(BLOCKED_ACTIONS).intersection(set(_string_list(result_record.get("blocked_actions"))) | {"accept_evidence", "accept_identity_merge", "mutate_master_index"}))
    factors = [
        {
            "schema_version": "explanation_factor.v0",
            "record_type": "explanation_factor",
            "factor_type": _factor_type(str(signal.get("signal_id", ""))),
            "summary": str(signal.get("required_explanation", "")),
            "score_effect": signal.get("score", 0),
            "review_required": True,
            "accepted_truth": False,
        }
        for signal in top_positive[:6] + top_negative[:6]
    ]
    return {
        "schema_version": "explanation_packet.v0",
        "record_type": "explanation_packet",
        "explanation_id": _stable_id("g0_explanation", result_ref),
        "created_at": FIXED_CREATED_AT,
        "source_context": {"source_kind": "g0_quality_fixture"},
        "query_context": dict(_mapping(score_breakdown.get("query_context"))),
        "result_ref": result_ref,
        "domain_id": str(score_breakdown.get("domain_id", result_record.get("domain_id", ""))),
        "score": score_breakdown.get("score", 0),
        "confidence": score_breakdown.get("confidence", "low"),
        "explanation": "Result appears because deterministic fixture signals matched the query and domain context.",
        "factors": factors,
        "why_result_appeared": [
            "candidate or local result was present in the explicit G0 fixture",
            "query/domain/source/member signals were computed without live calls",
        ],
        "why_result_ranked_here": [
            f"score={score_breakdown.get('score', 0)} from visible score decomposition",
            f"positive_signals={score_breakdown.get('positive_signal_count', 0)} negative_signals={score_breakdown.get('negative_signal_count', 0)}",
        ],
        "why_result_is_limited": list(score_breakdown.get("limitations", [])),
        "why_actions_are_blocked": [
            f"{action}: G0 foundation is read-only and cannot perform this action"
            for action in blocked
        ],
        "what_would_improve_confidence": [
            "human review of candidate identity",
            "accepted evidence in a future reviewed review phase",
            "governed source/cache/provenance review",
        ],
        "what_remaining_work_exists": [
            "future production ranking policy",
            "future reviewed identity merge gate",
            "future public projection review",
        ],
        "blocked_actions": blocked,
        "uncertainty": score_breakdown.get("uncertainty", "review required"),
        "limitations": list(score_breakdown.get("limitations", [])),
        "accepted_truth": False,
        "review_required": True,
        "non_claims": _default_non_claims(),
    }


def build_identity_cluster_candidates(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Build provisional identity cluster candidates from fixture records."""
    groups: dict[str, list[Mapping[str, Any]]] = {}
    for record in records:
        key = _identity_key(record)
        groups.setdefault(key, []).append(record)
    clusters: list[dict[str, Any]] = []
    for key, members in sorted(groups.items()):
        if len(members) < 2:
            continue
        clusters.append(
            {
                "schema_version": "identity_cluster_candidate.v0",
                "record_type": "identity_cluster_candidate",
                "identity_cluster_id": _stable_id("g0_identity_cluster", key),
                "cluster_type": "same_object_candidate",
                "member_refs": [str(member.get("result_ref", "")) for member in members],
                "identity_key": key,
                "provisional": True,
                "accepted_identity_merge": False,
                "confidence": "medium",
                "explanation": "Title/identifier normalization suggests a provisional group.",
                "uncertainty": "requires human identity review",
                "limitations": ["no automatic merge", "source-specific locators preserved"],
                "accepted_truth": False,
                "review_required": True,
                "non_claims": _default_non_claims(),
                "created_at": FIXED_CREATED_AT,
            }
        )
    return {
        "schema_version": "identity_cluster_candidate_set.v0",
        "record_type": "identity_cluster_candidate_set",
        "identity_cluster_candidates": clusters,
        "accepted_identity_merge_created": False,
        "review_required": True,
        "accepted_truth": False,
        "non_claims": _default_non_claims(),
    }


def build_near_miss_candidates(records: Sequence[Mapping[str, Any]], query_context: Mapping[str, Any]) -> dict[str, Any]:
    """Build deterministic near-miss candidates from fixture records."""
    candidates: list[dict[str, Any]] = []
    target_platform = str(query_context.get("target_platform", ""))
    query_terms = _token_set(str(query_context.get("query_text", "")))
    for record in records:
        result_ref = str(record.get("result_ref", ""))
        reasons: list[str] = []
        if target_platform and record.get("platform") and record.get("platform") != target_platform:
            reasons.append("wrong_platform_candidate")
        if record.get("result_kind") == "parent_bundle":
            reasons.append("parent_bundle_candidate")
        if record.get("result_kind") == "known_absence":
            reasons.append("related_but_distinct_candidate")
        if not query_terms.intersection(_token_set(str(record.get("title", "")))):
            reasons.append("near_miss_candidate")
        if not reasons:
            continue
        candidates.append(
            {
                "schema_version": "near_miss_candidate.v0",
                "record_type": "near_miss_candidate",
                "near_miss_id": _stable_id("g0_near_miss", result_ref),
                "result_ref": result_ref,
                "mismatch_reasons": sorted(set(reasons)),
                "explanation": "Record is related but not an exact result for the current query.",
                "uncertainty": "near miss label is provisional",
                "limitations": ["near misses are not suppressed or accepted as truth"],
                "accepted_truth": False,
                "review_required": True,
                "non_claims": _default_non_claims(),
                "created_at": FIXED_CREATED_AT,
            }
        )
    return {
        "schema_version": "near_miss_candidate_set.v0",
        "record_type": "near_miss_candidate_set",
        "near_miss_candidates": candidates,
        "review_required": True,
        "accepted_truth": False,
        "non_claims": _default_non_claims(),
    }


def build_user_cost_score(result_record: Mapping[str, Any], action_posture: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a user-cost/actionability estimate for one fixture result."""
    action_posture = action_posture or {}
    cost_class = _user_cost_class(result_record)
    effort, actionability = _cost_details(cost_class)
    blocked = sorted(set(_string_list(action_posture.get("blocked_actions")) or BLOCKED_ACTIONS).union(_string_list(result_record.get("blocked_actions"))))
    allowed = sorted(set(_string_list(action_posture.get("allowed_actions")) or ["inspect", "explain", "request_review"]))
    return {
        "schema_version": "user_cost_score.v0",
        "record_type": "user_cost_score",
        "user_cost_score_id": _stable_id("g0_user_cost", str(result_record.get("result_ref", ""))),
        "created_at": FIXED_CREATED_AT,
        "source_context": {"source_kind": "g0_quality_fixture"},
        "query_context": {},
        "result_ref": str(result_record.get("result_ref", "")),
        "domain_id": str(result_record.get("domain_id", "")),
        "score": max(0.0, min(1.0, 1.0 - effort)),
        "confidence": "medium",
        "user_cost_class": cost_class,
        "effort_estimate": effort,
        "actionability_level": actionability,
        "allowed_actions": allowed,
        "blocked_actions": blocked,
        "future_workunit_seed": _future_workunit_seed(cost_class),
        "explanation": f"{cost_class} has {actionability} actionability and requires review before downstream use.",
        "uncertainty": "user cost is a deterministic estimate",
        "limitations": ["does not perform action", "does not make installability or safety claims"],
        "accepted_truth": False,
        "review_required": True,
        "non_claims": _default_non_claims(),
    }


def build_quality_console_view(records: Sequence[Mapping[str, Any]] | Mapping[str, Any], projection_profile: str = "operator_workbench") -> dict[str, Any]:
    """Build a read-only Workbench quality console view model."""
    if projection_profile not in PROJECTION_PROFILES:
        raise G0QualityError(f"unsupported projection profile: {projection_profile}")
    if isinstance(records, Mapping):
        fixture = records
        result_records = [dict(item) for item in _list(fixture.get("records")) if isinstance(item, Mapping)]
        query_context = _mapping(fixture.get("query_context"))
        domain_context = _mapping(fixture.get("domain_context"))
        action_posture = _mapping(fixture.get("action_posture"))
    else:
        result_records = [dict(item) for item in records if isinstance(item, Mapping)]
        query_context = {}
        domain_context = {}
        action_posture = {}

    score_breakdowns = [build_score_breakdown(record, query_context, domain_context) for record in result_records]
    explanations = [build_explanation_packet(score, record) for score, record in zip(score_breakdowns, result_records)]
    identity = build_identity_cluster_candidates(result_records)
    near_misses = build_near_miss_candidates(result_records, query_context)
    user_costs = [build_user_cost_score(record, action_posture) for record in result_records]
    operator_detail_visible = projection_profile == "operator_workbench"
    if not operator_detail_visible:
        for explanation in explanations:
            explanation["factors"] = explanation["factors"][:3]
        for record in result_records:
            record.pop("internal_notes", None)
    return {
        "schema_version": "quality_console_view.v0",
        "record_type": "quality_console_view",
        "view_id": f"g0_quality:{projection_profile}",
        "routes": [
            "/quality",
            "/quality/scores",
            "/quality/explanations",
            "/quality/identity",
            "/quality/near-misses",
            "/quality/user-cost",
            "/quality/blocked-actions",
        ],
        "projection_profile": projection_profile,
        "read_only": True,
        "operator_detail_visible": operator_detail_visible,
        "views": {
            "QualityOverviewView": {
                "result_count": len(result_records),
                "score_count": len(score_breakdowns),
                "explanation_count": len(explanations),
            },
            "ScoreSignalView": {"required_signal_ids": list(REQUIRED_SCORE_SIGNALS)},
            "ScoreBreakdownView": {"score_breakdowns": score_breakdowns},
            "ExplanationPacketView": {"explanation_packets": explanations},
            "IdentityClusterCandidateView": identity,
            "NearMissView": near_misses,
            "UserCostView": {"user_cost_scores": user_costs},
            "ActionabilityView": {"actionability_scores": user_costs},
            "BlockedActionExplanationView": {"blocked_actions": list(BLOCKED_ACTIONS)},
        },
        "blocked_actions": list(BLOCKED_ACTIONS),
        "accepted_truth": False,
        "review_required": True,
        "non_claims": _default_non_claims(),
        "created_at": FIXED_CREATED_AT,
    }


def _score_signal(signal_id: str, result_ref: str, score: float, polarity: str, explanation: str) -> dict[str, Any]:
    return {
        "schema_version": "score_signal.v0",
        "record_type": "score_signal",
        "score_signal_id": _stable_id("g0_score_signal", f"{result_ref}:{signal_id}"),
        "signal_id": signal_id,
        "description": explanation,
        "positive_or_negative": polarity,
        "score": round(score, 6),
        "allowed_inputs": ["fixture_record", "query_context", "domain_context"],
        "required_explanation": explanation,
        "can_affect_public_projection": False,
        "review_required": True,
        "accepted_truth": False,
        "non_claims": _default_non_claims(),
        "created_at": FIXED_CREATED_AT,
    }


def _default_non_claims() -> dict[str, bool]:
    return {
        "fake_evidence_created": False,
        "fake_verified_records_created": False,
        "accepted_identity_merge_created": False,
        "live_source_call_performed": False,
        "source_probe_executed": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "operator_instance_mutated": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _assert_non_claims(record: Mapping[str, Any], errors: list[str], label: str) -> None:
    claims = _mapping(record.get("non_claims"))
    for key, expected in _default_non_claims().items():
        if claims.get(key) is not expected:
            errors.append(f"{label}: non_claims.{key} must be {str(expected).lower()}.")


def _report(schema_version: str, record_id: str, errors: Sequence[str]) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "record_id": record_id,
        "status": "valid" if not errors else "invalid",
        "errors": list(errors),
    }


def _resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = (REPO_ROOT / candidate).resolve()
    return candidate


def _stable_id(prefix: str, value: Any) -> str:
    text = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()[:48] or "record"
    return f"{prefix}_{slug}"


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in _list(value)]


def _normalize_list(value: Any) -> list[str]:
    return [item.lower().replace("_", " ") for item in _string_list(value)]


def _token_set(text: str) -> set[str]:
    return {token for token in re.split(r"[^a-zA-Z0-9]+", text.lower()) if token}


def _any_token_in_text(tokens: set[str], text: str) -> bool:
    text_tokens = _token_set(text)
    return bool(tokens.intersection(text_tokens))


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _trust_score(record: Mapping[str, Any]) -> float:
    trust = str(record.get("source_trust", "unknown"))
    return {"reviewed": 0.08, "known_source": 0.05, "source_cache": 0.03, "unknown": 0.0}.get(trust, 0.0)


def _confidence(score: float, record: Mapping[str, Any]) -> str:
    if record.get("review_state") == "reviewed_fixture" and score >= 0.70:
        return "medium_high"
    if score >= 0.60:
        return "medium"
    return "low"


def _uncertainty(record: Mapping[str, Any]) -> str:
    if record.get("review_state") == "reviewed_fixture":
        return "fixture reviewed label only; no new truth accepted"
    if record.get("result_kind") == "known_absence":
        return "absence is scoped to fixture only"
    return "candidate requires review"


def _is_near_miss(record: Mapping[str, Any], query_context: Mapping[str, Any]) -> bool:
    target_platform = str(query_context.get("target_platform", ""))
    return bool(target_platform and record.get("platform") and record.get("platform") != target_platform)


def _user_cost_weight(record: Mapping[str, Any]) -> float:
    return {
        "reviewed_local_result": 0.0,
        "ia_metadata_candidate": 1.0,
        "source_cache_hit": 1.4,
        "f0_member_manifest": 1.6,
        "scout_discovery_candidate": 1.2,
        "known_absence": 1.8,
        "parent_bundle": 1.5,
    }.get(str(record.get("result_kind", "")), 1.0)


def _user_cost_class(record: Mapping[str, Any]) -> str:
    result_kind = str(record.get("result_kind", ""))
    if result_kind == "reviewed_local_result":
        return "direct_reviewed_result"
    if result_kind == "ia_metadata_candidate":
        return "provisional_candidate_needs_review"
    if result_kind == "source_cache_hit":
        return "source_cache_hit_needs_evidence"
    if result_kind == "parent_bundle":
        return "parent_bundle_known_member_unknown"
    if _list(record.get("member_paths")):
        return "member_path_known"
    if result_kind == "f0_member_manifest":
        return "file_manifest_only"
    if result_kind == "known_absence":
        return "known_absence"
    if result_kind == "policy_blocked":
        return "blocked_by_policy"
    if result_kind == "source_probe_needed":
        return "source_probe_needed"
    if result_kind == "mention_only":
        return "mention_only"
    return "manual_research_needed"


def _cost_details(cost_class: str) -> tuple[float, str]:
    return {
        "direct_reviewed_result": (0.05, "high"),
        "provisional_candidate_needs_review": (0.35, "medium"),
        "source_cache_hit_needs_evidence": (0.50, "medium_low"),
        "parent_bundle_known_member_unknown": (0.65, "low"),
        "member_path_known": (0.45, "medium"),
        "file_manifest_only": (0.60, "low"),
        "mention_only": (0.70, "low"),
        "known_absence": (0.80, "low"),
        "blocked_by_policy": (0.90, "blocked"),
        "deferred_extraction_needed": (0.85, "blocked"),
        "source_probe_needed": (0.80, "blocked"),
        "manual_research_needed": (0.75, "low"),
    }.get(cost_class, (0.75, "low"))


def _future_workunit_seed(cost_class: str) -> str:
    return {
        "source_cache_hit_needs_evidence": "review_source_cache_hit",
        "parent_bundle_known_member_unknown": "inspect_file_manifest",
        "file_manifest_only": "review_member_manifest",
        "blocked_by_policy": "request_operator_policy",
        "deferred_extraction_needed": "queue_future_extraction",
        "source_probe_needed": "defer_live_source_probe",
        "manual_research_needed": "manual_research_needed",
    }.get(cost_class, "review_result")


def _identity_key(record: Mapping[str, Any]) -> str:
    identifiers = _string_list(record.get("identifiers"))
    if identifiers:
        return identifiers[0].lower()
    title = re.sub(r"[^a-zA-Z0-9]+", "_", str(record.get("title", "")).lower()).strip("_")
    return title or str(record.get("result_ref", "unknown"))


def _factor_type(signal_id: str) -> str:
    return {
        "exact_title_match": "matched_query_term",
        "identifier_match": "matched_identifier",
        "alias_match": "matched_alias",
        "domain_fit": "matched_domain_hint",
        "source_trust_prior": "matched_source_family",
        "metadata_completeness": "matched_metadata_field",
        "member_path_relevance": "matched_member_path",
        "scout_relation_strength": "matched_scout_relation",
        "reviewed_status": "reviewed_local_result",
        "candidate_status": "provisional_candidate",
        "source_cache_age": "source_cache_only",
        "blocked_action_penalty": "blocked_action",
        "near_miss_penalty": "near_miss",
        "duplicate_penalty": "duplicate_candidate",
        "provenance_strength": "uncertain_provenance",
        "rights_risk_penalty": "rights_unknown",
        "safety_risk_penalty": "safety_unknown",
    }.get(signal_id, "needs_review")
