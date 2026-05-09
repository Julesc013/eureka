"""Shadow-only duplicate grouping helpers."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from runtime.extraction.guards import detect_truth_or_product_violations, stable_id
from runtime.search_quality.ranking_shadow import ranking_product_boundary, ranking_truth_boundary


def build_dedup_shadow(items: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    groups = group_duplicate_candidates_shadow_only(items, policy)
    record = {
        "schema_version": "dedup_shadow_result.v0",
        "dedup_shadow_id": stable_id("dedup.shadow", groups),
        "dedup_shadow_status": "local_shadow",
        "candidate_refs": [str(item.get("item_ref") or item.get("candidate_id")) for item in items],
        "duplicate_groups_proposed": groups,
        "duplicate_reasons": ["Exact identifier or title/version/platform fixture keys matched."],
        "conflicts_preserved": True,
        "merge_allowed_current": False,
        "delete_allowed_current": False,
        "automatic_dedup_allowed": False,
        "limitations": ["Dedup shadow proposes review groups only and never merges or deletes."],
        "truth_boundary": ranking_truth_boundary(),
        "product_boundary": ranking_product_boundary(),
    }
    return validate_dedup_shadow(record, policy)


def group_duplicate_candidates_shadow_only(items: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for item in items:
        key = _dedup_key(item)
        buckets[key].append(str(item.get("item_ref") or item.get("candidate_id") or key))
    return [
        {"duplicate_key": key, "candidate_refs": sorted(refs), "merge_allowed_current": False, "delete_allowed_current": False}
        for key, refs in sorted(buckets.items())
        if len(refs) > 1
    ]


def validate_dedup_shadow(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    violations = detect_truth_or_product_violations(record)
    if violations:
        raise ValueError("; ".join(violations))
    for key in ("merge_allowed_current", "delete_allowed_current", "automatic_dedup_allowed"):
        if record.get(key) is not False:
            raise ValueError(f"dedup shadow {key} must be false")
    return dict(record)


def _dedup_key(item: Mapping[str, Any]) -> str:
    identifiers = item.get("identifiers")
    if isinstance(identifiers, list) and identifiers:
        return "id:" + "|".join(sorted(str(value).casefold() for value in identifiers))
    return "fields:" + "|".join(
        [
            str(item.get("title") or item.get("name") or "").casefold(),
            str(item.get("version") or item.get("version_or_state") or "").casefold(),
            str(item.get("platform") or item.get("platform_or_context") or "").casefold(),
        ]
    )
