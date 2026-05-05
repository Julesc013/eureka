from __future__ import annotations

from typing import Any

from runtime.engine.ranking.models import RankingFactor


FACTOR_TYPES = (
    "evidence_strength",
    "provenance_strength",
    "source_posture",
    "intrinsic_identifier_match",
    "compatibility_evidence",
    "platform_os_match",
    "architecture_match",
    "runtime_dependency_match",
    "representation_availability",
    "member_access",
    "freshness",
    "conflict_penalty",
    "uncertainty_penalty",
    "candidate_penalty",
    "rights_risk_caution",
    "action_safety",
    "absence_gap_transparency",
    "result_merge_group_quality",
    "identity_resolution_strength",
    "manual_review_status",
)

VALID_CATEGORY_VALUES = {
    "absent",
    "weak",
    "medium",
    "strong",
    "conflicting",
    "unknown",
    "not_applicable",
}

POSITIVE_TYPES = {
    "evidence_strength",
    "provenance_strength",
    "source_posture",
    "intrinsic_identifier_match",
    "compatibility_evidence",
    "platform_os_match",
    "architecture_match",
    "runtime_dependency_match",
    "representation_availability",
    "member_access",
    "freshness",
    "result_merge_group_quality",
    "identity_resolution_strength",
    "manual_review_status",
}

NEGATIVE_TYPES = {"conflict_penalty", "uncertainty_penalty", "candidate_penalty"}
INFO_TYPES = {"rights_risk_caution", "action_safety", "absence_gap_transparency"}


def extract_evidence_factors(result: dict[str, Any]) -> list[RankingFactor]:
    evidence = _dict(result.get("evidence"))
    source = _dict(result.get("source"))
    freshness = _dict(result.get("freshness"))
    return [
        _factor(
            "evidence_strength",
            _category(evidence.get("strength")),
            "Evidence strength is visible from public-safe evidence metadata.",
            f"Evidence refs: {_refs_text(evidence)}",
            evidence_refs=_refs(evidence),
        ),
        _factor(
            "provenance_strength",
            _category(evidence.get("provenance_strength")),
            "Provenance strength is represented as an explicit factor.",
            "Provenance strength is not a truth claim.",
            evidence_refs=_refs(evidence),
        ),
        _factor(
            "source_posture",
            _category(source.get("posture") or source.get("source_posture")),
            "Source posture is visible as metadata, not trust.",
            "Source posture is not rights clearance or source truth.",
        ),
        _factor(
            "intrinsic_identifier_match",
            "strong" if evidence.get("intrinsic_identifier_match") is True else "absent",
            "Intrinsic identifier/checksum match is explicit when present.",
            "Intrinsic identifier matching is a public-safe ranking factor only.",
            evidence_refs=_refs(evidence),
        ),
        _factor(
            "freshness",
            _category(freshness.get("status") or freshness.get("category")),
            "Freshness/staleness is visible when known.",
            "Freshness is informational for dry-run ranking and not production quality.",
        ),
    ]


def extract_compatibility_factors(result: dict[str, Any], target_profile: dict[str, Any] | None = None) -> list[RankingFactor]:
    compatibility = _dict(result.get("compatibility"))
    target_note = " Target profile was provided." if target_profile else ""
    return [
        _factor(
            "compatibility_evidence",
            _category(compatibility.get("evidence_strength")),
            "Compatibility evidence is considered only when public-safe.",
            "Compatibility evidence is not installability proof." + target_note,
        ),
        _factor(
            "platform_os_match",
            _category(compatibility.get("platform_os_match")),
            "Platform/OS fit is explicit when known.",
            "Platform-name similarity alone remains weak.",
        ),
        _factor(
            "architecture_match",
            _category(compatibility.get("architecture_match")),
            "Architecture/CPU/ABI fit is explicit when known.",
            "Architecture fit is metadata, not execution proof.",
        ),
        _factor(
            "runtime_dependency_match",
            _category(compatibility.get("runtime_dependency_match")),
            "Runtime/dependency fit is explicit when known.",
            "Dependency metadata is not dependency safety or installability.",
        ),
    ]


def extract_conflict_gap_factors(result: dict[str, Any]) -> list[RankingFactor]:
    conflicts = result.get("conflicts") or []
    gaps = result.get("gaps") or []
    limitations = tuple(str(item) for item in result.get("limitations") or [])
    uncertainty = "unknown" if limitations or _has_unknown(result) else "absent"
    return [
        _factor(
            "conflict_penalty",
            "conflicting" if conflicts else "absent",
            "Conflicts stay visible and are not suppressed.",
            f"{len(conflicts)} conflict item(s) recorded.",
            limitations=tuple(str(item) for item in conflicts),
        ),
        _factor(
            "uncertainty_penalty",
            uncertainty,
            "Unknowns and limitations stay visible.",
            "Uncertainty is not hidden by dry-run ranking.",
            limitations=limitations,
        ),
        _factor(
            "absence_gap_transparency",
            "medium" if gaps else "absent",
            "Gaps stay visible in ranking reasons.",
            f"{len(gaps)} gap item(s) recorded.",
            limitations=tuple(str(item) for item in gaps),
        ),
    ]


