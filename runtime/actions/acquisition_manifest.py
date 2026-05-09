"""Descriptive acquisition manifest builder."""

from __future__ import annotations

from typing import Any, Mapping

from runtime.actions.action_policy import (
    action_product_boundary,
    action_truth_boundary,
    detect_action_boundary_violations,
    stable_id,
    subject_ref,
)


SCHEMA_VERSION = "acquisition_manifest.v0"


def build_acquisition_manifest(subject: Mapping[str, Any] | None, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    subject = subject or {}
    source_refs = _list_field(subject, "source_refs") or _list_field(subject, "sources_checked")
    locator = subject.get("source_locator") or subject.get("target_path") or subject.get("subject_ref") or subject_ref(subject)
    return {
        "schema_version": SCHEMA_VERSION,
        "acquisition_manifest_id": stable_id("acquisition_manifest", {"subject": subject_ref(subject), "locator": locator}),
        "acquisition_status": "descriptive_only",
        "subject_ref": subject_ref(subject),
        "source_refs": source_refs,
        "access_path_candidates": [
            {
                "access_path_ref": str(locator),
                "access_path_status": "described_not_fetched",
                "download_allowed_current": False,
                "mirror_allowed_current": False,
                "source_fetch_allowed_current": False,
            }
        ],
        "source_locator_summaries": [
            {
                "source_locator": str(locator),
                "locator_role": "candidate_access_path",
                "executed_or_fetched": False,
            }
        ],
        "hash_or_fixity_refs": _list_field(subject, "hash_or_fixity_refs") or _list_field(subject, "fixity_refs"),
        "rights_posture": "unknown_not_cleared",
        "risk_posture": "unknown_not_scanned",
        "compatibility_posture": "unknown_not_verified",
        "required_reviews": ["rights_review_before_future_access", "risk_review_before_future_execution"],
        "blocked_actions": ["download", "mirror", "install", "execute", "emulate"],
        "allowed_current_actions": ["view", "inspect", "cite", "export", "blocked_action"],
        "forbidden_current_actions": ["download", "mirror", "install", "execute", "emulate", "source_fetch"],
        "limitations": [
            "Acquisition manifest describes possible access paths only.",
            "No source was fetched, downloaded, mirrored, installed, executed, or emulated.",
        ],
        "truth_boundary": action_truth_boundary(),
        "product_boundary": action_product_boundary(),
        "notes": ["Descriptive manifest only; future acquisition needs separate policy."],
    }


def validate_acquisition_manifest(manifest: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "acquisition_manifest_id",
        "acquisition_status",
        "subject_ref",
        "source_refs",
        "access_path_candidates",
        "source_locator_summaries",
        "hash_or_fixity_refs",
        "rights_posture",
        "risk_posture",
        "compatibility_posture",
        "required_reviews",
        "blocked_actions",
        "allowed_current_actions",
        "forbidden_current_actions",
        "limitations",
        "truth_boundary",
        "product_boundary",
        "notes",
    }
    for field in sorted(required):
        if field not in manifest:
            errors.append(f"missing acquisition manifest field: {field}")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    for action in ("download", "mirror", "install", "execute", "emulate"):
        if action not in manifest.get("blocked_actions", []):
            errors.append(f"blocked_actions must include {action}")
    errors.extend(detect_action_boundary_violations(manifest))
    return sorted(dict.fromkeys(errors))


def _list_field(subject: Mapping[str, Any], key: str) -> list[str]:
    value = subject.get(key)
    if isinstance(value, list):
        return [str(item) for item in value]
    if value:
        return [str(value)]
    return []
