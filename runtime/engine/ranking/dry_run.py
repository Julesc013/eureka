from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from runtime.engine.ranking.errors import RankingDryRunError
from runtime.engine.ranking.explain import build_ranking_explanation_summary
from runtime.engine.ranking.factors import compute_explicit_factor_summary, factor_sort_key
from runtime.engine.ranking.models import RankingDryRunResultSet, RankingResultCandidate
from runtime.engine.ranking.policy import APPROVED_EXAMPLE_ROOTS, validate_public_safe_record, resolve_approved_root
from runtime.engine.ranking.report import build_report


def load_result_set(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RankingDryRunError(f"invalid JSON in {path.name}: {exc}") from exc


def discover_result_sets(root: Path) -> list[Path]:
    if not root.exists():
        return []
    if root.is_file():
        return [root] if root.name == "RESULT_SET.json" else []
    return sorted(root.rglob("RESULT_SET.json"))


def classify_result_set(record: dict[str, Any]) -> str:
    status = str(record.get("status", "unknown"))
    if status in {"synthetic_example", "public_safe_example", "fixture_backed"}:
        return status
    return "unknown"


def validate_result_set_shape(record: dict[str, Any]) -> list[str]:
    warnings = validate_public_safe_record(record)
    if not isinstance(record, dict):
        raise RankingDryRunError("result set must be a JSON object")
    result_set_id = record.get("result_set_id")
    if not isinstance(result_set_id, str) or not result_set_id:
        raise RankingDryRunError("result_set_id is required")
    results = record.get("results")
    if not isinstance(results, list) or not results:
        raise RankingDryRunError("results must be a non-empty list")
    seen = set()
    for index, result in enumerate(results):
        if not isinstance(result, dict):
            raise RankingDryRunError(f"result at index {index} must be an object")
        result_id = result.get("result_id")
        if not isinstance(result_id, str) or not result_id:
            raise RankingDryRunError(f"result at index {index} is missing result_id")
        if result_id in seen:
            raise RankingDryRunError(f"duplicate result_id: {result_id}")
        seen.add(result_id)
    current_order = record.get("current_order")
    if current_order is not None:
        if not isinstance(current_order, list) or any(not isinstance(item, str) for item in current_order):
            raise RankingDryRunError("current_order must be a list of result ids")
        missing = [result_id for result_id in current_order if result_id not in seen]
        if missing:
            raise RankingDryRunError(f"current_order references missing result ids: {', '.join(missing)}")
    return warnings


def rank_result_set_dry_run(record: dict[str, Any], strict: bool = False) -> RankingDryRunResultSet:
    warnings = validate_result_set_shape(record)
    result_set_id = str(record["result_set_id"])
    target_profile = record.get("target_profile") if isinstance(record.get("target_profile"), dict) else None
    results: list[dict[str, Any]] = list(record["results"])
    current_order = tuple(record.get("current_order") or [str(result["result_id"]) for result in results])
    current_rank = {result_id: index for index, result_id in enumerate(current_order)}
    summaries: list[RankingResultCandidate] = []
    explanations = []
    fallback_reasons = list(record.get("fallback_reasons") or [])
    policy = record.get("policy") if isinstance(record.get("policy"), dict) else {}
    if policy.get("force_current_order_fallback") is True:
        fallback_reasons.append("policy requested current-order fallback")

    sortable = []
    for result in results:
        factors = compute_explicit_factor_summary(result, target_profile)
        result_id = str(result["result_id"])
        rank = current_rank.get(result_id, len(current_rank))
        if result.get("requires_current_order_fallback") is True:
            fallback_reasons.append(f"{result_id} requires current-order fallback")
        summary = RankingResultCandidate(
            result_id=result_id,
            title=str(result.get("title") or result_id),
            current_rank=rank,
            factors=tuple(factors),
            policy_status="fallback" if fallback_reasons else "rankable",
            warnings=tuple(str(item) for item in result.get("warnings") or []),
        )
        summaries.append(summary)
        explanation = build_ranking_explanation_summary(result, factors)
        explanations.append(explanation)
        if not explanation.user_visible_reason:
            fallback_reasons.append(f"{result_id} missing explanation")
        sortable.append((factor_sort_key(factors, rank), result_id))

    fallback_used = bool(fallback_reasons)
    proposed = current_order if fallback_used else tuple(result_id for _, result_id in sorted(sortable))
    errors: tuple[str, ...] = ()
    if strict and fallback_used:
        errors = tuple(fallback_reasons)
    return RankingDryRunResultSet(
        result_set_id=result_set_id,
        current_order=current_order,
        proposed_dry_run_order=proposed,
        fallback_order=current_order,
        fallback_used=fallback_used,
        result_summaries=tuple(summaries),
        explanation_summaries=tuple(explanations),
        warnings=tuple(warnings + fallback_reasons),
        errors=errors,
    )


def run_public_search_ranking_dry_run(roots: list[Path] | None = None, strict: bool = False):
    roots = roots or [root for root in APPROVED_EXAMPLE_ROOTS if root.exists()]
    input_roots = [str(root.relative_to(Path(__file__).resolve().parents[3])) if root.is_absolute() else str(root) for root in roots]
    result_sets: list[RankingDryRunResultSet] = []
    errors: list[str] = []
    for root in roots:
        try:
            paths = discover_result_sets(root)
            if not paths:
                continue
            for path in paths:
                try:
                    record = load_result_set(path)
                    result_sets.append(rank_result_set_dry_run(record, strict=strict))
                except RankingDryRunError as exc:
                    if strict:
                        errors.append(f"{path.name}: {exc}")
                    else:
                        errors.append(f"{path.name}: {exc}")
        except RankingDryRunError as exc:
            errors.append(str(exc))
    if strict and errors:
        report = build_report(input_roots, result_sets, errors)
        raise RankingDryRunError("; ".join(errors) or "strict ranking dry-run failed")
    return build_report(input_roots, result_sets, errors)


def approved_root_from_text(path_text: str) -> Path:
    return resolve_approved_root(path_text)

