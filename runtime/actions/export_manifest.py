"""Export manifest builder for J0 descriptive exports."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from runtime.actions.action_policy import (
    action_product_boundary,
    action_truth_boundary,
    detect_action_boundary_violations,
    stable_id,
    subject_ref,
    subject_type,
)


SCHEMA_VERSION = "export_manifest.v0"


def build_export_manifest(subjects: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    subject_list = _coerce_subjects(subjects)
    refs = [subject_ref(subject) for subject in subject_list]
    return {
        "schema_version": SCHEMA_VERSION,
        "export_manifest_id": stable_id("export_manifest", refs),
        "export_status": "manifest_only",
        "export_subject_type": "mixed" if len({subject_type(subject) for subject in subject_list}) > 1 else subject_type(subject_list[0]),
        "export_subject_refs": refs,
        "exported_record_summaries": [
            {
                "record_ref": subject_ref(subject),
                "record_type": subject_type(subject),
                "exported_record_is_truth": False,
                "accepted": False,
            }
            for subject in subject_list
        ],
        "included_refs": refs,
        "excluded_refs": [],
        "export_format": "json_manifest_preview",
        "fixity_summary": {
            "fixity_available": False,
            "fixity_note": "J0 export manifest records refs; it does not create a signed or accepted pack.",
        },
        "limitations": ["Export manifest is not pack import, submission, publication, or public truth."],
        "review_required": True,
        "truth_boundary": action_truth_boundary(),
        "product_boundary": action_product_boundary(),
    }


def validate_export_manifest(manifest: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "export_manifest_id",
        "export_status",
        "export_subject_type",
        "export_subject_refs",
        "exported_record_summaries",
        "included_refs",
        "excluded_refs",
        "export_format",
        "fixity_summary",
        "limitations",
        "review_required",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required):
        if field not in manifest:
            errors.append(f"missing export manifest field: {field}")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if manifest.get("review_required") is not True:
        errors.append("review_required must be true")
    errors.extend(detect_action_boundary_violations(manifest))
    return sorted(dict.fromkeys(errors))


def _coerce_subjects(subjects: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None) -> list[Mapping[str, Any]]:
    if subjects is None:
        return [{}]
    if isinstance(subjects, Mapping):
        return [subjects]
    return [item for item in subjects if isinstance(item, Mapping)] or [{}]
