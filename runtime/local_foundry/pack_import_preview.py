"""Preview-only pack import projection.

Import previews describe proposed records and blockers. They do not import,
submit, publish, accept, or mutate any store or index.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from runtime.local_foundry.pack_fixity import pack_product_boundary


SCHEMA_VERSION = "pack_import_preview.v0"


def import_preview_truth_boundary() -> dict[str, bool]:
    return {
        "import_preview_imports_records": False,
        "quarantined_pack_is_accepted": False,
        "quarantined_pack_is_imported": False,
        "quarantined_pack_is_submitted": False,
        "accepted_evidence": False,
        "accepted_candidate": False,
        "accepted_public_record": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
    }


def build_pack_import_preview(
    pack: Mapping[str, Any],
    quarantine_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    pack_type = str(quarantine_result.get("input_pack_type") or pack.get("export_pack_type") or "unknown_pack")
    proposed_records = _proposed_records(pack, quarantine_result)
    blockers = list(quarantine_result.get("blocker_summary", {}).get("blockers", []))
    status = "policy_blocked" if quarantine_result.get("quarantine_status", "").startswith("blocked") or blockers else "preview_only"
    preview = {
        "schema_version": SCHEMA_VERSION,
        "import_preview_id": f"pack_import_preview.{quarantine_result.get('quarantine_result_id', 'unknown')}.v0",
        "input_pack_ref": quarantine_result.get("input_pack_ref") or pack.get("pack_export_id", ""),
        "import_preview_status": status,
        "proposed_records": proposed_records,
        "proposed_source_records": [record for record in proposed_records if record.get("candidate_record_type") == "source_record"],
        "proposed_evidence_records": [record for record in proposed_records if record.get("candidate_record_type") == "evidence_record"],
        "proposed_candidate_records": [record for record in proposed_records if record.get("candidate_record_type") == "candidate_record"],
        "proposed_review_records": [record for record in proposed_records if record.get("candidate_record_type") == "review_record"],
        "proposed_public_records_future": [],
        "blockers": blockers,
        "required_reviews": [
            "schema_review",
            "fixity_review",
            "signature_envelope_review",
            "provenance_review",
            "rights_risk_review",
        ],
        "forbidden_effects": [
            "pack_import",
            "pack_submission",
            "pack_publication",
            "pack_acceptance",
            "accepted_evidence",
            "accepted_candidate",
            "public_index_mutation",
            "master_index_mutation",
        ],
        "truth_boundary": import_preview_truth_boundary(),
        "product_boundary": pack_product_boundary(),
        "notes": [
            f"{pack_type} import preview is proposal-only.",
            "No records are written to source cache, evidence ledger, candidate store, review queue, public index, or master index.",
        ],
    }
    return preview


def validate_pack_import_preview(preview: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "import_preview_id",
        "input_pack_ref",
        "import_preview_status",
        "proposed_records",
        "proposed_source_records",
        "proposed_evidence_records",
        "proposed_candidate_records",
        "proposed_review_records",
        "proposed_public_records_future",
        "blockers",
        "required_reviews",
        "forbidden_effects",
        "truth_boundary",
        "product_boundary",
        "notes",
    }
    for field in sorted(required):
        if field not in preview:
            errors.append(f"missing import preview field: {field}")
    if preview.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if preview.get("proposed_public_records_future") not in ([], None):
        errors.append("proposed_public_records_future must be empty in current runtime")
    truth = preview.get("truth_boundary", {})
    if not isinstance(truth, Mapping):
        errors.append("truth_boundary must be an object")
    else:
        for key, expected in import_preview_truth_boundary().items():
            if truth.get(key) is not expected:
                errors.append(f"truth_boundary.{key} must be {str(expected).lower()}")
    return sorted(dict.fromkeys(errors))


def summarize_pack_import_preview(preview: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": "pack_import_preview_summary.v0",
        "import_preview_id": preview.get("import_preview_id"),
        "import_preview_status": preview.get("import_preview_status"),
        "proposed_record_count": len(preview.get("proposed_records", [])),
        "source_record_count": len(preview.get("proposed_source_records", [])),
        "evidence_record_count": len(preview.get("proposed_evidence_records", [])),
        "candidate_record_count": len(preview.get("proposed_candidate_records", [])),
        "review_record_count": len(preview.get("proposed_review_records", [])),
        "blocker_count": len(preview.get("blockers", [])),
        "imports_records": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def _proposed_records(pack: Mapping[str, Any], quarantine_result: Mapping[str, Any]) -> list[dict[str, Any]]:
    summaries = quarantine_result.get("provenance_summary", {}).get("proposed_record_summary", [])
    if isinstance(summaries, list) and summaries:
        return [deepcopy(dict(record)) for record in summaries if isinstance(record, Mapping)]
    exported = pack.get("exported_pack", {})
    draft = exported.get("source_pack_draft", {}) if isinstance(exported, Mapping) else {}
    records = draft.get("pack_contents", {}).get("records", []) if isinstance(draft, Mapping) else []
    proposed: list[dict[str, Any]] = []
    for record in records if isinstance(records, list) else []:
        if not isinstance(record, Mapping):
            continue
        input_type = str(record.get("input_type", "unknown"))
        proposed.append(
            {
                "record_ref": record.get("record_ref", ""),
                "candidate_record_type": _candidate_record_type(input_type),
                "record_label": record.get("record_label", ""),
                "proposal_only": True,
                "accepted": False,
                "imported": False,
            }
        )
    return proposed


def _candidate_record_type(input_type: str) -> str:
    if "source" in input_type:
        return "source_record"
    if "evidence" in input_type:
        return "evidence_record"
    if "candidate" in input_type:
        return "candidate_record"
    if "review" in input_type:
        return "review_record"
    return "proposal_record"
