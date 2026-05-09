"""Preservation manifest builder for metadata-only J0 preservation posture."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from runtime.actions.action_policy import (
    action_product_boundary,
    action_truth_boundary,
    detect_action_boundary_violations,
    stable_id,
    subject_ref,
)


SCHEMA_VERSION = "preservation_manifest.v0"


def build_preservation_manifest(subjects: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    subject_list = _coerce_subjects(subjects)
    refs = [subject_ref(subject) for subject in subject_list]
    return {
        "schema_version": SCHEMA_VERSION,
        "preservation_manifest_id": stable_id("preservation_manifest", refs),
        "preservation_status": "metadata_manifest_only",
        "subject_refs": refs,
        "source_refs": _collect_refs(subject_list, "source_refs"),
        "evidence_refs": _collect_refs(subject_list, "evidence_refs"),
        "fixity_refs": _collect_refs(subject_list, "fixity_refs"),
        "preservation_actions_current": ["describe_metadata", "export_manifest_preview", "cite"],
        "preservation_actions_future": ["mirror_future", "capture_future", "storage_or_cas_future"],
        "blocked_actions": ["mirror", "download", "capture", "install", "execute", "emulate"],
        "storage_or_cas_refs_future": [],
        "limitations": ["No files are mirrored, captured, downloaded, or stored by J0 preservation manifests."],
        "truth_boundary": action_truth_boundary(),
        "product_boundary": action_product_boundary(),
    }


def validate_preservation_manifest(manifest: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "preservation_manifest_id",
        "preservation_status",
        "subject_refs",
        "source_refs",
        "evidence_refs",
        "fixity_refs",
        "preservation_actions_current",
        "preservation_actions_future",
        "blocked_actions",
        "storage_or_cas_refs_future",
        "limitations",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required):
        if field not in manifest:
            errors.append(f"missing preservation manifest field: {field}")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    for action in ("mirror", "download"):
        if action not in manifest.get("blocked_actions", []):
            errors.append(f"blocked_actions must include {action}")
    errors.extend(detect_action_boundary_violations(manifest))
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