def extract_action_safety_factors(result: dict[str, Any]) -> list[RankingFactor]:
    actions = _dict(result.get("actions"))
    rights = _dict(result.get("rights_risk"))
    candidate_status = str(result.get("candidate_status") or result.get("status") or "unknown")
    grouping = _dict(result.get("grouping"))
    identity = _dict(result.get("identity"))
    manual_review = _dict(result.get("manual_review"))
    risky_enabled = actions.get("risky_actions_enabled") is True
    return [
        _factor(
            "candidate_penalty",
            "medium" if candidate_status in {"candidate", "provisional", "review_required"} else "absent",
            "Candidate/provisional status remains visible.",
            f"Candidate status: {candidate_status}",
        ),
        _factor(
            "rights_risk_caution",
            "medium" if rights.get("caution") or rights.get("review_required") else "absent",
            "Rights and risk cautions remain visible.",
            "No rights clearance, malware safety, or installability claim is made.",
            limitations=tuple(str(item) for item in rights.get("limitations") or []),
        ),
        _factor(
            "action_safety",
            "conflicting" if risky_enabled else "strong",
            "Risky actions are disabled for public-safe ranking.",
            "Download, install, execute, upload, and package-manager actions remain disabled.",
        ),
        _factor(
            "result_merge_group_quality",
            _category(grouping.get("quality")),
            "Grouping refs can inform display factors only.",
            "Grouping is not destructive merge or duplicate deletion.",
        ),
        _factor(
            "identity_resolution_strength",
            _category(identity.get("strength")),
            "Identity refs can inform duplicate/variant context.",
            "Identity relation is not source truth or canonical acceptance.",
        ),
        _factor(
            "manual_review_status",
            _category(manual_review.get("status") or result.get("review_status")),
            "Manual review status is explicit when present.",
            "Manual review status does not promote candidates.",
        ),
    ]


def compute_explicit_factor_summary(result: dict[str, Any], target_profile: dict[str, Any] | None = None) -> list[RankingFactor]:
    representation = _dict(result.get("representation"))
    factors = []
    factors.extend(extract_evidence_factors(result))
    factors.extend(extract_compatibility_factors(result, target_profile))
    factors.extend(
        [
            _factor(
                "representation_availability",
                _category(representation.get("availability")),
                "Representation availability is explicit when known.",
                "Availability is not download or install permission.",
            ),
            _factor(
                "member_access",
                _category(representation.get("member_access")),
                "Member-level access is considered when public-safe.",
                "Member access is not file retrieval or download enablement.",
            ),
        ]
    )
    factors.extend(extract_conflict_gap_factors(result))
    factors.extend(extract_action_safety_factors(result))
    return factors


def factor_sort_key(factors: list[RankingFactor], current_rank: int) -> tuple[int, ...]:
    positives = [factor for factor in factors if factor.direction == "positive"]
    negatives = [factor for factor in factors if factor.direction == "negative"]
    info = [factor for factor in factors if factor.direction == "informational"]
    return (
        -sum(1 for factor in positives if factor.category_value == "strong"),
        -sum(1 for factor in positives if factor.category_value == "medium"),
        -sum(1 for factor in positives if factor.category_value == "weak"),
        sum(1 for factor in negatives if factor.category_value == "conflicting"),
        sum(1 for factor in negatives if factor.category_value in {"strong", "medium", "weak", "unknown"}),
        -sum(1 for factor in info if factor.category_value in {"strong", "medium"}),
        current_rank,
    )


def _factor(
    factor_type: str,
    category_value: str,
    public_reason: str,
    audit_reason: str,
    *,
    evidence_refs: tuple[str, ...] = (),
    limitations: tuple[str, ...] = (),
) -> RankingFactor:
    if factor_type in NEGATIVE_TYPES:
        direction = "negative"
    elif factor_type in INFO_TYPES:
        direction = "informational"
    else:
        direction = "positive"
    return RankingFactor(
        factor_type=factor_type,
        direction=direction,
        category_value=category_value,
        public_reason=public_reason,
        audit_reason=audit_reason,
        evidence_refs=evidence_refs,
        limitations=limitations,
    )


def _category(value: Any) -> str:
    if isinstance(value, bool):
        return "strong" if value else "absent"
    text = str(value or "unknown").lower()
    aliases = {
        "reviewed_recorded": "medium",
        "source_backed": "medium",
        "fixture_backed": "medium",
        "reviewed": "strong",
        "candidate_ready_future": "weak",
        "compatible": "strong",
        "likely": "medium",
        "gap": "unknown",
        "none": "absent",
        "not_present": "absent",
    }
    text = aliases.get(text, text)
    return text if text in VALID_CATEGORY_VALUES else "unknown"


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _refs(value: dict[str, Any]) -> tuple[str, ...]:
    refs = value.get("refs") or value.get("evidence_refs") or []
    return tuple(str(ref) for ref in refs)


def _refs_text(value: dict[str, Any]) -> str:
    refs = _refs(value)
    return ", ".join(refs) if refs else "none"


def _has_unknown(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_has_unknown(child) for child in value.values())
    if isinstance(value, list):
        return any(_has_unknown(child) for child in value)
    return isinstance(value, str) and value.lower() in {"unknown", "not_checked", "not_available"}

