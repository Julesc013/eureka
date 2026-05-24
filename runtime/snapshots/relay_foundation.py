from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence


CREATED_AT = "2026-05-25T00:00:00Z"
SNAPSHOT_VERSION = "snapshot_relay_00.v0"

UNSAFE_FALSE_FIELDS = (
    "private_local_state_included",
    "operator_tokens_included",
    "raw_live_source_response_committed",
    "live_source_call_performed",
    "source_probe_executed",
    "operator_instance_mutated",
    "master_index_mutated",
    "committed_data_public_index_mutated",
    "download_performed",
    "upload_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)


def stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def stable_id(prefix: str, *parts: object) -> str:
    return f"{prefix}_{stable_hash(parts)[:16]}"


def default_snapshot_policy() -> dict[str, Any]:
    return {
        "schema_version": "snapshot_relay_policy_bundle.v0",
        "snapshots_are_read_only_data_products": True,
        "snapshots_may_include_reviewed_records": True,
        "snapshots_may_include_source_summaries": True,
        "snapshots_may_include_evidence_summaries": True,
        "snapshots_may_include_absence_reports": True,
        "snapshots_may_include_known_needs": True,
        "snapshots_must_not_include_private_local_state": True,
        "snapshots_must_not_include_operator_tokens": True,
        "snapshots_must_not_include_raw_live_source_responses": True,
        "snapshots_must_not_include_unreviewed_truth": True,
        "snapshot_integrity_manifest_required": True,
        "snapshot_hashes_required": True,
        "private_signing_keys_forbidden": True,
        "relay_read_only": True,
        "relay_mutation_enabled": False,
        "relay_live_source_calls_enabled": False,
        "relay_downloads_enabled": False,
        "relay_extraction_enabled": False,
        "public_launch_claim_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def sample_reviewed_records() -> list[dict[str, Any]]:
    return [
        {
            "record_id": "reviewed-sampleproject-001",
            "object_id": "sampleproject",
            "title": "SampleProject 1.0 reviewed local record",
            "domain_id": "legacy_software",
            "result_kind": "reviewed_object_record",
            "reviewed_status": "reviewed_local",
            "source_summary_refs": ["source-summary-sampleproject-001"],
            "evidence_summary_refs": ["evidence-summary-sampleproject-001"],
            "limitations": ["fixture reviewed record for snapshot relay validation"],
            "action_posture": "view_cite_export_only",
            "public_safe_fields": ["record_id", "object_id", "title", "domain_id", "result_kind"],
            "private_notes": "removed by snapshot projection",
        }
    ]


def sample_source_summaries() -> list[dict[str, Any]]:
    return [
        {
            "summary_id": "source-summary-sampleproject-001",
            "source_family": "manual_source_pack",
            "title": "Manual source pack fixture summary",
            "source_locator_summary": "fixture://manual_source_pack/sampleproject",
            "raw_response_included": False,
        }
    ]


def sample_evidence_summaries() -> list[dict[str, Any]]:
    return [
        {
            "summary_id": "evidence-summary-sampleproject-001",
            "evidence_kind": "operator_review_summary",
            "title": "Reviewed local evidence summary",
            "accepted_evidence": True,
            "raw_evidence_blob_included": False,
        }
    ]


def sample_absence_summaries() -> list[dict[str, Any]]:
    return [
        {
            "summary_id": "absence-summary-sampleproject-001",
            "need_id": "need-sampleproject-source-expansion",
            "title": "Known need for broader source coverage",
            "absence_status": "known_gap",
        }
    ]


def sample_need_summaries() -> list[dict[str, Any]]:
    return [
        {
            "summary_id": "need-summary-sampleproject-001",
            "need_id": "need-sampleproject-source-expansion",
            "title": "Expand metadata sources for SampleProject",
            "public_safe": True,
        }
    ]


def build_snapshot_plan(reviewed_records: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    policy_payload = dict(policy or default_snapshot_policy())
    return {
        "schema_version": "snapshot_build_plan.v0",
        "record_type": "snapshot_build_plan",
        "snapshot_id": stable_id("snapshot", [record.get("record_id") for record in reviewed_records]),
        "created_at": CREATED_AT,
        "source_context": "fixture_reviewed_records",
        "reviewed_only": True,
        "public_safe": True,
        "reviewed_record_count": len(reviewed_records),
        "include_source_summaries": policy_payload.get("snapshots_may_include_source_summaries", True),
        "include_evidence_summaries": policy_payload.get("snapshots_may_include_evidence_summaries", True),
        "include_absence_reports": policy_payload.get("snapshots_may_include_absence_reports", True),
        "include_known_needs": policy_payload.get("snapshots_may_include_known_needs", True),
        "target_projection_profiles": [
            "public_api_read_only",
            "public_web_read_only",
            "files_read_only",
            "text_read_only",
            "lite_client_read_only",
            "native_desktop_read_only",
        ],
        "limitations": ["fixture-reviewed records only", "read-only snapshot product"],
        "non_claims": snapshot_non_claims(),
    }


def project_reviewed_record_to_snapshot(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    del policy
    public_fields = {
        "record_id": record.get("record_id"),
        "object_id": record.get("object_id"),
        "title": record.get("title"),
        "domain_id": record.get("domain_id"),
        "result_kind": record.get("result_kind", "reviewed_object_record"),
        "reviewed_status": record.get("reviewed_status", "reviewed_local"),
        "source_summary_refs": list(record.get("source_summary_refs", [])),
        "evidence_summary_refs": list(record.get("evidence_summary_refs", [])),
        "limitations": list(record.get("limitations", [])),
        "action_posture": record.get("action_posture", "view_cite_export_only"),
        "public_safe_fields": list(record.get("public_safe_fields", [])),
    }
    return {
        "schema_version": "snapshot_record.v0",
        "record_type": "snapshot_record",
        "snapshot_id": stable_id("snapshot_record_snapshot", public_fields["record_id"]),
        "created_at": CREATED_AT,
        "source_context": "fixture_reviewed_record",
        "reviewed_only": True,
        "public_safe": True,
        **public_fields,
        "private_fields_removed": True,
        "non_claims": snapshot_non_claims(),
    }


def build_snapshot_record_set(records: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    snapshot_records = [project_reviewed_record_to_snapshot(record, policy) for record in records]
    return {
        "schema_version": "snapshot_record_set.v0",
        "record_type": "snapshot_record_set",
        "snapshot_id": stable_id("snapshot_record_set", [record["record_id"] for record in snapshot_records]),
        "created_at": CREATED_AT,
        "source_context": "fixture_reviewed_records",
        "reviewed_only": True,
        "public_safe": True,
        "records": snapshot_records,
        "record_count": len(snapshot_records),
        "limitations": ["record set contains public-safe reviewed fixture records"],
        "non_claims": snapshot_non_claims(),
    }


def build_snapshot_manifest(record_set: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    records = list(record_set.get("records", []))
    snapshot_id = str(record_set.get("snapshot_id") or stable_id("snapshot", records))
    return {
        "schema_version": "snapshot_manifest.v0",
        "record_type": "snapshot_manifest",
        "snapshot_id": snapshot_id,
        "snapshot_version": SNAPSHOT_VERSION,
        "created_at": CREATED_AT,
        "source_context": "fixture_reviewed_records",
        "reviewed_only": True,
        "public_safe": True,
        "record_count": len(records),
        "record_refs": [record["record_id"] for record in records],
        "source_summary_count": len(sample_source_summaries()),
        "evidence_summary_count": len(sample_evidence_summaries()),
        "absence_summary_count": len(sample_absence_summaries()),
        "known_need_count": len(sample_need_summaries()),
        "record_classes": [
            "reviewed_object_record",
            "reviewed_source_summary",
            "reviewed_evidence_summary",
            "known_absence_summary",
            "known_need_summary",
            "limitation_summary",
            "action_posture_summary",
        ],
        "limitations": ["manifest is for read-only fixture snapshot relay validation"],
        "non_claims": snapshot_non_claims(),
    }


def build_integrity_manifest(snapshot_files_or_records: Mapping[str, Any] | Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    del policy
    if isinstance(snapshot_files_or_records, Mapping):
        entries = [
            {"path": key, "sha256": stable_hash(value)}
            for key, value in sorted(snapshot_files_or_records.items())
        ]
        snapshot_id = stable_id("snapshot_integrity", snapshot_files_or_records)
    else:
        entries = [
            {"record_id": str(record.get("record_id", index)), "sha256": stable_hash(record)}
            for index, record in enumerate(snapshot_files_or_records)
        ]
        snapshot_id = stable_id("snapshot_integrity", entries)
    return {
        "schema_version": "snapshot_integrity_manifest.v0",
        "record_type": "snapshot_integrity_manifest",
        "snapshot_id": snapshot_id,
        "created_at": CREATED_AT,
        "source_context": "fixture_reviewed_records",
        "reviewed_only": True,
        "public_safe": True,
        "hash_algorithm": "sha256",
        "entries": entries,
        "entry_count": len(entries),
        "deterministic": True,
        "private_signing_key_included": False,
        "limitations": ["hashes prove local packet integrity only, not source authenticity"],
        "non_claims": snapshot_non_claims(),
    }


def build_snapshot_envelope(
    manifest: Mapping[str, Any],
    integrity_manifest: Mapping[str, Any],
    capability_profile: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    del policy
    snapshot_id = str(manifest.get("snapshot_id"))
    return {
        "schema_version": "snapshot_envelope.v0",
        "record_type": "snapshot_envelope",
        "snapshot_id": snapshot_id,
        "snapshot_version": manifest.get("snapshot_version", SNAPSHOT_VERSION),
        "created_at": CREATED_AT,
        "source_context": "fixture_reviewed_records",
        "reviewed_only": True,
        "public_safe": True,
        "build_plan_ref": stable_id("snapshot_build_plan_ref", snapshot_id),
        "manifest_ref": manifest.get("snapshot_id"),
        "integrity_manifest_ref": integrity_manifest.get("snapshot_id"),
        "capability_profile_ref": capability_profile.get("profile_id"),
        "record_count": manifest.get("record_count", 0),
        "source_summary_count": manifest.get("source_summary_count", 0),
        "evidence_summary_count": manifest.get("evidence_summary_count", 0),
        "absence_summary_count": manifest.get("absence_summary_count", 0),
        "known_need_count": manifest.get("known_need_count", 0),
        "production_claim": False,
        "public_launch_claim": False,
        "limitations": ["read-only reviewed-record snapshot envelope"],
        "non_claims": snapshot_non_claims(),
    }


def validate_snapshot_envelope(envelope: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    del policy
    errors: list[str] = []
    required = (
        "schema_version",
        "snapshot_id",
        "snapshot_version",
        "build_plan_ref",
        "manifest_ref",
        "integrity_manifest_ref",
        "capability_profile_ref",
        "record_count",
        "public_safe",
        "reviewed_only",
        "production_claim",
        "public_launch_claim",
    )
    for field in required:
        if field not in envelope:
            errors.append(f"missing {field}")
    if envelope.get("schema_version") != "snapshot_envelope.v0":
        errors.append("schema_version must be snapshot_envelope.v0")
    if envelope.get("public_safe") is not True:
        errors.append("public_safe must be true")
    if envelope.get("reviewed_only") is not True:
        errors.append("reviewed_only must be true")
    if envelope.get("production_claim") is not False:
        errors.append("production_claim must be false")
    if envelope.get("public_launch_claim") is not False:
        errors.append("public_launch_claim must be false")
    return {
        "schema_version": "snapshot_validation_report.v0",
        "record_type": "snapshot_validation_report",
        "snapshot_id": envelope.get("snapshot_id"),
        "created_at": CREATED_AT,
        "source_context": "fixture_reviewed_records",
        "reviewed_only": envelope.get("reviewed_only") is True,
        "public_safe": envelope.get("public_safe") is True,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "limitations": ["schema and boundary validation only"],
        "non_claims": snapshot_non_claims(),
    }


def build_snapshot_boundary_report(snapshot_result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    del policy
    report: dict[str, Any] = {
        "schema_version": "snapshot_boundary_report.v0",
        "record_type": "snapshot_boundary_report",
        "snapshot_id": snapshot_result.get("snapshot_id", stable_id("snapshot_boundary", snapshot_result)),
        "created_at": CREATED_AT,
        "source_context": "fixture_reviewed_records",
        "reviewed_only": True,
        "public_safe": True,
        "limitations": ["boundary report for read-only snapshot relay foundation"],
        "non_claims": snapshot_non_claims(),
    }
    for field in UNSAFE_FALSE_FIELDS:
        report[field] = False
    return report


def build_snapshot_from_examples(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    records = sample_reviewed_records()
    plan = build_snapshot_plan(records, policy)
    record_set = build_snapshot_record_set(records, policy)
    manifest = build_snapshot_manifest(record_set, policy)
    integrity = build_integrity_manifest(
        {
            "manifest": manifest,
            "records": record_set,
            "source_summaries": sample_source_summaries(),
            "evidence_summaries": sample_evidence_summaries(),
            "absence_summaries": sample_absence_summaries(),
            "need_summaries": sample_need_summaries(),
        },
        policy,
    )
    from runtime.capabilities import build_capability_profile

    capability = build_capability_profile("public_api_read_only", policy)
    envelope = build_snapshot_envelope(manifest, integrity, capability, policy)
    validation = validate_snapshot_envelope(envelope, policy)
    boundary = build_snapshot_boundary_report(envelope, policy)
    return {
        "schema_version": "snapshot_build_result.v0",
        "record_type": "snapshot_build_result",
        "snapshot_id": envelope["snapshot_id"],
        "created_at": CREATED_AT,
        "source_context": "fixture_reviewed_records",
        "reviewed_only": True,
        "public_safe": True,
        "plan": plan,
        "record_set": record_set,
        "manifest": manifest,
        "integrity_manifest": integrity,
        "capability_profile": capability,
        "envelope": envelope,
        "validation_report": validation,
        "boundary_report": boundary,
        "source_summaries": sample_source_summaries(),
        "evidence_summaries": sample_evidence_summaries(),
        "absence_summaries": sample_absence_summaries(),
        "need_summaries": sample_need_summaries(),
        "limitations": ["fixture snapshot build result"],
        "non_claims": snapshot_non_claims(),
    }


def snapshot_non_claims() -> list[str]:
    return [
        "not_public_truth",
        "not_production_deployment",
        "not_public_launch",
        "not_live_source_action",
        "not_store_mutation",
        "not_download_or_extraction",
    ]
