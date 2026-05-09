"""Compare action manifest builder."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from runtime.actions.action_policy import (
    action_product_boundary,
    action_truth_boundary,
    detect_action_boundary_violations,
    stable_id,
    subject_ref,
)


SCHEMA_VERSION = "compare_action_manifest.v0"


def build_compare_action_manifest(subjects: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    subject_list = _coerce_subjects(subjects)
    refs = [subject_ref(subject) for subject in subject_list]
    return {
        "schema_version": SCHEMA_VERSION,
        "compare_action_manifest_id": stable_id("compare_action_manifest", refs),
        "comparison_subject_refs": refs,
        "comparison_basis": "explicit_subject_refs",
        "comparison_fields": ["title_or_label", "source_refs", "evidence_refs", "limitations", "policy_posture"],
        "comparison_limitations": ["Comparison preserves conflicts and does not merge identity."],
        "conflicts_preserved": True,
        "merge_allowed_current": False,
        "truth_boundary": action_truth_boundary(),
        "product_boundary": action_product_boundary(),
    }


def validate_compare_action_manifest(manifest: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "compare_action_manifest_id",
        "comparison_subject_refs",
        "comparison_basis",
        "comparison_fields",
        "comparison_limitations",
        "conflicts_preserved",
        "merge_allowed_current",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required):
        if field not in manifest:
            errors.append(f"missing compare manifest field: {field}")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if manifest.get("conflicts_preserved") is not True:
        errors.append("conflicts_preserved must be true")
    if manifest.get("merge_allowed_current") is not False:
        errors.append("merge_allowed_current must be false")
    errors.extend(detect_action_boundary_violations(manifest))
    return sorted(dict.fromkeys(errors))


def _coerce_subjects(subjects: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None) -> list[Mapping[str, Any]]:
    if subjects is None:
        return [{}, {}]
    if isinstance(subjects, Mapping):
        return [subjects]
    return [item for item in subjects if isinstance(item, Mapping)] or [{}, {}]
