"""Shadow-only identity clustering helpers."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from runtime.extraction.guards import detect_truth_or_product_violations, stable_id
from runtime.search_quality.ranking_shadow import ranking_product_boundary, ranking_truth_boundary


def build_identity_merge_shadow(items: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    clusters: dict[str, list[str]] = defaultdict(list)
    for item in items:
        key = _identity_key(item)
        clusters[key].append(str(item.get("item_ref") or item.get("candidate_id") or key))
    proposed = [
        {"cluster_key": key, "subject_refs": sorted(refs), "merge_allowed_current": False}
        for key, refs in sorted(clusters.items())
        if len(refs) > 1
    ]
    conflicts = preserve_identity_conflicts(items, policy)
    record = {
        "schema_version": "identity_merge_shadow.v0",
        "identity_shadow_id": stable_id("identity.shadow", proposed or [item.get("item_ref") for item in items]),
        "identity_shadow_status": "local_shadow",
        "subject_refs": [str(item.get("item_ref") or item.get("candidate_id")) for item in items],
        "proposed_identity_cluster": proposed,
        "identity_evidence_summary": "Identity grouping is based on deterministic fixture title/version/platform keys.",
        "conflict_summary": conflicts,
        "duplicate_summary": {"duplicate_cluster_count": len(proposed)},
        "merge_allowed_current": False,
        "automatic_merge_allowed": False,
        "limitations": ["Identity shadow does not canonicalize or merge records."],
        "truth_boundary": {**ranking_truth_boundary(), "identity_cluster_is_public_truth": False},
        "product_boundary": ranking_product_boundary(),
    }
    return validate_identity_merge_shadow(record, policy)


def preserve_identity_conflicts(items: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    by_title: dict[str, set[str]] = defaultdict(set)
    for item in items:
        by_title[_norm(item.get("title") or item.get("name"))].add(_norm(item.get("version") or item.get("version_or_state")))
    conflicts = [
        {"title_key": key, "version_values": sorted(values), "conflict_preserved": True}
        for key, values in sorted(by_title.items())
        if key and len(values) > 1
    ]
    return {"conflict_count": len(conflicts), "conflicts": conflicts, "conflict_preservation_required": True}


def validate_identity_merge_shadow(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    violations = detect_truth_or_product_violations(record)
    if violations:
        raise ValueError("; ".join(violations))
    if record.get("merge_allowed_current") is not False or record.get("automatic_merge_allowed") is not False:
        raise ValueError("identity merge shadow must not allow merge")
    return dict(record)


def _identity_key(item: Mapping[str, Any]) -> str:
    return "|".join(
        [
            _norm(item.get("title") or item.get("name")),
            _norm(item.get("version") or item.get("version_or_state")),
            _norm(item.get("platform") or item.get("platform_or_context")),
        ]
    )


def _norm(value: Any) -> str:
    return str(value or "").strip().casefold()
