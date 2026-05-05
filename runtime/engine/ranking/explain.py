from __future__ import annotations

from runtime.engine.ranking.models import RankingFactor, RankingExplanationSummary


def build_ranking_explanation_summary(result: dict, factors: list[RankingFactor]) -> RankingExplanationSummary:
    result_id = str(result.get("result_id", "unknown_result"))
    return RankingExplanationSummary(
        result_id=result_id,
        user_visible_reason=build_user_visible_reason(result, factors),
        audit_reason=build_audit_reason(result, factors),
        caveats=_build_caveats(result, factors),
    )


def build_user_visible_reason(result: dict, factors: list[RankingFactor]) -> str:
    title = str(result.get("title") or result.get("result_id") or "Untitled result")
    positives = [factor for factor in factors if factor.direction == "positive" and factor.category_value in {"strong", "medium"}]
    negatives = [factor for factor in factors if factor.direction == "negative" and factor.category_value not in {"absent", "not_applicable"}]
    gaps = [factor for factor in factors if factor.factor_type == "absence_gap_transparency" and factor.category_value != "absent"]
    parts = [f"{title}: dry-run ranking uses explicit public factors only."]
    if positives:
        parts.append("Helpful factors include " + ", ".join(factor.factor_type for factor in positives[:4]) + ".")
    if negatives:
        parts.append("Cautions remain visible for " + ", ".join(factor.factor_type for factor in negatives[:3]) + ".")
    if gaps:
        parts.append("Known gaps are preserved in the explanation.")
    parts.append("No hidden score, suppression, rights clearance, malware safety, or installability claim is made.")
    return " ".join(parts)


def build_audit_reason(result: dict, factors: list[RankingFactor]) -> str:
    factor_bits = [f"{factor.factor_type}={factor.category_value}/{factor.direction}" for factor in factors]
    return f"result_id={result.get('result_id', 'unknown_result')}; factors: " + "; ".join(factor_bits)


def _build_caveats(result: dict, factors: list[RankingFactor]) -> tuple[str, ...]:
    caveats = []
    if result.get("conflicts"):
        caveats.append("conflicts_visible")
    if result.get("gaps"):
        caveats.append("gaps_visible")
    if str(result.get("candidate_status", "")).lower() in {"candidate", "provisional", "review_required"}:
        caveats.append("candidate_or_review_required")
    if any(factor.factor_type == "rights_risk_caution" and factor.category_value != "absent" for factor in factors):
        caveats.append("rights_risk_caution")
    return tuple(caveats)

