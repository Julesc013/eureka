from __future__ import annotations

import argparse
import json
import sys

CONTAINER_KINDS = {
    "zip_archive",
    "tar_archive",
    "gzip_archive",
    "seven_zip_archive",
    "ISO_image",
    "disk_image",
    "installer",
    "package_archive",
    "wheel",
    "sdist",
    "npm_tarball",
    "WARC",
    "WACZ",
    "PDF",
    "scanned_volume",
    "source_bundle",
    "repository_snapshot",
    "unknown",
}
HARD_FALSE = [
    "runtime_extraction_implemented",
    "extraction_executed",
    "files_opened",
    "archive_unpacked",
    "payload_executed",
    "installer_executed",
    "package_manager_invoked",
    "emulator_vm_launched",
    "OCR_performed",
    "transcription_performed",
    "live_source_called",
    "external_calls_performed",
    "URL_fetched",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "telemetry_exported",
]


def build(label: str, container_kind: str) -> dict:
    if container_kind not in CONTAINER_KINDS:
        raise ValueError(f"unsupported container kind: {container_kind}")
    safe_id = "".join(ch.lower() if ch.isalnum() else "-" for ch in label).strip("-") or "example"
    data = {
        "schema_version": "0.1.0",
        "extraction_request_id": f"dry_run_{safe_id}",
        "extraction_request_kind": "deep_extraction_request",
        "status": "dry_run_validated",
        "created_by_tool": "dry_run_deep_extraction_request.py",
        "request_scope": {"scope_kind": "stdout_only_dry_run", "contract_only": True, "runtime_allowed_now": False},
        "target_ref": {
            "target_kind": "synthetic_example",
            "target_label": label,
            "target_identifier": f"synthetic:dry-run:{safe_id}",
            "target_status": "synthetic_example",
            "target_payload_available": False,
            "target_path_public_safe": f"synthetic/dry-run/{safe_id}",
            "limitations": ["Dry-run request only; no payload is available."],
        },
        "extraction_policy_ref": "deep_extraction_policy_v0",
        "requested_tiers": ["tier_0_outer_metadata"],
        "container_hints": [
            {
                "container_kind": container_kind,
                "container_label": label,
                "container_status": "synthetic_example",
                "payload_included": False,
                "executable_risk_present": container_kind == "installer",
                "nested_container_present": False,
                "limitations": ["Hypothetical container hint only; no file is opened."],
            }
        ],
        "safety_requirements": {
            "sandbox_required_before_runtime": True,
            "network_disabled_required": True,
            "execution_disabled_required": True,
            "resource_limits_required": True,
            "operator_approval_required": True,
        },
        "privacy": {
            "public_safe_example": True,
            "absolute_paths_allowed": False,
            "private_paths_allowed": False,
            "credentials_allowed": False,
            "raw_private_query_data_allowed": False,
        },
        "rights_risk": {
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "payload_safety_known": False,
            "review_required_before_public_use": True,
        },
        "expected_outputs": ["extraction_result_summary_candidate_future"],
        "limitations": ["Stdout-only dry run. No files are written."],
        "no_runtime_guarantees": ["No extraction runtime, file opening, archive unpacking, OCR, transcription, URL fetch, or execution occurs."],
        "no_mutation_guarantees": ["No source/evidence/candidate/public/local/master mutation occurs."],
        "notes": ["Generated for contract planning only."],
    }
    for key in HARD_FALSE:
        data[key] = False
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit a hypothetical Deep Extraction Request v0 to stdout only.")
    parser.add_argument("--label", required=True)
    parser.add_argument("--container-kind", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        data = build(args.label, args.container_kind)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
