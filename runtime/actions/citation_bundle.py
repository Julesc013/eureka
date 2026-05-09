"""Citation bundle builder for governed local records."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from runtime.actions.action_policy import (
    action_product_boundary,
    action_truth_boundary,
    detect_action_boundary_violations,
    stable_id,
    subject_ref,
    subject_type,
)


SCHEMA_VERSION = "citation_bundle.v0"


def build_citation_bundle(subjects: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    subject_list = _coerce_subjects(subjects)
    refs = [subject_ref(subject) for subject in subject_list]
    return {
        "schema_version": SCHEMA_VERSION,
        "citation_bundle_id": stable_id("citation_bundle", refs),
        "citation_status": "descriptive_only",
        "subject_refs": refs,
        "source_refs": _collect_refs(subject_list, "source_refs"),
        "evidence_refs": _collect_refs(subject_list, "evidence_refs"),
        "pack_refs": _collect_refs(subject_list, "pack_refs"),
        "citation_entries": [
            {
                "citation_entry_id": stable_id("citation_entry", {"subject": subject_ref(subject)}),
                "subject_ref": subject_ref(subject),
                "subject_type": subject_type(subject),
                "label": str(subject.get("action_label") or subject.get("title") or subject.get("name") or subject_ref(subject)),
                "source_posture": "governed_ref_or_unknown",
                "evidence_posture": "candidate_or_reviewed_ref_only",
                "limitations": ["Citation preserves posture and does not accept truth."],
            }
            for subject in subject_list
        ],
        "citation_formats": ["plain_text", "json"],
        "generated_at_note": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "limitations": ["Citation bundle is descriptive and does not clear rights or accept evidence."],
        "no_claims": [
            "no rights clearance",
            "no malware safety",
            "no verified installability",
            "no accepted public truth",
        ],
        "truth_boundary": action_truth_boundary(),
        "product_boundary": action_product_boundary(),
    }


def validate_citation_bundle(bundle: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "citation_bundle_id",
        "citation_status",
        "subject_refs",
        "source_refs",
        "evidence_refs",
        "pack_refs",
        "citation_entries",
        "citation_formats",
        "generated_at_note",
        "limitations",
        "no_claims",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required):
        if field not in bundle:
            errors.append(f"missing citation bundle field: {field}")
    if bundle.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if not bundle.get("limitations"):
        errors.append("citation bundle must preserve limitations")
    errors.extend(detect_action_boundary_violations(bundle))
    return sorted(dict.fromkeys(errors))


def _coerce_subjects(subjects: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None) -> list[Mapping[str, Any]]:
    if subjects is None:
        return [{}]
    if isinstance(subjects, Mapping):
        return [subjects]
    return [item for item in subjects if isinstance(item, Mapping)] or [{}]


def _collect_refs(subjects: list[Mapping[str, Any]], key: str) -> list[str]:
    refs: list[str] = []
    for subject in subjects:
        value = subject.get(key)
        if isinstance(value, list):
            refs.extend(str(item) for item in value)
        elif value:
            refs.append(str(value))
    return sorted(dict.fromkeys(refs))
