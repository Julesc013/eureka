"""Local reviewed-artifact gate seed helpers.

This module prepares manual evidence-collection seed artifacts from the local
search index. It does not verify artifacts, fetch files, download binaries, or
promote fixture/source-lead evidence into truth.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.local.search_index import load_index, validate_index


TASK_ID = "REVIEWED-ARTIFACT-GATE-SEED-00"
MANUAL_BATCH_TASK_ID = "MANUAL-ARTIFACT-EVIDENCE-BATCH-01"
SOURCE_COLLECTION_TASK_ID = "ARTIFACT-EVIDENCE-SOURCE-COLLECTION-00"
ARTIFACT_GATE_SCHEMA_VERSION = "eureka.reviewed_artifact_gate_seed.v0"
MANUAL_BATCH_SCHEMA_VERSION = "eureka.manual_artifact_evidence_batch.v0"
SOURCE_COLLECTION_SCHEMA_VERSION = "eureka.artifact_evidence_source_collection.v0"
SOURCE_OBSERVATION_SCHEMA_VERSION = "eureka.artifact_source_observation.v0"
CANDIDATE_SCHEMA_VERSION = "eureka.artifact_gate_candidate.v0"
EVIDENCE_PACKET_SCHEMA_VERSION = "eureka.artifact_gate_evidence_packet.v0"
REVIEWED_ARTIFACT_RECORD_SCHEMA_VERSION = "eureka.reviewed_artifact_gate_record.v0"
DEFAULT_GATE_TARGET = 25
DEFAULT_GATE_DIR = ".eureka/artifact-gate/public-alpha-seed"
DEFAULT_MANUAL_BATCH_DIR = ".eureka/artifact-gate/manual-batch-01"
DEFAULT_SOURCE_COLLECTION_DIR = ".eureka/artifact-gate/source-collection-01"
DEFAULT_CANDIDATES_FILE = "candidates.jsonl"
DEFAULT_EVIDENCE_TEMPLATE_FILE = "evidence_template.jsonl"
DEFAULT_EVIDENCE_PACKETS_FILE = "evidence_packets.jsonl"
DEFAULT_REVIEWED_ARTIFACT_RECORDS_FILE = "reviewed_artifact_records.jsonl"
DEFAULT_GATE_REPORT_FILE = "artifact_gate_report.json"
DEFAULT_GATE_REPORT_MD = "ARTIFACT_GATE_REPORT.md"
MANUAL_BATCH_MANIFEST_FILE = "batch_manifest.json"
MANUAL_BATCH_CANDIDATE_PLAN_FILE = "candidate_plan.jsonl"
MANUAL_BATCH_TEMPLATE_FILE = "manual_evidence_template.jsonl"
MANUAL_BATCH_EVIDENCE_FILE = "manual_evidence_packets.jsonl"
MANUAL_BATCH_VALIDATION_REPORT_FILE = "evidence_validation_report.json"
MANUAL_BATCH_REPORT_MD = "MANUAL_BATCH_REPORT.md"
SOURCE_COLLECTION_MANIFEST_FILE = "collection_manifest.json"
SOURCE_COLLECTION_CANDIDATE_PLAN_FILE = "source_candidate_plan.jsonl"
SOURCE_COLLECTION_TEMPLATE_FILE = "source_observation_template.jsonl"
SOURCE_COLLECTION_URL_LIST_TEMPLATE_FILE = "source_url_list_template.jsonl"
SOURCE_COLLECTION_OBSERVATIONS_FILE = "source_observations.jsonl"
SOURCE_COLLECTION_VALIDATION_REPORT_FILE = "source_validation_report.json"
SOURCE_COLLECTION_EVIDENCE_FILE = "manual_evidence_packets.jsonl"
SOURCE_COLLECTION_REPORT_FILE = "source_collection_report.json"
SOURCE_COLLECTION_REPORT_MD = "SOURCE_COLLECTION_REPORT.md"
_INSUFFICIENT_VERIFICATION_SCOPES = {"", "source_lead_only", "metadata_only", "none", "artifact_identity_candidate"}
_APPROVED_ARTIFACT_AUTHORITIES = {
    "primary_official_source",
    "official_source",
    "stable_archive_plus_independent_corroboration",
    "independent_reputable_corroboration",
    "existing_repo_authority",
}

_HARD_QUERY_ORDER = (
    "manual for sound blaster ct1740",
    "old blue ftp client for xp",
    "latest firefox before xp support ended",
    "article about ray tracing in a 1994 magazine",
    "driver for win98",
    "windows 7 apps",
)
_FIXTURE_MARKERS = (
    "fixture",
    "evals/",
    "hard_query_fixture",
    "ia_metadata_fixture",
    "local_review_materialization",
    "local_reviewed_record",
)
_SOURCE_AUTHORITY_TO_PACKET_AUTHORITY = {
    "primary": "primary_official_source",
    "official": "official_source",
    "primary_official_source": "primary_official_source",
    "official_source": "official_source",
    "reputable_secondary": "independent_reputable_corroboration",
    "stable_catalog": "independent_reputable_corroboration",
    "stable_catalog_page": "independent_reputable_corroboration",
    "existing_repo_authority": "existing_repo_authority",
}
_SOURCE_TYPES_INSUFFICIENT_FOR_VERIFIED = {
    "archive_metadata_page",
    "ia_metadata",
    "ia_metadata_page",
    "local_fixture",
    "repo_record",
    "unknown",
}
_SOURCE_COLLECTION_CURATABLE_EXCLUSION_REASONS = {
    "needs_more_identity_or_source_evidence",
}
_CURATED_SOURCE_COLLECTION_TARGETS: tuple[dict[str, Any], ...] = (
    {
        "artifact_gate_candidate_reason": "curated concrete Windows utility target for source observation after local candidates are exhausted",
        "artifact_gate_excluded": False,
        "artifact_type": "software",
        "artifact_verified": False,
        "candidate_id": "artifact-gate-curated:7zip-19-00-windows",
        "evidence_hints": [
            "Official 7-Zip pages identify version 19.00 as a Windows release.",
            "Curated because the broad Windows 7 apps candidates are not concrete artifact identities.",
        ],
        "gate_eligible": False,
        "gate_exclusion_reason": "curated_concrete_source_target",
        "matched_queries": ["Windows 7 apps"],
        "missing_information": ["bounded source observation and manual review before truth promotion"],
        "no_download_performed": True,
        "non_verified_reason": "curated source target is not reviewed truth until evidence is collected",
        "platform_or_context": "Windows 7 / Windows desktop utility",
        "provenance": {
            "source": "curated_source_collection_target",
            "source_kind": "source_observation_batch_04_curation",
            "source_ref": "SOURCE-OBSERVATION-BATCH-04",
        },
        "query_hints": [
            "7-Zip 19.00 for Windows",
            "Windows 7 compatible archive utility",
            "official 7-Zip release/download page",
        ],
        "record_state": "",
        "review_state": "unreviewed",
        "safe_next_action": "observe official/catalog metadata pages only; do not download installers or archives",
        "schema_version": CANDIDATE_SCHEMA_VERSION,
        "source_authority": "curated_target",
        "source_family": "curated_source_target",
        "source_hints": ["https://www.7-zip.org/", "https://www.7-zip.org/download.html"],
        "source_index_document_id": "curated-source-target:7zip-19-00-windows",
        "source_observations": [],
        "status": "candidate",
        "summary": "Concrete 7-Zip 19.00 for Windows identity selected from a broad Windows 7 app scope.",
        "title": "7-Zip 19.00 for Windows",
        "verification_scope": "source_lead_only",
    },
    {
        "artifact_gate_candidate_reason": "curated concrete FTP/SFTP client target after the blue FTP clue remains ambiguous",
        "artifact_gate_excluded": False,
        "artifact_type": "software",
        "artifact_verified": False,
        "candidate_id": "artifact-gate-curated:winscp-5-21-8",
        "evidence_hints": [
            "WinSCP 5.21.8 has stable release-history and catalog metadata.",
            "Curated as a concrete FTP/SFTP client artifact, not as proof of the vague blue visual clue.",
        ],
        "gate_eligible": False,
        "gate_exclusion_reason": "curated_concrete_source_target",
        "matched_queries": ["old blue FTP client for XP"],
        "missing_information": ["bounded source observation and manual review before truth promotion"],
        "no_download_performed": True,
        "non_verified_reason": "curated source target is not reviewed truth until evidence is collected",
        "platform_or_context": "Windows FTP/SFTP client",
        "provenance": {
            "source": "curated_source_collection_target",
            "source_kind": "source_observation_batch_04_curation",
            "source_ref": "SOURCE-OBSERVATION-BATCH-04",
        },
        "query_hints": [
            "WinSCP 5.21.8",
            "FTP and SFTP client for Windows",
            "official WinSCP version history",
        ],
        "record_state": "",
        "review_state": "unreviewed",
        "safe_next_action": "observe release-history/catalog metadata only; do not download installer or portable archives",
        "schema_version": CANDIDATE_SCHEMA_VERSION,
        "source_authority": "curated_target",
        "source_family": "curated_source_target",
        "source_hints": ["https://winscp.net/eng/docs/history_old", "https://sourceforge.net/projects/winscp/files/WinSCP/5.21.8/"],
        "source_index_document_id": "curated-source-target:winscp-5-21-8",
        "source_observations": [],
        "status": "candidate",
        "summary": "Concrete WinSCP 5.21.8 FTP/SFTP client identity selected after the local blue FTP clue stayed ambiguous.",
        "title": "WinSCP 5.21.8",
        "verification_scope": "source_lead_only",
    },
)
_PRIVATE_SOURCE_MARKERS = ("file:", "\\", "c:\\", "d:\\", "users\\", ".eureka", ".aide", "local_review", "local_search_index")
_SECRET_MARKERS = ("token=", "api_key", "apikey", "password", "secret", "authorization:")


def list_artifact_gate_candidates(index_path: str | Path) -> dict[str, Any]:
    """Return deterministic artifact-gate seed candidates from a local index."""

    index, documents = _load_valid_index(index_path)
    candidates = [_candidate_from_document(document, index_path=str(index_path)) for document in documents]
    candidates = sorted(candidates, key=_candidate_sort_key)
    return {
        "schema_version": ARTIFACT_GATE_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "status": "pass",
        "index_path": str(index_path),
        "index_document_count": len(documents),
        "candidate_count": len(candidates),
        "seed_candidate_count": sum(1 for item in candidates if item.get("artifact_gate_excluded") is not True),
        "excluded_candidate_count": sum(1 for item in candidates if item.get("artifact_gate_excluded") is True),
        "artifact_verified_count": sum(1 for item in candidates if item.get("artifact_verified") is True),
        "source_family_counts": _counts(item.get("source_family") for item in candidates),
        "status_counts": _counts(item.get("status") for item in candidates),
        "candidates": candidates,
        "source_index_digest": _path_sha256(index_path),
        "source_index_schema_version": str(index.get("index_schema_version") or ""),
        "truth_promotion_performed": False,
        "downloads_performed": False,
        "file_fetch_performed": False,
        "live_network_used": False,
    }


def evidence_templates_from_candidates(candidates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [_evidence_packet_from_candidate(candidate, template=True) for candidate in candidates]


def evidence_packets_from_candidates(candidates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [_evidence_packet_from_candidate(candidate, template=False) for candidate in candidates]


def reviewed_artifact_records_from_evidence(packets: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for packet in packets:
        records.append(
            {
                "schema_version": REVIEWED_ARTIFACT_RECORD_SCHEMA_VERSION,
                "reviewed_artifact_record_id": _stable_id("reviewed-artifact-gate-record", packet.get("candidate_id")),
                "source_candidate_id": str(packet.get("candidate_id") or ""),
                "source_index_document_id": str(packet.get("source_index_document_id") or ""),
                "source_evidence_packet_id": str(packet.get("evidence_packet_id") or ""),
                "title": str(packet.get("artifact_title") or ""),
                "artifact_type": str(packet.get("artifact_type") or "unknown"),
                "platform_or_context": str(packet.get("platform_or_context") or ""),
                "artifact_identity_fields": dict(packet.get("artifact_identity_fields") or {}),
                "status": "candidate",
                "review_state": "reviewed_gate_seed",
                "artifact_verified": False,
                "accepted_truth": False,
                "gate_eligible": False,
                "gate_exclusion_reason": str(packet.get("gate_exclusion_reason") or "manual_external_evidence_required"),
                "verification_scope": str(packet.get("verification_scope") or "source_lead_only"),
                "source_authority": str(packet.get("source_authority") or "local_source_lead"),
                "evidence_type": str(packet.get("evidence_type") or "source_metadata_lead"),
                "reviewer": str(packet.get("reviewer") or "artifact_gate_seed"),
                "review_rationale": str(packet.get("review_rationale") or ""),
                "source_observations": _object_list(packet.get("source_observations")),
                "evidence_hints": _string_list(packet.get("evidence_hints")),
                "source_hints": _string_list(packet.get("source_hints")),
                "provenance": dict(packet.get("provenance") or {}),
                "non_verified_reason": "artifact gate seed record is a non-verified source lead; manual artifact evidence is still required",
                "binary_verified": False,
                "download_safe": False,
                "execution_safe": False,
                "rights_cleared": False,
                "no_download_performed": True,
                "file_fetch_performed": False,
                "live_network_used": False,
            }
        )
    return records


def seed_artifact_gate(index_path: str | Path, gate_dir: str | Path, *, max_records: int = 5) -> dict[str, Any]:
    """Write a complete local artifact-gate seed bundle."""

    gate_path = Path(gate_dir)
    gate_path.mkdir(parents=True, exist_ok=True)

    candidate_payload = list_artifact_gate_candidates(index_path)
    candidates = [dict(item) for item in candidate_payload["candidates"]]
    seed_candidates = [item for item in candidates if item.get("artifact_gate_excluded") is not True]
    seed_candidates = seed_candidates[: max(0, int(max_records))]
    templates = evidence_templates_from_candidates(seed_candidates)
    packets = evidence_packets_from_candidates(seed_candidates)
    records = reviewed_artifact_records_from_evidence(packets)

    write_jsonl(gate_path / DEFAULT_CANDIDATES_FILE, candidates)
    write_jsonl(gate_path / DEFAULT_EVIDENCE_TEMPLATE_FILE, templates)
    write_jsonl(gate_path / DEFAULT_EVIDENCE_PACKETS_FILE, packets)
    write_jsonl(gate_path / DEFAULT_REVIEWED_ARTIFACT_RECORDS_FILE, records)

    report = build_gate_report(
        gate_path,
        index_path=index_path,
        candidates=candidates,
        evidence_packets=packets,
        reviewed_artifact_records=records,
        max_records=max_records,
    )
    write_json(gate_path / DEFAULT_GATE_REPORT_FILE, report)
    (gate_path / DEFAULT_GATE_REPORT_MD).write_text(render_gate_markdown(report), encoding="utf-8")
    return report


def build_gate_report(
    gate_dir: str | Path,
    *,
    index_path: str | Path,
    candidates: Sequence[Mapping[str, Any]],
    evidence_packets: Sequence[Mapping[str, Any]],
    reviewed_artifact_records: Sequence[Mapping[str, Any]],
    max_records: int,
) -> dict[str, Any]:
    candidate_count = len(candidates)
    seed_candidate_count = sum(1 for item in candidates if item.get("artifact_gate_excluded") is not True)
    excluded_candidate_count = candidate_count - seed_candidate_count
    evidence_packet_count = len(evidence_packets)
    reviewed_record_count = len(reviewed_artifact_records)
    artifact_verified_count = sum(1 for item in reviewed_artifact_records if item.get("artifact_verified") is True)
    gate_eligible_count = sum(1 for item in reviewed_artifact_records if item.get("gate_eligible") is True)
    reviewed_artifact_gate_count = sum(
        1
        for item in reviewed_artifact_records
        if item.get("artifact_verified") is True and item.get("gate_eligible") is True
    )
    blockers = []
    if reviewed_artifact_gate_count < DEFAULT_GATE_TARGET:
        blockers.append(
            {
                "id": "reviewed_artifact_gate_count_below_target",
                "message": f"reviewed artifact gate count is {reviewed_artifact_gate_count}/{DEFAULT_GATE_TARGET}",
                "status": "blocked",
            }
        )
    if artifact_verified_count == 0:
        blockers.append(
            {
                "id": "artifact_verified_count_zero",
                "message": "no artifact-verified evidence packets exist in this local seed bundle",
                "status": "blocked",
            }
        )
    if gate_eligible_count == 0:
        blockers.append(
            {
                "id": "manual_external_evidence_required",
                "message": "local seed records are source leads only; manual external evidence is required",
                "status": "blocked",
            }
        )

    status = "PASS" if not blockers else "PASS_WITH_WARNINGS"
    gate_status = "pass" if reviewed_artifact_gate_count >= DEFAULT_GATE_TARGET else "blocked"
    return {
        "schema_version": ARTIFACT_GATE_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "status": status,
        "gate_status": gate_status,
        "gate_scope": "public_alpha_seed",
        "gate_dir": str(gate_dir),
        "source_index_path": str(index_path),
        "source_index_digest": _path_sha256(index_path),
        "gate_target_reviewed_artifacts": DEFAULT_GATE_TARGET,
        "official_reviewed_artifact_gate_target": DEFAULT_GATE_TARGET,
        "reviewed_artifact_gate_count": reviewed_artifact_gate_count,
        "official_reviewed_artifact_count": reviewed_artifact_gate_count,
        "reviewed_artifact_record_count": reviewed_record_count,
        "evidence_packet_count": evidence_packet_count,
        "candidate_count": candidate_count,
        "seed_candidate_count": seed_candidate_count,
        "excluded_candidate_count": excluded_candidate_count,
        "artifact_verified_count": artifact_verified_count,
        "gate_eligible_count": gate_eligible_count,
        "status_counts": _counts(item.get("status") for item in candidates),
        "source_family_counts": _counts(item.get("source_family") for item in candidates),
        "source_authority_counts": _counts(item.get("source_authority") for item in evidence_packets),
        "verification_scope_counts": _counts(item.get("verification_scope") for item in evidence_packets),
        "gate_exclusion_counts": _counts(item.get("gate_exclusion_reason") for item in evidence_packets),
        "blockers": blockers,
        "warnings": [
            "local seed output is not official artifact gate completion",
            "fixture, IA metadata, and local reviewed source leads remain non-verified",
            "manual external evidence collection is still required",
        ],
        "max_records": int(max_records),
        "truth_promotion_performed": False,
        "verified_artifact_truth_created": False,
        "downloads_performed": False,
        "file_fetch_performed": False,
        "wayback_replay_performed": False,
        "live_network_used": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "official_gate_counts_mutated": False,
        "generated_at": "1970-01-01T00:00:00Z",
        "next_recommended_task": "MANUAL-ARTIFACT-EVIDENCE-BATCH-01",
    }


def validate_gate(gate_dir: str | Path) -> list[str]:
    gate_path = Path(gate_dir)
    errors: list[str] = []
    paths = {
        "candidates": gate_path / DEFAULT_CANDIDATES_FILE,
        "evidence_packets": gate_path / DEFAULT_EVIDENCE_PACKETS_FILE,
        "reviewed_artifact_records": gate_path / DEFAULT_REVIEWED_ARTIFACT_RECORDS_FILE,
        "report": gate_path / DEFAULT_GATE_REPORT_FILE,
    }
    for name, path in paths.items():
        if not path.is_file():
            errors.append(f"missing {name}: {path}")
    if errors:
        return errors

    candidates = read_jsonl(paths["candidates"])
    packets = read_jsonl(paths["evidence_packets"])
    records = read_jsonl(paths["reviewed_artifact_records"])
    try:
        report = json.loads(paths["report"].read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"artifact gate report is invalid JSON: {exc.msg}"]

    errors.extend(validate_gate_report(report, candidates=candidates, evidence_packets=packets, records=records))
    for index, packet in enumerate(packets, start=1):
        for error in validate_evidence_packet(packet):
            errors.append(f"evidence_packets[{index}]: {error}")
    for index, record in enumerate(records, start=1):
        if record.get("artifact_verified") is True:
            errors.append(f"reviewed_artifact_records[{index}]: artifact_verified must remain false for seed records")
        if record.get("accepted_truth") is True:
            errors.append(f"reviewed_artifact_records[{index}]: accepted_truth must remain false for seed records")
        if record.get("download_safe") is True or record.get("execution_safe") is True:
            errors.append(f"reviewed_artifact_records[{index}]: download/execution safety cannot be asserted by seed records")
    return errors


def validate_gate_report(
    report: Mapping[str, Any],
    *,
    candidates: Sequence[Mapping[str, Any]],
    evidence_packets: Sequence[Mapping[str, Any]],
    records: Sequence[Mapping[str, Any]],
) -> list[str]:
    required = (
        "schema_version",
        "task_id",
        "status",
        "gate_status",
        "gate_target_reviewed_artifacts",
        "reviewed_artifact_gate_count",
        "artifact_verified_count",
        "candidate_count",
        "evidence_packet_count",
        "reviewed_artifact_record_count",
        "blockers",
        "warnings",
        "next_recommended_task",
    )
    errors = [f"missing required field: {key}" for key in required if key not in report]
    if errors:
        return errors
    if report.get("schema_version") != ARTIFACT_GATE_SCHEMA_VERSION:
        errors.append(f"schema_version must be {ARTIFACT_GATE_SCHEMA_VERSION}")
    if report.get("task_id") != TASK_ID:
        errors.append(f"task_id must be {TASK_ID}")
    if report.get("status") not in {"PASS", "PASS_WITH_WARNINGS", "FAIL"}:
        errors.append("status must be PASS, PASS_WITH_WARNINGS, or FAIL")
    if report.get("gate_status") not in {"pass", "blocked", "fail"}:
        errors.append("gate_status must be pass, blocked, or fail")
    expected_verified = sum(1 for item in records if item.get("artifact_verified") is True)
    expected_gate_count = sum(1 for item in records if item.get("artifact_verified") is True and item.get("gate_eligible") is True)
    expected_gate_eligible = sum(1 for item in records if item.get("gate_eligible") is True)
    if _int_report_field(report, "candidate_count", -1) != len(candidates):
        errors.append("candidate_count must match candidates.jsonl")
    if _int_report_field(report, "evidence_packet_count", -1) != len(evidence_packets):
        errors.append("evidence_packet_count must match evidence_packets.jsonl")
    if _int_report_field(report, "reviewed_artifact_record_count", -1) != len(records):
        errors.append("reviewed_artifact_record_count must match reviewed_artifact_records.jsonl")
    if _int_report_field(report, "artifact_verified_count", -1) != expected_verified:
        errors.append("artifact_verified_count must match reviewed_artifact_records.jsonl")
    if _int_report_field(report, "reviewed_artifact_gate_count", -1) != expected_gate_count:
        errors.append("reviewed_artifact_gate_count must count gate-eligible verified records only")
    if _int_report_field(report, "gate_eligible_count", 0) != expected_gate_eligible:
        errors.append("gate_eligible_count must match reviewed_artifact_records.jsonl")
    if expected_verified == 0 and report.get("gate_status") == "pass":
        errors.append("gate_status cannot pass with artifact_verified_count=0")
    if expected_gate_count < _int_report_field(report, "gate_target_reviewed_artifacts", DEFAULT_GATE_TARGET) and report.get("gate_status") == "pass":
        errors.append("gate_status cannot pass below target")
    return errors


def validate_evidence_packet(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    required_text = ("evidence_packet_id", "candidate_id", "artifact_title", "reviewer", "review_rationale")
    for key in required_text:
        if not str(packet.get(key) or "").strip():
            errors.append(f"{key} is required")
    identity = packet.get("artifact_identity_fields") if isinstance(packet.get("artifact_identity_fields"), Mapping) else {}
    if not any(str(identity.get(key) or "").strip() for key in ("title", "identifier", "platform_or_context", "source_index_document_id")):
        errors.append("artifact_identity_fields must include source identity")
    if not _object_list(packet.get("source_observations")) and not _string_list(packet.get("source_hints")):
        errors.append("source identity or source observations are required")
    if packet.get("no_download_performed") is not True:
        errors.append("no_download_performed must be true for seed evidence")
    if packet.get("file_fetch_performed") is True:
        errors.append("file_fetch_performed must be false for seed evidence")
    if packet.get("binary_verified") is True:
        errors.append("binary_verified cannot be true for seed evidence")
    if packet.get("download_safe") is True or packet.get("execution_safe") is True:
        errors.append("download_safe/execution_safe cannot be true for seed evidence")
    if packet.get("artifact_verified") is True:
        if packet.get("gate_eligible") is not True:
            errors.append("artifact_verified evidence requires gate_eligible true")
        if str(packet.get("verification_scope") or "") in {"", "source_lead_only", "metadata_only", "none"}:
            errors.append("artifact_verified evidence requires stronger verification_scope")
        if _evidence_source_is_fixture_only(packet):
            errors.append("fixture-only or metadata-only evidence cannot be artifact_verified")
    return errors


def gate_status(gate_dir: str | Path) -> dict[str, Any]:
    gate_path = Path(gate_dir)
    report_path = gate_path / DEFAULT_GATE_REPORT_FILE
    if not report_path.is_file():
        return {
            "schema_version": "eureka.artifact_gate_seed_status.v0",
            "status": "fail",
            "gate_dir": str(gate_path),
            "errors": [f"missing report: {report_path}"],
        }
    report = json.loads(report_path.read_text(encoding="utf-8"))
    errors = validate_gate(gate_path)
    return {
        "schema_version": "eureka.artifact_gate_seed_status.v0",
        "status": "pass" if not errors else "fail",
        "gate_dir": str(gate_path),
        "report_status": report.get("status"),
        "gate_status": report.get("gate_status"),
        "candidate_count": report.get("candidate_count"),
        "evidence_packet_count": report.get("evidence_packet_count"),
        "reviewed_artifact_record_count": report.get("reviewed_artifact_record_count"),
        "reviewed_artifact_gate_count": report.get("reviewed_artifact_gate_count"),
        "gate_target_reviewed_artifacts": report.get("gate_target_reviewed_artifacts"),
        "artifact_verified_count": report.get("artifact_verified_count"),
        "blockers": report.get("blockers") or [],
        "warnings": report.get("warnings") or [],
        "errors": errors,
        "next_recommended_task": report.get("next_recommended_task"),
    }


def export_launch_report(gate_dir: str | Path, out_path: str | Path) -> dict[str, Any]:
    gate_path = Path(gate_dir)
    report = json.loads((gate_path / DEFAULT_GATE_REPORT_FILE).read_text(encoding="utf-8"))
    destination = Path(out_path)
    write_json(destination, report)
    return report


def create_manual_batch_plan(gate_dir: str | Path, batch_dir: str | Path, *, target_records: int = 5) -> dict[str, Any]:
    gate_path = Path(gate_dir)
    batch_path = Path(batch_dir)
    batch_path.mkdir(parents=True, exist_ok=True)
    candidates = read_jsonl(gate_path / DEFAULT_CANDIDATES_FILE)
    seed_report = json.loads((gate_path / DEFAULT_GATE_REPORT_FILE).read_text(encoding="utf-8"))
    target = max(1, int(target_records))
    selectable = [dict(item) for item in candidates if item.get("artifact_gate_excluded") is not True]
    selected_ids = {str(item.get("candidate_id") or "") for item in selectable[:target]}
    plan_rows = []
    for position, candidate in enumerate(sorted((dict(item) for item in candidates), key=_candidate_sort_key), start=1):
        candidate_id = str(candidate.get("candidate_id") or "")
        selected = candidate_id in selected_ids
        plan_rows.append(
            {
                **candidate,
                "batch_id": _batch_id(batch_path),
                "plan_position": position,
                "manual_batch_selected": selected,
                "manual_batch_target": selected and candidate.get("artifact_gate_excluded") is not True,
                "manual_evidence_required": True,
                "manual_batch_reason": (
                    "selected for bounded manual evidence collection"
                    if selected
                    else str(candidate.get("gate_exclusion_reason") or "not selected for this bounded batch")
                ),
            }
        )
    manifest = {
        "schema_version": MANUAL_BATCH_SCHEMA_VERSION,
        "task_id": MANUAL_BATCH_TASK_ID,
        "batch_id": _batch_id(batch_path),
        "status": "pass",
        "gate_dir": str(gate_path),
        "batch_dir": str(batch_path),
        "source_gate_report": str(gate_path / DEFAULT_GATE_REPORT_FILE),
        "source_gate_report_digest": _path_sha256(gate_path / DEFAULT_GATE_REPORT_FILE),
        "candidate_count": len(plan_rows),
        "selected_candidate_count": len(selected_ids),
        "excluded_candidate_count": sum(1 for item in plan_rows if item.get("artifact_gate_excluded") is True),
        "target_records": target,
        "gate_target_reviewed_artifacts": DEFAULT_GATE_TARGET,
        "source_gate_status": seed_report.get("gate_status"),
        "source_artifact_verified_count": seed_report.get("artifact_verified_count"),
        "truth_promotion_performed": False,
        "downloads_performed": False,
        "file_fetch_performed": False,
        "live_network_used": False,
        "generated_at": "1970-01-01T00:00:00Z",
    }
    write_json(batch_path / MANUAL_BATCH_MANIFEST_FILE, manifest)
    write_jsonl(batch_path / MANUAL_BATCH_CANDIDATE_PLAN_FILE, plan_rows)
    return manifest


def write_manual_evidence_template(batch_dir: str | Path, out_path: str | Path | None = None) -> dict[str, Any]:
    batch_path = Path(batch_dir)
    rows = read_jsonl(batch_path / MANUAL_BATCH_CANDIDATE_PLAN_FILE)
    selected = [row for row in rows if row.get("manual_batch_selected") is True and row.get("artifact_gate_excluded") is not True]
    templates = [_manual_template_from_candidate(candidate, batch_id=_batch_id(batch_path)) for candidate in selected]
    destination = Path(out_path) if out_path else batch_path / MANUAL_BATCH_TEMPLATE_FILE
    write_jsonl(destination, templates)
    return {
        "schema_version": MANUAL_BATCH_SCHEMA_VERSION,
        "task_id": MANUAL_BATCH_TASK_ID,
        "status": "pass",
        "batch_id": _batch_id(batch_path),
        "batch_dir": str(batch_path),
        "out": str(destination),
        "template_count": len(templates),
    }


def ingest_manual_evidence(batch_dir: str | Path, evidence_path: str | Path) -> dict[str, Any]:
    batch_path = Path(batch_dir)
    packets = read_jsonl(evidence_path)
    destination = batch_path / MANUAL_BATCH_EVIDENCE_FILE
    write_jsonl(destination, packets)
    report = validate_manual_batch(batch_path)
    return {
        "schema_version": MANUAL_BATCH_SCHEMA_VERSION,
        "task_id": MANUAL_BATCH_TASK_ID,
        "status": "pass" if report["invalid_evidence_packet_count"] == 0 else "fail",
        "batch_id": _batch_id(batch_path),
        "batch_dir": str(batch_path),
        "evidence": str(evidence_path),
        "out": str(destination),
        "evidence_packet_count": len(packets),
        "valid_evidence_packet_count": report["valid_evidence_packet_count"],
        "invalid_evidence_packet_count": report["invalid_evidence_packet_count"],
        "errors": report["errors"],
    }


def validate_manual_batch(batch_dir: str | Path) -> dict[str, Any]:
    batch_path = Path(batch_dir)
    errors: list[str] = []
    warnings: list[str] = []
    evidence_path = batch_path / MANUAL_BATCH_EVIDENCE_FILE
    if not evidence_path.is_file():
        warnings.append(f"missing evidence packets: {evidence_path}")
        packets: list[dict[str, Any]] = []
    else:
        packets = read_jsonl(evidence_path)
    diagnostics = []
    valid_count = 0
    invalid_count = 0
    for index, packet in enumerate(packets, start=1):
        packet_errors = validate_manual_evidence_packet(packet)
        diagnostics.append(
            {
                "packet_index": index,
                "evidence_packet_id": str(packet.get("evidence_packet_id") or ""),
                "candidate_id": str(packet.get("candidate_id") or ""),
                "status": "valid" if not packet_errors else "invalid",
                "errors": packet_errors,
                "artifact_verified": bool(packet.get("artifact_verified") is True),
                "gate_eligible": bool(packet.get("gate_eligible") is True),
            }
        )
        if packet_errors:
            invalid_count += 1
            errors.extend(f"packet[{index}]: {error}" for error in packet_errors)
        else:
            valid_count += 1
    report = {
        "schema_version": MANUAL_BATCH_SCHEMA_VERSION,
        "task_id": MANUAL_BATCH_TASK_ID,
        "status": "fail" if invalid_count else ("pass_with_warnings" if warnings else "pass"),
        "batch_id": _batch_id(batch_path),
        "batch_dir": str(batch_path),
        "evidence_packet_count": len(packets),
        "valid_evidence_packet_count": valid_count,
        "invalid_evidence_packet_count": invalid_count,
        "artifact_verified_packet_count": sum(1 for packet in packets if packet.get("artifact_verified") is True),
        "gate_eligible_packet_count": sum(1 for packet in packets if packet.get("gate_eligible") is True),
        "diagnostics": diagnostics,
        "errors": errors,
        "warnings": warnings,
        "truth_promotion_performed": False,
        "downloads_performed": False,
        "file_fetch_performed": False,
        "live_network_used": any(packet.get("live_network_used") is True for packet in packets),
    }
    write_json(batch_path / MANUAL_BATCH_VALIDATION_REPORT_FILE, report)
    return report


def validate_manual_evidence_packet(packet: Mapping[str, Any]) -> list[str]:
    errors = validate_evidence_packet(packet)
    required_text = (
        "batch_id",
        "artifact_type",
        "platform_or_context",
        "evidence_type",
        "source_authority",
        "verification_scope",
    )
    for key in required_text:
        if not str(packet.get(key) or "").strip():
            errors.append(f"{key} is required")
    if not str(packet.get("collected_at") or packet.get("observed_at") or "").strip():
        errors.append("collected_at or observed_at is required")
    if not _string_list(packet.get("observed_fields")):
        errors.append("observed_fields are required")
    if not (_string_list(packet.get("evidence_urls")) or _string_list(packet.get("source_identifiers")) or _object_list(packet.get("source_observations"))):
        errors.append("evidence_urls, source_identifiers, or source_observations are required")
    for index, observation in enumerate(_object_list(packet.get("source_observations")), start=1):
        if not str(observation.get("source_id") or observation.get("observation_id") or "").strip():
            errors.append(f"source_observations[{index}].source_id is required")
        if not str(observation.get("source_url") or observation.get("source_identifier") or observation.get("value") or "").strip():
            errors.append(f"source_observations[{index}] must include source_url or source_identifier")
        if observation.get("downloaded_file") is True or observation.get("fetched_binary") is True:
            errors.append(f"source_observations[{index}] cannot download or fetch binaries")
        if str(observation.get("access_method") or "").strip().casefold() in {"local_fixture", "repo_record"} and packet.get("artifact_verified") is True:
            errors.append(f"source_observations[{index}] fixture/repo observations cannot verify artifacts")
    if packet.get("rights_cleared") is True:
        errors.append("rights_cleared cannot be true in this manual batch workflow")
    if packet.get("artifact_verified") is True:
        errors.extend(_manual_artifact_verified_errors(packet))
    elif packet.get("gate_eligible") is True:
        errors.append("gate_eligible true requires artifact_verified true")
    return _dedupe(errors)


def review_manual_batch(batch_dir: str | Path, *, reviewer: str, out_path: str | Path | None = None) -> dict[str, Any]:
    batch_path = Path(batch_dir)
    validation = validate_manual_batch(batch_path)
    packets = _manual_packets(batch_path)
    diagnostics = {
        str(item.get("evidence_packet_id") or ""): dict(item)
        for item in validation.get("diagnostics") or []
        if isinstance(item, Mapping)
    }
    records = []
    rejected = []
    seen_identity_keys: dict[str, str] = {}
    for packet in packets:
        packet_id = str(packet.get("evidence_packet_id") or "")
        diagnostic = diagnostics.get(packet_id, {})
        if diagnostic.get("status") == "valid" and packet.get("artifact_verified") is True and packet.get("gate_eligible") is True:
            identity_key = _manual_packet_identity_key(packet)
            duplicate_of = seen_identity_keys.get(identity_key)
            if duplicate_of:
                rejected.append(
                    {
                        "evidence_packet_id": packet_id,
                        "candidate_id": str(packet.get("candidate_id") or ""),
                        "status": "duplicate",
                        "errors": ["duplicate artifact identity already counted in this manual batch"],
                        "gate_exclusion_reason": "duplicate_artifact_identity",
                        "artifact_verified": True,
                        "gate_eligible": False,
                        "duplicate_of": duplicate_of,
                    }
                )
                continue
            record = _reviewed_record_from_manual_packet(packet, reviewer=reviewer)
            records.append(record)
            seen_identity_keys[identity_key] = str(record.get("reviewed_artifact_record_id") or packet_id)
        else:
            rejected.append(
                {
                    "evidence_packet_id": packet_id,
                    "candidate_id": str(packet.get("candidate_id") or ""),
                    "status": "rejected" if diagnostic.get("status") == "invalid" else "non_eligible",
                    "errors": list(diagnostic.get("errors") or []),
                    "gate_exclusion_reason": str(packet.get("gate_exclusion_reason") or "insufficient_artifact_evidence"),
                    "artifact_verified": bool(packet.get("artifact_verified") is True),
                    "gate_eligible": bool(packet.get("gate_eligible") is True),
                }
            )
    destination = Path(out_path) if out_path else batch_path / DEFAULT_REVIEWED_ARTIFACT_RECORDS_FILE
    write_jsonl(destination, records)
    review_report = {
        "schema_version": MANUAL_BATCH_SCHEMA_VERSION,
        "task_id": MANUAL_BATCH_TASK_ID,
        "status": "pass" if not validation.get("errors") else "pass_with_warnings",
        "batch_id": _batch_id(batch_path),
        "batch_dir": str(batch_path),
        "reviewer": reviewer,
        "out": str(destination),
        "reviewed_artifact_record_count": len(records),
        "rejected_or_non_eligible_count": len(rejected),
        "rejected_or_non_eligible": rejected,
        "artifact_verified_count": sum(1 for record in records if record.get("artifact_verified") is True),
        "binary_verified_count": sum(1 for record in records if record.get("binary_verified") is True),
        "download_safe_count": sum(1 for record in records if record.get("download_safe") is True),
        "execution_safe_count": sum(1 for record in records if record.get("execution_safe") is True),
        "truth_promotion_performed": False,
    }
    write_json(batch_path / "manual_review_report.json", review_report)
    return review_report


def write_manual_batch_report(batch_dir: str | Path, out_path: str | Path | None = None) -> dict[str, Any]:
    batch_path = Path(batch_dir)
    validation = validate_manual_batch(batch_path)
    candidate_plan = read_jsonl(batch_path / MANUAL_BATCH_CANDIDATE_PLAN_FILE) if (batch_path / MANUAL_BATCH_CANDIDATE_PLAN_FILE).is_file() else []
    packets = _manual_packets(batch_path)
    records_path = batch_path / DEFAULT_REVIEWED_ARTIFACT_RECORDS_FILE
    records = read_jsonl(records_path) if records_path.is_file() else []
    report = _manual_batch_report(batch_path, candidate_plan=candidate_plan, packets=packets, records=records, validation=validation)
    destination = Path(out_path) if out_path else batch_path / DEFAULT_GATE_REPORT_FILE
    write_json(destination, report)
    write_json(batch_path / DEFAULT_GATE_REPORT_FILE, report)
    (batch_path / DEFAULT_GATE_REPORT_MD).write_text(render_gate_markdown(report), encoding="utf-8")
    (batch_path / MANUAL_BATCH_REPORT_MD).write_text(render_manual_batch_markdown(report), encoding="utf-8")
    return report


def manual_batch_status(batch_dir: str | Path) -> dict[str, Any]:
    batch_path = Path(batch_dir)
    report_path = batch_path / DEFAULT_GATE_REPORT_FILE
    validation_path = batch_path / MANUAL_BATCH_VALIDATION_REPORT_FILE
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {}
    validation = json.loads(validation_path.read_text(encoding="utf-8")) if validation_path.is_file() else validate_manual_batch(batch_path)
    return {
        "schema_version": MANUAL_BATCH_SCHEMA_VERSION,
        "task_id": MANUAL_BATCH_TASK_ID,
        "status": "pass" if report_path.is_file() else "pass_with_warnings",
        "batch_id": _batch_id(batch_path),
        "batch_dir": str(batch_path),
        "gate_status": report.get("gate_status", "blocked"),
        "report_status": report.get("status", "PASS_WITH_WARNINGS"),
        "candidate_count": report.get("candidate_count", 0),
        "evidence_packet_count": validation.get("evidence_packet_count", report.get("evidence_packet_count", 0)),
        "valid_evidence_packet_count": validation.get("valid_evidence_packet_count", report.get("valid_evidence_packet_count", 0)),
        "invalid_evidence_packet_count": validation.get("invalid_evidence_packet_count", report.get("invalid_evidence_packet_count", 0)),
        "reviewed_artifact_gate_count": report.get("reviewed_artifact_gate_count", 0),
        "gate_target_reviewed_artifacts": report.get("gate_target_reviewed_artifacts", DEFAULT_GATE_TARGET),
        "artifact_verified_count": report.get("artifact_verified_count", 0),
        "blockers": report.get("blockers", []),
        "warnings": [*list(report.get("warnings") or []), *list(validation.get("warnings") or [])],
        "next_recommended_task": report.get("next_recommended_task", "ARTIFACT-EVIDENCE-SOURCE-COLLECTION-00"),
    }


def create_source_collection_plan(
    gate_dir: str | Path,
    manual_batch_dir: str | Path,
    collection_dir: str | Path,
    *,
    target_records: int = 5,
) -> dict[str, Any]:
    gate_path = Path(gate_dir)
    batch_path = Path(manual_batch_dir)
    collection_path = Path(collection_dir)
    collection_path.mkdir(parents=True, exist_ok=True)

    gate_candidates = read_jsonl(gate_path / DEFAULT_CANDIDATES_FILE)
    manual_plan_path = batch_path / MANUAL_BATCH_CANDIDATE_PLAN_FILE
    manual_plan = read_jsonl(manual_plan_path) if manual_plan_path.is_file() else []
    reviewed_records_path = batch_path / DEFAULT_REVIEWED_ARTIFACT_RECORDS_FILE
    reviewed_records = read_jsonl(reviewed_records_path) if reviewed_records_path.is_file() else []
    target = max(1, int(target_records))

    manual_selected_ids = {
        str(item.get("candidate_id") or "")
        for item in manual_plan
        if item.get("manual_batch_selected") is True and item.get("artifact_gate_excluded") is not True
    }
    annotated_candidates = []
    for item in sorted(gate_candidates, key=_candidate_sort_key):
        candidate = dict(item)
        duplicate = _source_collection_duplicate_info(candidate, reviewed_records)
        curation_target = _source_collection_curation_target(candidate, duplicate)
        candidate.update(
            {
                "source_collection_duplicate": duplicate["is_duplicate"],
                "source_collection_duplicate_of": duplicate["duplicate_of"],
                "source_collection_duplicate_identity": duplicate["duplicate_identity"],
                "source_collection_duplicate_reason": duplicate["duplicate_reason"],
                "source_collection_curation_target": curation_target,
            }
        )
        annotated_candidates.append(candidate)
    selectable = _source_collection_selectable_candidates(annotated_candidates)
    curated_candidate_count = 0
    if not selectable:
        curated = _curated_source_collection_candidates(reviewed_records)
        curated_candidate_count = len(curated)
        annotated_candidates = [*annotated_candidates, *curated]
        selectable = _source_collection_selectable_candidates(annotated_candidates)
    if manual_selected_ids:
        preferred = [item for item in selectable if str(item.get("candidate_id") or "") in manual_selected_ids]
        remaining = [item for item in selectable if str(item.get("candidate_id") or "") not in manual_selected_ids]
        selectable = [*preferred, *remaining]
    selected_ids = {str(item.get("candidate_id") or "") for item in selectable[:target]}

    plan_rows = []
    for position, candidate in enumerate(annotated_candidates, start=1):
        candidate_id = str(candidate.get("candidate_id") or "")
        selected = candidate_id in selected_ids
        excluded = candidate.get("artifact_gate_excluded") is True
        duplicate = candidate.get("source_collection_duplicate") is True
        curation_target = candidate.get("source_collection_curation_target") is True
        source_target = selected and not duplicate and (not excluded or curation_target)
        if duplicate:
            reason = str(candidate.get("source_collection_duplicate_reason") or "duplicate artifact identity already counted")
        elif source_target and curation_target:
            reason = "selected for bounded source observation to resolve missing identity/source evidence"
        elif source_target:
            reason = "selected for bounded source observation"
        else:
            reason = str(candidate.get("gate_exclusion_reason") or "not selected for this bounded source collection")
        plan_rows.append(
            {
                **candidate,
                "collection_id": _collection_id(collection_path),
                "manual_batch_id": _batch_id(batch_path),
                "plan_position": position,
                "source_collection_selected": selected,
                "source_collection_target": source_target,
                "source_collection_reason": reason,
                "expected_source_types": _expected_source_types(candidate),
                "source_collection_instructions": [
                    "record page, catalog, support, release-note, manual-page, or publication metadata only",
                    "do not download files, fetch binaries, or use Wayback replay",
                    "artifact_verified true requires explicit gate criteria and reviewer rationale",
                ],
            }
        )

    source_gate_report = gate_path / DEFAULT_GATE_REPORT_FILE
    manifest = {
        "schema_version": SOURCE_COLLECTION_SCHEMA_VERSION,
        "task_id": SOURCE_COLLECTION_TASK_ID,
        "collection_id": _collection_id(collection_path),
        "status": "pass",
        "gate_dir": str(gate_path),
        "manual_batch_dir": str(batch_path),
        "manual_batch_id": _batch_id(batch_path),
        "collection_dir": str(collection_path),
        "source_gate_report": str(source_gate_report),
        "source_gate_report_digest": _path_sha256(source_gate_report),
        "candidate_count": len(plan_rows),
        "selected_candidate_count": sum(1 for item in plan_rows if item.get("source_collection_target") is True),
        "curated_candidate_count": curated_candidate_count,
        "duplicate_candidate_count": sum(1 for item in plan_rows if item.get("source_collection_duplicate") is True),
        "excluded_candidate_count": sum(1 for item in plan_rows if item.get("artifact_gate_excluded") is True),
        "target_records": target,
        "gate_target_reviewed_artifacts": DEFAULT_GATE_TARGET,
        "truth_promotion_performed": False,
        "downloads_performed": False,
        "file_fetch_performed": False,
        "wayback_replay_performed": False,
        "live_network_used": False,
        "generated_at": "1970-01-01T00:00:00Z",
    }
    write_json(collection_path / SOURCE_COLLECTION_MANIFEST_FILE, manifest)
    write_jsonl(collection_path / SOURCE_COLLECTION_CANDIDATE_PLAN_FILE, plan_rows)
    write_jsonl(collection_path / SOURCE_COLLECTION_URL_LIST_TEMPLATE_FILE, _source_url_list_templates(plan_rows))
    return manifest


def write_source_observation_template(collection_dir: str | Path, out_path: str | Path | None = None) -> dict[str, Any]:
    collection_path = Path(collection_dir)
    plan_rows = read_jsonl(collection_path / SOURCE_COLLECTION_CANDIDATE_PLAN_FILE)
    selected = [row for row in plan_rows if row.get("source_collection_target") is True]
    templates = [_source_observation_template_from_candidate(candidate, collection_id=_collection_id(collection_path)) for candidate in selected]
    destination = Path(out_path) if out_path else collection_path / SOURCE_COLLECTION_TEMPLATE_FILE
    write_jsonl(destination, templates)
    return {
        "schema_version": SOURCE_COLLECTION_SCHEMA_VERSION,
        "task_id": SOURCE_COLLECTION_TASK_ID,
        "status": "pass",
        "collection_id": _collection_id(collection_path),
        "collection_dir": str(collection_path),
        "out": str(destination),
        "template_count": len(templates),
    }


def ingest_source_observations(collection_dir: str | Path, observations_path: str | Path) -> dict[str, Any]:
    collection_path = Path(collection_dir)
    observations = read_jsonl(observations_path)
    destination = collection_path / SOURCE_COLLECTION_OBSERVATIONS_FILE
    write_jsonl(destination, observations)
    report = validate_source_collection(collection_path)
    return {
        "schema_version": SOURCE_COLLECTION_SCHEMA_VERSION,
        "task_id": SOURCE_COLLECTION_TASK_ID,
        "status": "pass" if report["invalid_observation_count"] == 0 else "fail",
        "collection_id": _collection_id(collection_path),
        "collection_dir": str(collection_path),
        "observations": str(observations_path),
        "out": str(destination),
        "observation_count": len(observations),
        "valid_observation_count": report["valid_observation_count"],
        "invalid_observation_count": report["invalid_observation_count"],
        "errors": report["errors"],
    }


def validate_source_collection(collection_dir: str | Path) -> dict[str, Any]:
    collection_path = Path(collection_dir)
    errors: list[str] = []
    warnings: list[str] = []
    observations_path = collection_path / SOURCE_COLLECTION_OBSERVATIONS_FILE
    if not observations_path.is_file():
        warnings.append(f"missing source observations: {observations_path}")
        observations: list[dict[str, Any]] = []
    else:
        observations = read_jsonl(observations_path)

    plan_rows = _source_plan_rows(collection_path)
    candidate_by_id = {str(item.get("candidate_id") or ""): dict(item) for item in plan_rows}
    diagnostics = []
    valid_count = 0
    invalid_count = 0
    for index, observation in enumerate(observations, start=1):
        observation_errors = validate_source_observation(observation, candidate_by_id=candidate_by_id)
        diagnostics.append(
            {
                "observation_index": index,
                "source_observation_id": str(observation.get("source_observation_id") or ""),
                "candidate_id": str(observation.get("candidate_id") or ""),
                "status": "valid" if not observation_errors else "invalid",
                "errors": observation_errors,
                "proposed_artifact_verified": bool(observation.get("proposed_artifact_verified") is True),
                "proposed_gate_eligible": bool(observation.get("proposed_gate_eligible") is True),
            }
        )
        if observation_errors:
            invalid_count += 1
            errors.extend(f"observation[{index}]: {error}" for error in observation_errors)
        else:
            valid_count += 1

    report = {
        "schema_version": SOURCE_COLLECTION_SCHEMA_VERSION,
        "task_id": SOURCE_COLLECTION_TASK_ID,
        "status": "fail" if invalid_count else ("pass_with_warnings" if warnings else "pass"),
        "collection_id": _collection_id(collection_path),
        "collection_dir": str(collection_path),
        "observation_count": len(observations),
        "valid_observation_count": valid_count,
        "invalid_observation_count": invalid_count,
        "proposed_artifact_verified_count": sum(1 for item in observations if item.get("proposed_artifact_verified") is True),
        "proposed_gate_eligible_count": sum(1 for item in observations if item.get("proposed_gate_eligible") is True),
        "source_authority_counts": _counts(item.get("source_authority") for item in observations),
        "source_type_counts": _counts(item.get("source_type") for item in observations),
        "diagnostics": diagnostics,
        "errors": errors,
        "warnings": warnings,
        "truth_promotion_performed": False,
        "downloads_performed": False,
        "file_fetch_performed": False,
        "wayback_replay_performed": False,
        "live_network_used": any(item.get("live_network_used") is True for item in observations),
    }
    write_json(collection_path / SOURCE_COLLECTION_VALIDATION_REPORT_FILE, report)
    return report


def validate_source_observation(
    observation: Mapping[str, Any],
    *,
    candidate_by_id: Mapping[str, Mapping[str, Any]] | None = None,
) -> list[str]:
    errors: list[str] = []
    candidate_id = str(observation.get("candidate_id") or "").strip()
    artifact_title = str(observation.get("artifact_title") or "").strip()
    source_identifier = str(observation.get("source_url") or observation.get("source_identifier") or "").strip()
    source_authority = str(observation.get("source_authority") or "").strip().casefold()
    source_type = str(observation.get("source_type") or "").strip().casefold()
    access_method = str(observation.get("access_method") or "").strip().casefold()
    proposed_verified = observation.get("proposed_artifact_verified") is True
    proposed_gate = observation.get("proposed_gate_eligible") is True
    proposed_scope = str(observation.get("proposed_verification_scope") or "").strip().casefold()

    if not candidate_id:
        errors.append("candidate_id is required")
    if not str(observation.get("source_observation_id") or "").strip():
        errors.append("source_observation_id is required")
    if not artifact_title:
        errors.append("artifact_title is required")
    if not source_identifier:
        errors.append("source_url or source_identifier is required")
    if not str(observation.get("observer") or "").strip():
        errors.append("observer is required")
    if not _string_list(observation.get("observed_artifact_fields")):
        errors.append("observed_artifact_fields are required")
    if observation.get("downloaded_file") is True:
        errors.append("downloaded_file must be false")
    if observation.get("fetched_binary") is True:
        errors.append("fetched_binary must be false")
    if observation.get("file_fetch_performed") is True:
        errors.append("file_fetch_performed must be false")
    if observation.get("wayback_replay_used") is True:
        errors.append("wayback_replay_used must be false")
    if observation.get("no_download_performed") is not True:
        errors.append("no_download_performed must be true")
    if _looks_private_source_identifier(source_identifier):
        errors.append("source identifier must be public-safe and must not be a local/private path")
    if _contains_secret_marker(observation):
        errors.append("source observation must not contain tokens, secrets, passwords, or authorization markers")

    candidate = dict(candidate_by_id.get(candidate_id) or {}) if candidate_by_id else {}
    if candidate.get("artifact_gate_excluded") is True and candidate.get("source_collection_curation_target") is not True:
        errors.append(f"candidate is excluded from artifact gate work: {candidate.get('gate_exclusion_reason')}")
    text = _normalize(" ".join([artifact_title, str(observation.get("platform_or_context") or ""), json.dumps(observation.get("artifact_identity_fields") or {}, sort_keys=True)]))
    if "windows 7 apps" in text or artifact_title.casefold().strip() in {"windows 7 apps", "windows 7 app"}:
        errors.append("broad category cannot be source-observed as a concrete artifact")
    if "driver" in text and not _driver_hardware_fields(observation):
        errors.append("driver observation requires hardware identity fields")

    if proposed_verified and not proposed_gate:
        errors.append("proposed_artifact_verified true requires proposed_gate_eligible true")
    if proposed_gate and not str(observation.get("reviewer") or "").strip():
        errors.append("proposed gate eligibility requires reviewer")
    if proposed_gate and not str(observation.get("review_rationale") or "").strip():
        errors.append("proposed gate eligibility requires review_rationale")
    if proposed_verified:
        if proposed_scope in _INSUFFICIENT_VERIFICATION_SCOPES:
            errors.append("proposed artifact verification requires artifact_identity_metadata scope")
        if source_authority in {"", "unknown"}:
            errors.append("source_authority=unknown cannot propose artifact_verified")
        if source_type in _SOURCE_TYPES_INSUFFICIENT_FOR_VERIFIED:
            errors.append(f"source_type={source_type or 'unknown'} cannot by itself propose artifact_verified")
        if access_method in {"local_fixture", "repo_record"}:
            errors.append("local_fixture or repo_record observations cannot propose artifact_verified")
        if source_authority in {"archive_metadata", "archive_metadata_fixture", "hard_query_fixture", "local_reviewed_source_lead"}:
            errors.append("archive metadata, fixture, or local reviewed source lead cannot by itself propose artifact_verified")
    return _dedupe(errors)


def source_observations_to_evidence(collection_dir: str | Path, out_path: str | Path | None = None) -> dict[str, Any]:
    collection_path = Path(collection_dir)
    validation = validate_source_collection(collection_path)
    plan_rows = _source_plan_rows(collection_path)
    candidate_by_id = {str(item.get("candidate_id") or ""): dict(item) for item in plan_rows}
    observations = read_jsonl(collection_path / SOURCE_COLLECTION_OBSERVATIONS_FILE) if (collection_path / SOURCE_COLLECTION_OBSERVATIONS_FILE).is_file() else []
    valid_ids = {
        str(item.get("source_observation_id") or "")
        for item in validation.get("diagnostics") or []
        if isinstance(item, Mapping) and item.get("status") == "valid"
    }
    valid_observations = [
        dict(item)
        for item in observations
        if str(item.get("source_observation_id") or "") in valid_ids
    ]
    grouped: dict[str, list[dict[str, Any]]] = {}
    for observation in valid_observations:
        grouped.setdefault(str(observation.get("candidate_id") or ""), []).append(observation)

    packets = []
    for candidate_id in sorted(grouped):
        candidate = candidate_by_id.get(candidate_id)
        if not candidate:
            continue
        packets.append(_manual_packet_from_source_observations(candidate, grouped[candidate_id], collection_path=collection_path))

    destination = Path(out_path) if out_path else collection_path / SOURCE_COLLECTION_EVIDENCE_FILE
    write_jsonl(destination, packets)
    status = "pass" if packets and not validation.get("errors") else "pass_with_warnings"
    return {
        "schema_version": SOURCE_COLLECTION_SCHEMA_VERSION,
        "task_id": SOURCE_COLLECTION_TASK_ID,
        "status": status,
        "collection_id": _collection_id(collection_path),
        "collection_dir": str(collection_path),
        "out": str(destination),
        "source_observation_count": len(observations),
        "valid_observation_count": len(valid_observations),
        "evidence_packet_count": len(packets),
        "artifact_verified_packet_count": sum(1 for packet in packets if packet.get("artifact_verified") is True),
        "gate_eligible_packet_count": sum(1 for packet in packets if packet.get("gate_eligible") is True),
        "errors": list(validation.get("errors") or []),
        "warnings": list(validation.get("warnings") or []),
    }


def write_source_collection_report(collection_dir: str | Path, out_path: str | Path | None = None) -> dict[str, Any]:
    collection_path = Path(collection_dir)
    validation = validate_source_collection(collection_path)
    plan_rows = _source_plan_rows(collection_path)
    evidence_path = collection_path / SOURCE_COLLECTION_EVIDENCE_FILE
    packets = read_jsonl(evidence_path) if evidence_path.is_file() else []
    report = _source_collection_report(collection_path, plan_rows=plan_rows, packets=packets, validation=validation)
    destination = Path(out_path) if out_path else collection_path / SOURCE_COLLECTION_REPORT_FILE
    write_json(destination, report)
    write_json(collection_path / SOURCE_COLLECTION_REPORT_FILE, report)
    (collection_path / SOURCE_COLLECTION_REPORT_MD).write_text(render_source_collection_markdown(report), encoding="utf-8")
    return report


def source_collection_status(collection_dir: str | Path) -> dict[str, Any]:
    collection_path = Path(collection_dir)
    report_path = collection_path / SOURCE_COLLECTION_REPORT_FILE
    validation_path = collection_path / SOURCE_COLLECTION_VALIDATION_REPORT_FILE
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {}
    validation = json.loads(validation_path.read_text(encoding="utf-8")) if validation_path.is_file() else validate_source_collection(collection_path)
    return {
        "schema_version": SOURCE_COLLECTION_SCHEMA_VERSION,
        "task_id": SOURCE_COLLECTION_TASK_ID,
        "status": "pass" if report_path.is_file() else "pass_with_warnings",
        "collection_id": _collection_id(collection_path),
        "collection_dir": str(collection_path),
        "report_status": report.get("status", "PASS_WITH_WARNINGS"),
        "collection_status": report.get("collection_status", "blocked"),
        "candidate_count": report.get("candidate_count", 0),
        "selected_candidate_count": report.get("selected_candidate_count", 0),
        "observation_count": validation.get("observation_count", report.get("observation_count", 0)),
        "valid_observation_count": validation.get("valid_observation_count", report.get("valid_observation_count", 0)),
        "invalid_observation_count": validation.get("invalid_observation_count", report.get("invalid_observation_count", 0)),
        "evidence_packet_count": report.get("evidence_packet_count", 0),
        "artifact_verified_packet_count": report.get("artifact_verified_packet_count", 0),
        "gate_eligible_packet_count": report.get("gate_eligible_packet_count", 0),
        "blockers": report.get("blockers", []),
        "warnings": [*list(report.get("warnings") or []), *list(validation.get("warnings") or [])],
        "next_recommended_task": report.get("next_recommended_task", "SOURCE-OBSERVATION-BATCH-01"),
    }


def render_source_collection_status(payload: Mapping[str, Any]) -> str:
    lines = [
        f"collection status: {payload.get('status')}",
        f"report status: {payload.get('report_status')}",
        f"collection gate status: {payload.get('collection_status')}",
        f"collection id: {payload.get('collection_id')}",
        f"candidate count: {payload.get('candidate_count')}",
        f"selected candidates: {payload.get('selected_candidate_count')}",
        f"observations: {payload.get('observation_count')}",
        f"valid observations: {payload.get('valid_observation_count')}",
        f"invalid observations: {payload.get('invalid_observation_count')}",
        f"evidence packets: {payload.get('evidence_packet_count')}",
        f"artifact verified packets: {payload.get('artifact_verified_packet_count')}",
        f"gate eligible packets: {payload.get('gate_eligible_packet_count')}",
        f"next recommended task: {payload.get('next_recommended_task')}",
        "blockers:",
    ]
    blockers = [item for item in payload.get("blockers") or [] if isinstance(item, Mapping)]
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker.get('id')}: {blocker.get('message')}")
    else:
        lines.append("- none")
    warnings = payload.get("warnings") or []
    if warnings:
        lines.append("warnings:")
        for warning in warnings:
            lines.append(f"- {warning}")
    return "\n".join(lines) + "\n"


def render_gate_markdown(report: Mapping[str, Any]) -> str:
    blockers = [item for item in report.get("blockers") or [] if isinstance(item, Mapping)]
    lines = [
        "# Reviewed Artifact Gate Seed Report",
        "",
        "## Summary",
        "",
        f"- Status: {report.get('status')}",
        f"- Gate status: {report.get('gate_status')}",
        f"- Reviewed artifact gate count: {report.get('reviewed_artifact_gate_count')}/{report.get('gate_target_reviewed_artifacts')}",
        f"- Artifact verified count: {report.get('artifact_verified_count')}",
        f"- Evidence packets: {report.get('evidence_packet_count')}",
        f"- Next recommended task: {report.get('next_recommended_task')}",
        "",
        "This report seeds manual artifact evidence collection. It does not verify artifacts, fetch files, or update official gate counts.",
        "",
        "## Blockers",
        "",
    ]
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker.get('id')}: {blocker.get('message')}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Safety",
            "",
            f"- Truth promotion performed: {str(report.get('truth_promotion_performed')).lower()}",
            f"- Downloads performed: {str(report.get('downloads_performed')).lower()}",
            f"- File fetch performed: {str(report.get('file_fetch_performed')).lower()}",
            f"- Live network used: {str(report.get('live_network_used')).lower()}",
            f"- Public index mutated: {str(report.get('public_index_mutated')).lower()}",
            f"- Master index mutated: {str(report.get('master_index_mutated')).lower()}",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_status(payload: Mapping[str, Any]) -> str:
    lines = [
        f"gate status: {payload.get('gate_status')}",
        f"report status: {payload.get('report_status')}",
        f"candidate count: {payload.get('candidate_count')}",
        f"evidence packets: {payload.get('evidence_packet_count')}",
        f"reviewed artifact records: {payload.get('reviewed_artifact_record_count')}",
        f"reviewed artifact gate count: {payload.get('reviewed_artifact_gate_count')}/{payload.get('gate_target_reviewed_artifacts')}",
        f"artifact verified count: {payload.get('artifact_verified_count')}",
        f"next recommended task: {payload.get('next_recommended_task')}",
        "blockers:",
    ]
    blockers = [item for item in payload.get("blockers") or [] if isinstance(item, Mapping)]
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker.get('id')}: {blocker.get('message')}")
    else:
        lines.append("- none")
    errors = payload.get("errors") or []
    if errors:
        lines.append("errors:")
        for error in errors:
            lines.append(f"- {error}")
    return "\n".join(lines) + "\n"


def write_jsonl(path: str | Path, rows: Sequence[Mapping[str, Any]]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(dict(row), sort_keys=True, ensure_ascii=True) for row in rows]
    destination.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{source}:{line_number}: invalid JSONL row: {exc.msg}") from exc
        if not isinstance(value, Mapping):
            raise ValueError(f"{source}:{line_number}: JSONL row must be an object")
        rows.append(dict(value))
    return rows


def write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(dict(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def _load_valid_index(index_path: str | Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    index = load_index(index_path)
    errors = validate_index(index)
    if errors:
        raise ValueError("; ".join(errors))
    documents = index.get("documents")
    if not isinstance(documents, list):
        raise ValueError("index documents must be a list")
    return index, [dict(item) for item in documents if isinstance(item, Mapping)]


def _candidate_from_document(document: Mapping[str, Any], *, index_path: str) -> dict[str, Any]:
    doc_id = str(document.get("id") or "")
    matched_queries = _string_list(document.get("matched_queries")) or _string_list(document.get("query_hints"))
    query_key = _best_query_key(document)
    excluded, exclusion_reason, candidate_reason = _candidate_posture(document, query_key)
    source_observations = _source_observations(document)
    source_family = str(document.get("source_family") or "unknown")
    provenance = dict(document.get("provenance") or {})
    source_authority = _source_authority(document)
    return {
        "schema_version": CANDIDATE_SCHEMA_VERSION,
        "candidate_id": _stable_id("artifact-gate-candidate", doc_id),
        "source_index_document_id": doc_id,
        "source_index_path": index_path,
        "title": str(document.get("title") or ""),
        "summary": str(document.get("summary") or ""),
        "status": str(document.get("status") or "unknown"),
        "review_state": str(document.get("review_state") or "unreviewed"),
        "record_state": str(document.get("record_state") or ""),
        "reviewed_record_id": str(document.get("reviewed_record_id") or ""),
        "review_event_id": str(document.get("review_event_id") or ""),
        "query_hints": _string_list(document.get("query_hints")),
        "matched_queries": matched_queries,
        "artifact_type": _artifact_type(document),
        "platform_or_context": _platform_or_context(document, query_key),
        "source_family": source_family,
        "source_authority": source_authority,
        "source_hints": _string_list(document.get("source_hints")),
        "evidence_hints": _string_list(document.get("evidence_hints")),
        "source_observations": source_observations,
        "missing_information": _string_list(document.get("missing_information")),
        "safe_next_action": str(document.get("safe_next_action") or "collect manual artifact evidence"),
        "non_verified_reason": str(document.get("non_verified_reason") or "not verified artifact evidence"),
        "provenance": provenance,
        "artifact_verified": False,
        "gate_eligible": False,
        "artifact_gate_excluded": excluded,
        "gate_exclusion_reason": exclusion_reason,
        "artifact_gate_candidate_reason": candidate_reason,
        "verification_scope": "source_lead_only",
        "manual_evidence_required": True,
        "no_download_performed": True,
        "file_fetch_performed": False,
        "live_network_used": False,
    }


def _candidate_posture(document: Mapping[str, Any], query_key: str) -> tuple[bool, str, str]:
    status = str(document.get("status") or "unknown")
    haystack = " ".join(
        [
            query_key,
            str(document.get("title") or ""),
            str(document.get("summary") or ""),
            " ".join(_string_list(document.get("matched_queries"))),
            " ".join(_string_list(document.get("query_hints"))),
        ]
    ).casefold()
    if "driver for win98" in haystack:
        return True, "hardware_details_missing", "driver query lacks hardware identity needed for artifact evidence"
    if "windows 7 apps" in haystack:
        return True, "broad_collection_query", "broad app collection query is not a specific artifact identity"
    if status == "policy_blocked":
        return True, "policy_blocked_without_safe_evidence", "policy-blocked state is not a gate seed"
    if status == "unavailable":
        return True, "unavailable_record", "unavailable state cannot seed artifact verification"
    if status == "need":
        return True, "needs_more_identity_or_source_evidence", "need state lacks enough artifact/source identity"
    if status == "near_miss":
        return True, "near_miss_needs_disambiguation", "near miss requires disambiguation before artifact-gate work"
    if not str(document.get("title") or "").strip():
        return True, "missing_artifact_title", "candidate is missing an artifact title"
    if not _string_list(document.get("source_hints")) and not _string_list(document.get("evidence_hints")):
        return True, "missing_source_or_evidence_hints", "candidate is missing source/evidence hints"
    return False, "manual_external_evidence_required", "candidate can seed manual artifact evidence collection"


def _evidence_packet_from_candidate(candidate: Mapping[str, Any], *, template: bool) -> dict[str, Any]:
    candidate_id = str(candidate.get("candidate_id") or "")
    rationale = "" if template else "Generated non-verified artifact gate seed; manual external evidence is still required."
    reviewer = "" if template else "artifact_gate_seed"
    return {
        "schema_version": EVIDENCE_PACKET_SCHEMA_VERSION,
        "evidence_packet_id": _stable_id("artifact-gate-evidence", candidate_id),
        "candidate_id": candidate_id,
        "source_index_document_id": str(candidate.get("source_index_document_id") or ""),
        "artifact_title": str(candidate.get("title") or ""),
        "artifact_type": str(candidate.get("artifact_type") or "unknown"),
        "platform_or_context": str(candidate.get("platform_or_context") or ""),
        "artifact_identity_fields": {
            "title": str(candidate.get("title") or ""),
            "source_index_document_id": str(candidate.get("source_index_document_id") or ""),
            "reviewed_record_id": str(candidate.get("reviewed_record_id") or ""),
            "platform_or_context": str(candidate.get("platform_or_context") or ""),
        },
        "source_observations": _object_list(candidate.get("source_observations")),
        "source_hints": _string_list(candidate.get("source_hints")),
        "evidence_hints": _string_list(candidate.get("evidence_hints")),
        "evidence_urls": [item for item in _string_list(candidate.get("source_hints")) if item.startswith("http://") or item.startswith("https://")],
        "evidence_type": "source_metadata_lead",
        "source_authority": str(candidate.get("source_authority") or "local_source_lead"),
        "observed_fields": ["title", "source_hints", "evidence_hints", "provenance"],
        "reviewer": reviewer,
        "review_rationale": rationale,
        "no_download_performed": True,
        "file_fetch_performed": False,
        "binary_verified": False,
        "download_safe": False,
        "execution_safe": False,
        "rights_cleared": False,
        "verification_scope": "source_lead_only",
        "artifact_verified": False,
        "gate_eligible": False,
        "artifact_gate_excluded": bool(candidate.get("artifact_gate_excluded") is True),
        "gate_exclusion_reason": str(candidate.get("gate_exclusion_reason") or "manual_external_evidence_required"),
        "non_verified_reason": "source lead only; not verified artifact evidence",
        "provenance": dict(candidate.get("provenance") or {}),
        "live_network_used": False,
        "template": bool(template),
    }


def _manual_template_from_candidate(candidate: Mapping[str, Any], *, batch_id: str) -> dict[str, Any]:
    packet = _evidence_packet_from_candidate(candidate, template=True)
    packet.update(
        {
            "batch_id": batch_id,
            "collected_at": "",
            "observed_at": "",
            "source_identifiers": [],
            "source_observations": [
                {
                    **observation,
                    "source_id": str(observation.get("observation_id") or ""),
                    "source_identifier": str(observation.get("value") or ""),
                    "source_title": "",
                    "publisher_or_source_name": "",
                    "observed_artifact_fields": [],
                    "authority_classification": "",
                    "observation_notes": "",
                    "access_method": "manual_page_observation",
                    "live_network_used": False,
                    "downloaded_file": False,
                    "fetched_binary": False,
                }
                for observation in _object_list(packet.get("source_observations"))
            ],
            "verification_scope": "artifact_identity_candidate",
            "source_authority": "",
            "gate_exclusion_reason": "manual_evidence_not_collected",
            "manual_instructions": [
                "record only page/catalog/release/support metadata observations",
                "do not download binaries or fetch files",
                "set artifact_verified true only when explicit gate criteria are met",
            ],
        }
    )
    return packet


def _manual_packets(batch_path: Path) -> list[dict[str, Any]]:
    evidence_path = batch_path / MANUAL_BATCH_EVIDENCE_FILE
    return read_jsonl(evidence_path) if evidence_path.is_file() else []


def _manual_artifact_verified_errors(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    authority = str(packet.get("source_authority") or "").strip().casefold()
    scope = str(packet.get("verification_scope") or "").strip().casefold()
    observations = _object_list(packet.get("source_observations"))
    if scope in _INSUFFICIENT_VERIFICATION_SCOPES:
        errors.append("artifact_verified evidence requires verification_scope such as artifact_identity_metadata")
    if authority not in _APPROVED_ARTIFACT_AUTHORITIES:
        errors.append("artifact_verified evidence requires an approved source_authority")
    if not observations:
        errors.append("artifact_verified evidence requires source_observations")
    if _evidence_source_is_fixture_only(packet):
        errors.append("fixture-only or metadata-only evidence cannot be artifact_verified")
    external_observations = []
    for observation in observations:
        access_method = str(observation.get("access_method") or "").strip().casefold()
        if access_method not in {"local_fixture", "repo_record"}:
            external_observations.append(observation)
    if not external_observations:
        errors.append("artifact_verified evidence requires at least one stable external observation")
    if authority in {"stable_archive_plus_independent_corroboration", "independent_reputable_corroboration"} and len(external_observations) < 2:
        errors.append("corroborated source_authority requires at least two external observations")
    return errors


def _reviewed_record_from_manual_packet(packet: Mapping[str, Any], *, reviewer: str) -> dict[str, Any]:
    packet_id = str(packet.get("evidence_packet_id") or "")
    return {
        "schema_version": REVIEWED_ARTIFACT_RECORD_SCHEMA_VERSION,
        "reviewed_artifact_record_id": _stable_id("reviewed-artifact-gate-record", packet_id),
        "source_candidate_id": str(packet.get("candidate_id") or ""),
        "source_index_document_id": str(packet.get("source_index_document_id") or ""),
        "source_evidence_packet_id": packet_id,
        "dedupe_identity_key": _manual_packet_identity_key(packet),
        "batch_id": str(packet.get("batch_id") or ""),
        "title": str(packet.get("artifact_title") or ""),
        "artifact_type": str(packet.get("artifact_type") or ""),
        "platform_or_context": str(packet.get("platform_or_context") or ""),
        "artifact_identity_fields": dict(packet.get("artifact_identity_fields") or {}),
        "status": "verified",
        "review_state": "accepted_artifact_identity",
        "artifact_verified": True,
        "accepted_truth": False,
        "gate_eligible": True,
        "gate_exclusion_reason": "",
        "verification_scope": str(packet.get("verification_scope") or "artifact_identity_metadata"),
        "source_authority": str(packet.get("source_authority") or ""),
        "evidence_type": str(packet.get("evidence_type") or ""),
        "reviewer": str(reviewer or packet.get("reviewer") or ""),
        "review_rationale": str(packet.get("review_rationale") or ""),
        "source_observations": _object_list(packet.get("source_observations")),
        "evidence_urls": _string_list(packet.get("evidence_urls")),
        "source_identifiers": _string_list(packet.get("source_identifiers")),
        "observed_fields": _string_list(packet.get("observed_fields")),
        "binary_verified": False,
        "download_safe": False,
        "execution_safe": False,
        "rights_cleared": False,
        "no_download_performed": True,
        "file_fetch_performed": False,
        "live_network_used": bool(packet.get("live_network_used") is True),
        "provenance": {
            "source": "manual_artifact_evidence_batch",
            "source_kind": "manual_artifact_evidence",
            "source_evidence_packet_id": packet_id,
            "source_candidate_id": str(packet.get("candidate_id") or ""),
        },
        "non_verified_reason": "",
    }


def _manual_packet_identity_key(packet: Mapping[str, Any]) -> str:
    identity = packet.get("artifact_identity_fields") if isinstance(packet.get("artifact_identity_fields"), Mapping) else {}
    title = _first_text(identity.get("title"), identity.get("artifact_title"), packet.get("artifact_title"), packet.get("title"))
    artifact_type = _first_text(identity.get("artifact_type"), packet.get("artifact_type"))
    platform = _first_text(identity.get("platform_or_context"), packet.get("platform_or_context"))
    scope = _first_text(packet.get("verification_scope"), default="artifact_identity_metadata")
    product = _first_text(identity.get("product"))
    version = _first_text(identity.get("version"))
    release_date = _first_text(identity.get("release_date"))
    parts = [title, artifact_type, platform, product, version, release_date, scope]
    return "|".join(_normalize(part) for part in parts if str(part or "").strip())


def _source_collection_duplicate_info(candidate: Mapping[str, Any], reviewed_records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    candidate_id = str(candidate.get("candidate_id") or "")
    source_index_document_id = str(candidate.get("source_index_document_id") or "")
    candidate_text = _normalize(
        " ".join(
            [
                str(candidate.get("title") or ""),
                str(candidate.get("artifact_type") or ""),
                str(candidate.get("platform_or_context") or ""),
                " ".join(_string_list(candidate.get("matched_queries"))),
                " ".join(_string_list(candidate.get("query_hints"))),
                source_index_document_id,
            ]
        )
    )
    for record in reviewed_records:
        record_id = str(record.get("reviewed_artifact_record_id") or "")
        record_title = str(record.get("title") or "")
        record_text = _normalize(
            " ".join(
                [
                    record_title,
                    str(record.get("artifact_type") or ""),
                    str(record.get("platform_or_context") or ""),
                    str(record.get("source_candidate_id") or ""),
                    str(record.get("source_index_document_id") or ""),
                    str(record.get("dedupe_identity_key") or ""),
                ]
            )
        )
        if candidate_id and candidate_id == str(record.get("source_candidate_id") or ""):
            return _duplicate_info(record_id, record_title, "candidate_id already counted")
        if source_index_document_id and source_index_document_id == str(record.get("source_index_document_id") or ""):
            return _duplicate_info(record_id, record_title, "source index document already counted")
        if record_title and _normalize(str(candidate.get("title") or "")) == _normalize(record_title):
            if str(candidate.get("artifact_type") or "").strip().casefold() == str(record.get("artifact_type") or "").strip().casefold():
                return _duplicate_info(record_id, record_title, "artifact title and type already counted")
        if "firefox" in candidate_text and "firefox" in record_text:
            return _duplicate_info(record_id, record_title, "Firefox artifact identity already counted")
        candidate_is_sound_blaster_manual = (
            str(candidate.get("artifact_type") or "").strip().casefold() == "manual"
            and ("ct1740" in candidate_text or "sound blaster" in candidate_text)
        )
        record_is_sound_blaster_manual = "manual" in record_text and ("ct1740" in record_text or "sound blaster" in record_text)
        if candidate_is_sound_blaster_manual and record_is_sound_blaster_manual:
            return _duplicate_info(record_id, record_title, "Sound Blaster manual artifact identity already counted")
    return {
        "is_duplicate": False,
        "duplicate_of": "",
        "duplicate_identity": "",
        "duplicate_reason": "",
    }


def _source_collection_selectable_candidates(candidates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        dict(item)
        for item in candidates
        if item.get("source_collection_duplicate") is not True
        and (item.get("artifact_gate_excluded") is not True or item.get("source_collection_curation_target") is True)
    ]


def _curated_source_collection_candidates(reviewed_records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    curated: list[dict[str, Any]] = []
    for position, template in enumerate(_CURATED_SOURCE_COLLECTION_TARGETS, start=1):
        candidate = dict(template)
        duplicate = _source_collection_duplicate_info(candidate, reviewed_records)
        candidate.update(
            {
                "curated_source_collection_target": True,
                "source_collection_duplicate": duplicate["is_duplicate"],
                "source_collection_duplicate_of": duplicate["duplicate_of"],
                "source_collection_duplicate_identity": duplicate["duplicate_identity"],
                "source_collection_duplicate_reason": duplicate["duplicate_reason"],
                "source_collection_curation_target": duplicate["is_duplicate"] is not True,
                "curated_source_collection_position": position,
            }
        )
        curated.append(candidate)
    return curated


def _duplicate_info(record_id: str, title: str, reason: str) -> dict[str, Any]:
    return {
        "is_duplicate": True,
        "duplicate_of": record_id,
        "duplicate_identity": title,
        "duplicate_reason": reason,
    }


def _source_collection_curation_target(candidate: Mapping[str, Any], duplicate: Mapping[str, Any]) -> bool:
    if duplicate.get("is_duplicate") is True:
        return False
    reason = str(candidate.get("gate_exclusion_reason") or "").strip().casefold()
    if reason not in _SOURCE_COLLECTION_CURATABLE_EXCLUSION_REASONS:
        return False
    text = _normalize(" ".join([str(candidate.get("title") or ""), " ".join(_string_list(candidate.get("matched_queries")))]))
    if "windows 7 apps" in text or "driver for win98" in text:
        return False
    return True


def _expected_source_fields(candidate: Mapping[str, Any]) -> list[str]:
    artifact_type = str(candidate.get("artifact_type") or "").strip().casefold()
    if artifact_type == "article":
        return ["article_title", "publication_title", "issue_or_date", "volume_or_issue", "page_range", "publisher_or_record_id"]
    if artifact_type == "software":
        return ["product", "version", "publisher", "release_date", "platform_or_context"]
    if artifact_type == "driver":
        return ["vendor", "device_model", "driver_package", "supported_os", "source_record_id"]
    if artifact_type == "manual":
        return ["manual_title", "publisher", "publication_date", "model_or_product", "source_record_id"]
    return ["title", "artifact_type", "platform_or_context", "source_record_id"]


def _manual_batch_report(
    batch_path: Path,
    *,
    candidate_plan: Sequence[Mapping[str, Any]],
    packets: Sequence[Mapping[str, Any]],
    records: Sequence[Mapping[str, Any]],
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    artifact_verified_count = sum(1 for record in records if record.get("artifact_verified") is True)
    gate_eligible_count = sum(1 for record in records if record.get("gate_eligible") is True)
    gate_count = sum(1 for record in records if record.get("artifact_verified") is True and record.get("gate_eligible") is True)
    invalid_count = int(validation.get("invalid_evidence_packet_count") or 0)
    blockers = []
    if gate_count < DEFAULT_GATE_TARGET:
        blockers.append(
            {
                "id": "reviewed_artifact_gate_count_below_target",
                "status": "blocked",
                "message": f"reviewed artifact gate count is {gate_count}/{DEFAULT_GATE_TARGET}",
            }
        )
    if not packets:
        blockers.append(
            {
                "id": "manual_evidence_packets_missing",
                "status": "blocked",
                "message": "manual evidence packets have not been supplied",
            }
        )
    if invalid_count:
        blockers.append(
            {
                "id": "manual_evidence_packets_invalid",
                "status": "blocked",
                "message": f"{invalid_count} manual evidence packet(s) failed validation",
            }
        )
    if artifact_verified_count == 0:
        blockers.append(
            {
                "id": "artifact_verified_count_zero",
                "status": "blocked",
                "message": "no artifact-verified manual evidence records were materialized",
            }
        )
    status = "PASS" if not blockers else "PASS_WITH_WARNINGS"
    gate_status = "pass" if gate_count >= DEFAULT_GATE_TARGET else "blocked"
    warnings = [
        "manual evidence batch artifacts are generated operational artifacts",
        "artifact_verified does not imply binary, download, execution, or rights safety",
    ]
    if not packets:
        warnings.append("no manual evidence packets were supplied; report is a blocked template/report")
    if invalid_count:
        warnings.append("invalid manual evidence packets were rejected and not materialized")
    return {
        "schema_version": MANUAL_BATCH_SCHEMA_VERSION,
        "task_id": MANUAL_BATCH_TASK_ID,
        "status": status,
        "gate_status": gate_status,
        "batch_id": _batch_id(batch_path),
        "batch_dir": str(batch_path),
        "candidate_count": len(candidate_plan),
        "selected_candidate_count": sum(1 for item in candidate_plan if item.get("manual_batch_selected") is True),
        "evidence_packet_count": len(packets),
        "valid_evidence_packet_count": int(validation.get("valid_evidence_packet_count") or 0),
        "invalid_evidence_packet_count": invalid_count,
        "reviewed_artifact_gate_count": gate_count,
        "official_reviewed_artifact_count": gate_count,
        "artifact_verified_count": artifact_verified_count,
        "gate_eligible_count": gate_eligible_count,
        "gate_target_reviewed_artifacts": DEFAULT_GATE_TARGET,
        "official_reviewed_artifact_gate_target": DEFAULT_GATE_TARGET,
        "reviewed_artifact_record_count": len(records),
        "verification_scope_counts": _counts(record.get("verification_scope") for record in records),
        "source_authority_counts": _counts(packet.get("source_authority") for packet in packets),
        "exclusion_counts": _counts(
            [
                *(packet.get("gate_exclusion_reason") for packet in packets if packet.get("gate_eligible") is not True),
                *(item.get("gate_exclusion_reason") for item in candidate_plan if item.get("artifact_gate_excluded") is True),
            ]
        ),
        "validation_errors": list(validation.get("errors") or []),
        "validation_warnings": list(validation.get("warnings") or []),
        "blockers": blockers,
        "warnings": warnings,
        "truth_promotion_performed": False,
        "verified_artifact_truth_created": artifact_verified_count > 0,
        "downloads_performed": False,
        "file_fetch_performed": False,
        "wayback_replay_performed": False,
        "live_network_used": any(packet.get("live_network_used") is True for packet in packets),
        "public_index_mutated": False,
        "master_index_mutated": False,
        "official_gate_counts_mutated": False,
        "generated_at": "1970-01-01T00:00:00Z",
        "next_recommended_task": (
            "MANUAL-ARTIFACT-EVIDENCE-BATCH-02"
            if artifact_verified_count > 0 and gate_count < DEFAULT_GATE_TARGET
            else "SOURCE-OBSERVATION-BATCH-01"
        ),
    }


def render_manual_batch_markdown(report: Mapping[str, Any]) -> str:
    blockers = [item for item in report.get("blockers") or [] if isinstance(item, Mapping)]
    lines = [
        "# Manual Artifact Evidence Batch Report",
        "",
        "## Summary",
        "",
        f"- Status: {report.get('status')}",
        f"- Gate status: {report.get('gate_status')}",
        f"- Batch: {report.get('batch_id')}",
        f"- Evidence packets: {report.get('evidence_packet_count')}",
        f"- Valid packets: {report.get('valid_evidence_packet_count')}",
        f"- Invalid packets: {report.get('invalid_evidence_packet_count')}",
        f"- Reviewed artifact gate count: {report.get('reviewed_artifact_gate_count')}/{report.get('gate_target_reviewed_artifacts')}",
        f"- Artifact verified count: {report.get('artifact_verified_count')}",
        f"- Next recommended task: {report.get('next_recommended_task')}",
        "",
        "Artifact identity verification does not imply binary safety, download safety, execution safety, or rights clearance.",
        "",
        "## Blockers",
        "",
    ]
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker.get('id')}: {blocker.get('message')}")
    else:
        lines.append("- none")
    lines.extend(["", "## Validation", ""])
    for error in report.get("validation_errors") or []:
        lines.append(f"- error: {error}")
    for warning in report.get("validation_warnings") or []:
        lines.append(f"- warning: {warning}")
    if not report.get("validation_errors") and not report.get("validation_warnings"):
        lines.append("- no validation errors")
    return "\n".join(lines).rstrip() + "\n"


def render_source_collection_markdown(report: Mapping[str, Any]) -> str:
    blockers = [item for item in report.get("blockers") or [] if isinstance(item, Mapping)]
    lines = [
        "# Artifact Evidence Source Collection Report",
        "",
        "## Summary",
        "",
        f"- Status: {report.get('status')}",
        f"- Collection status: {report.get('collection_status')}",
        f"- Collection: {report.get('collection_id')}",
        f"- Selected candidates: {report.get('selected_candidate_count')}",
        f"- Source observations: {report.get('observation_count')}",
        f"- Valid observations: {report.get('valid_observation_count')}",
        f"- Invalid observations: {report.get('invalid_observation_count')}",
        f"- Source-derived evidence packets: {report.get('evidence_packet_count')}",
        f"- Artifact verified packets: {report.get('artifact_verified_packet_count')}",
        f"- Gate eligible packets: {report.get('gate_eligible_packet_count')}",
        f"- Next recommended task: {report.get('next_recommended_task')}",
        "",
        "Source observations are evidence inputs only. They do not imply binary safety, download safety, execution safety, or rights clearance.",
        "",
        "## Blockers",
        "",
    ]
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker.get('id')}: {blocker.get('message')}")
    else:
        lines.append("- none")
    lines.extend(["", "## Validation", ""])
    for error in report.get("validation_errors") or []:
        lines.append(f"- error: {error}")
    for warning in report.get("validation_warnings") or []:
        lines.append(f"- warning: {warning}")
    if not report.get("validation_errors") and not report.get("validation_warnings"):
        lines.append("- no validation errors")
    return "\n".join(lines).rstrip() + "\n"


def _source_collection_report(
    collection_path: Path,
    *,
    plan_rows: Sequence[Mapping[str, Any]],
    packets: Sequence[Mapping[str, Any]],
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    artifact_verified_count = sum(1 for packet in packets if packet.get("artifact_verified") is True)
    gate_eligible_count = sum(1 for packet in packets if packet.get("gate_eligible") is True)
    valid_count = int(validation.get("valid_observation_count") or 0)
    invalid_count = int(validation.get("invalid_observation_count") or 0)
    blockers = []
    if valid_count == 0:
        blockers.append(
            {
                "id": "source_observations_missing",
                "status": "blocked",
                "message": "no valid source observations have been supplied",
            }
        )
    if invalid_count:
        blockers.append(
            {
                "id": "source_observations_invalid",
                "status": "blocked",
                "message": f"{invalid_count} source observation(s) failed validation",
            }
        )
    if not packets:
        blockers.append(
            {
                "id": "source_derived_evidence_missing",
                "status": "blocked",
                "message": "no source-derived manual evidence packets were created",
            }
        )
    if artifact_verified_count == 0:
        blockers.append(
            {
                "id": "artifact_verified_count_zero",
                "status": "blocked",
                "message": "no artifact-verified source-derived evidence packets exist",
            }
        )
    warnings = [
        "source collection artifacts are generated operational artifacts",
        "fixture and IA metadata observations cannot verify artifacts by themselves",
        "artifact identity verification does not imply binary, download, execution, or rights safety",
    ]
    if valid_count == 0:
        warnings.append("fill source_observations.jsonl before expecting evidence packets")
    if invalid_count:
        warnings.append("invalid source observations were rejected and not converted")
    collection_status = "ready_for_manual_ingest" if packets else "blocked"
    status = "PASS" if not blockers else "PASS_WITH_WARNINGS"
    manifest = _source_collection_manifest(collection_path)
    return {
        "schema_version": SOURCE_COLLECTION_SCHEMA_VERSION,
        "task_id": SOURCE_COLLECTION_TASK_ID,
        "status": status,
        "collection_status": collection_status,
        "collection_id": _collection_id(collection_path),
        "collection_dir": str(collection_path),
        "manual_batch_dir": str(manifest.get("manual_batch_dir") or ""),
        "manual_batch_id": str(manifest.get("manual_batch_id") or ""),
        "candidate_count": len(plan_rows),
        "selected_candidate_count": sum(1 for item in plan_rows if item.get("source_collection_selected") is True),
        "excluded_candidate_count": sum(1 for item in plan_rows if item.get("artifact_gate_excluded") is True),
        "observation_count": int(validation.get("observation_count") or 0),
        "valid_observation_count": valid_count,
        "invalid_observation_count": invalid_count,
        "evidence_packet_count": len(packets),
        "artifact_verified_packet_count": artifact_verified_count,
        "gate_eligible_packet_count": gate_eligible_count,
        "source_authority_counts": _counts(packet.get("source_authority") for packet in packets),
        "verification_scope_counts": _counts(packet.get("verification_scope") for packet in packets),
        "validation_errors": list(validation.get("errors") or []),
        "validation_warnings": list(validation.get("warnings") or []),
        "blockers": blockers,
        "warnings": warnings,
        "truth_promotion_performed": False,
        "verified_artifact_truth_created": artifact_verified_count > 0,
        "downloads_performed": False,
        "file_fetch_performed": False,
        "wayback_replay_performed": False,
        "live_network_used": bool(validation.get("live_network_used") is True),
        "public_index_mutated": False,
        "master_index_mutated": False,
        "official_gate_counts_mutated": False,
        "generated_at": "1970-01-01T00:00:00Z",
        "next_recommended_task": (
            "MANUAL-ARTIFACT-EVIDENCE-BATCH-02"
            if artifact_verified_count > 0
            else "SOURCE-OBSERVATION-BATCH-01"
        ),
    }


def _source_plan_rows(collection_path: Path) -> list[dict[str, Any]]:
    plan_path = collection_path / SOURCE_COLLECTION_CANDIDATE_PLAN_FILE
    return read_jsonl(plan_path) if plan_path.is_file() else []


def _source_collection_manifest(collection_path: Path) -> dict[str, Any]:
    manifest_path = collection_path / SOURCE_COLLECTION_MANIFEST_FILE
    if not manifest_path.is_file():
        return {}
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _source_observation_template_from_candidate(candidate: Mapping[str, Any], *, collection_id: str) -> dict[str, Any]:
    candidate_id = str(candidate.get("candidate_id") or "")
    return {
        "schema_version": SOURCE_OBSERVATION_SCHEMA_VERSION,
        "source_observation_id": _stable_id("source-observation-packet", collection_id, candidate_id),
        "collection_id": collection_id,
        "candidate_id": candidate_id,
        "artifact_title": str(candidate.get("title") or ""),
        "artifact_type": str(candidate.get("artifact_type") or "unknown"),
        "artifact_identity_fields": {
            "title": str(candidate.get("title") or ""),
            "source_index_document_id": str(candidate.get("source_index_document_id") or ""),
            "reviewed_record_id": str(candidate.get("reviewed_record_id") or ""),
            "platform_or_context": str(candidate.get("platform_or_context") or ""),
        },
        "platform_or_context": str(candidate.get("platform_or_context") or ""),
        "source_id": "",
        "source_url": "",
        "source_identifier": "",
        "source_title": "",
        "publisher_or_source_name": "",
        "source_type": "",
        "source_authority": "",
        "observed_artifact_fields": [],
        "observation_notes": "",
        "short_evidence_summary": "",
        "access_method": "manual_page_observation",
        "observed_at": "",
        "collected_at": "",
        "observer": "",
        "reviewer": "",
        "review_rationale": "",
        "live_network_used": False,
        "no_download_performed": True,
        "downloaded_file": False,
        "fetched_binary": False,
        "wayback_replay_used": False,
        "file_fetch_performed": False,
        "proposed_verification_scope": "source_lead_only",
        "proposed_artifact_verified": False,
        "proposed_gate_eligible": False,
        "confidence": "",
        "limitations": [],
        "instructions": [
            "use short field extraction or paraphrase only",
            "do not download binaries, fetch files, or use Wayback replay",
            "set proposed_artifact_verified true only when explicit gate criteria are met",
        ],
    }


def _source_url_list_templates(plan_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for candidate in plan_rows:
        if candidate.get("source_collection_target") is not True:
            continue
        rows.append(
            {
                "collection_id": str(candidate.get("collection_id") or ""),
                "candidate_id": str(candidate.get("candidate_id") or ""),
                "artifact_title": str(candidate.get("title") or ""),
                "source_url": "",
                "source_identifier": "",
                "source_type": "",
                "source_authority": "",
                "expected_observed_fields": _expected_source_fields(candidate),
                "why_this_source_may_help": str(candidate.get("source_collection_reason") or "bounded source observation target"),
                "allowed_access_method": "bounded_page_observation",
                "forbidden_actions": ["download binaries", "fetch files", "replay Wayback", "install or emulate", "marketplace action"],
                "duplicate_check_note": str(candidate.get("source_collection_duplicate_reason") or "not currently counted as a reviewed artifact identity"),
                "notes": "Optional explicit URL list for a future bounded observation pass; no crawling or downloads.",
            }
        )
    return rows


def _manual_packet_from_source_observations(
    candidate: Mapping[str, Any],
    observations: Sequence[Mapping[str, Any]],
    *,
    collection_path: Path,
) -> dict[str, Any]:
    manifest = _source_collection_manifest(collection_path)
    packet = _evidence_packet_from_candidate(candidate, template=False)
    packet_observations = [_source_observation_for_evidence(observation) for observation in observations]
    observation_identity = _merged_observation_identity(observations)
    authority = _packet_source_authority(observations)
    proposed_verified = any(item.get("proposed_artifact_verified") is True for item in observations)
    proposed_gate = any(item.get("proposed_gate_eligible") is True for item in observations)
    verification_scope = _packet_verification_scope(observations, proposed_verified=proposed_verified)
    artifact_verified = bool(
        proposed_verified
        and proposed_gate
        and authority in _APPROVED_ARTIFACT_AUTHORITIES
        and verification_scope not in _INSUFFICIENT_VERIFICATION_SCOPES
    )
    evidence_urls = _dedupe(str(item.get("source_url") or "") for item in observations if str(item.get("source_url") or "").strip())
    source_identifiers = _dedupe(
        str(item.get("source_identifier") or item.get("source_id") or "")
        for item in observations
        if str(item.get("source_identifier") or item.get("source_id") or "").strip()
    )
    observed_fields = _dedupe(
        field
        for observation in observations
        for field in _string_list(observation.get("observed_artifact_fields"))
    )
    reviewer = _first_text(*(item.get("reviewer") for item in observations), *(item.get("observer") for item in observations))
    rationale = _first_text(
        *(item.get("review_rationale") for item in observations),
        *(item.get("short_evidence_summary") for item in observations),
        default="Source observation recorded as a non-verified source lead.",
    )
    packet.update(
        {
            "evidence_packet_id": _stable_id("source-derived-evidence", _collection_id(collection_path), candidate.get("candidate_id"), packet_observations),
            "batch_id": str(manifest.get("manual_batch_id") or ""),
            "artifact_title": _first_text(*(item.get("artifact_title") for item in observations), default=str(packet.get("artifact_title") or "")),
            "artifact_type": _first_text(*(item.get("artifact_type") for item in observations), default=str(packet.get("artifact_type") or "")),
            "artifact_identity_fields": {**dict(packet.get("artifact_identity_fields") or {}), **observation_identity},
            "platform_or_context": _first_text(*(item.get("platform_or_context") for item in observations), default=str(packet.get("platform_or_context") or "")),
            "source_observations": packet_observations,
            "evidence_urls": evidence_urls,
            "source_identifiers": source_identifiers,
            "evidence_type": "source_collection_observation",
            "source_authority": authority,
            "observed_fields": observed_fields,
            "reviewer": reviewer,
            "review_rationale": rationale,
            "collected_at": _first_text(*(item.get("collected_at") for item in observations), *(item.get("observed_at") for item in observations), default="1970-01-01T00:00:00Z"),
            "no_download_performed": True,
            "file_fetch_performed": False,
            "binary_verified": False,
            "download_safe": False,
            "execution_safe": False,
            "rights_cleared": False,
            "verification_scope": verification_scope,
            "artifact_verified": artifact_verified,
            "gate_eligible": artifact_verified,
            "gate_exclusion_reason": "" if artifact_verified else "source_observation_insufficient_for_artifact_verification",
            "non_verified_reason": "" if artifact_verified else "source observation is a source lead or artifact identity candidate, not verified artifact evidence",
            "live_network_used": any(item.get("live_network_used") is True for item in observations),
            "provenance": {
                **dict(packet.get("provenance") or {}),
                "source": "artifact_evidence_source_collection",
                "source_collection_id": _collection_id(collection_path),
                "source_collection_dir": str(collection_path),
            },
        }
    )
    if not artifact_verified:
        packet["verification_scope"] = verification_scope or "artifact_identity_candidate"
    return packet


def _merged_observation_identity(observations: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for observation in observations:
        identity = observation.get("artifact_identity_fields")
        if isinstance(identity, Mapping):
            for key, value in identity.items():
                if str(value or "").strip():
                    merged[str(key)] = value
        for key in ("artifact_title", "artifact_type", "platform_or_context"):
            value = observation.get(key)
            if str(value or "").strip():
                merged[key] = value
    return merged


def _source_observation_for_evidence(observation: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": str(observation.get("source_id") or observation.get("source_observation_id") or ""),
        "source_observation_id": str(observation.get("source_observation_id") or ""),
        "source_url": str(observation.get("source_url") or ""),
        "source_identifier": str(observation.get("source_identifier") or ""),
        "source_title": str(observation.get("source_title") or ""),
        "publisher_or_source_name": str(observation.get("publisher_or_source_name") or ""),
        "source_type": str(observation.get("source_type") or ""),
        "source_authority": str(observation.get("source_authority") or ""),
        "duplicate_check_result": str(observation.get("duplicate_check_result") or ""),
        "observed_artifact_fields": _string_list(observation.get("observed_artifact_fields")),
        "observation_notes": str(observation.get("observation_notes") or ""),
        "short_evidence_summary": str(observation.get("short_evidence_summary") or ""),
        "access_method": str(observation.get("access_method") or "manual_page_observation"),
        "live_network_used": bool(observation.get("live_network_used") is True),
        "downloaded_file": False,
        "fetched_binary": False,
        "file_fetch_performed": False,
        "wayback_replay_used": False,
    }


def _packet_source_authority(observations: Sequence[Mapping[str, Any]]) -> str:
    authorities = {str(item.get("source_authority") or "").strip().casefold() for item in observations}
    source_types = {str(item.get("source_type") or "").strip().casefold() for item in observations}
    mapped = [_SOURCE_AUTHORITY_TO_PACKET_AUTHORITY.get(item) for item in authorities]
    mapped = [item for item in mapped if item]
    if "primary_official_source" in mapped:
        return "primary_official_source"
    if "official_source" in mapped:
        return "official_source"
    if ("archive_metadata" in authorities or "archive_metadata_page" in source_types) and len(observations) >= 2:
        if authorities & {"reputable_secondary", "stable_catalog", "primary", "official"}:
            return "stable_archive_plus_independent_corroboration"
    if "independent_reputable_corroboration" in mapped and len(observations) >= 2:
        return "independent_reputable_corroboration"
    return mapped[0] if mapped else str(next(iter(authorities), "") or "source_collection_observation")


def _packet_verification_scope(observations: Sequence[Mapping[str, Any]], *, proposed_verified: bool) -> str:
    scopes = [str(item.get("proposed_verification_scope") or "").strip() for item in observations if str(item.get("proposed_verification_scope") or "").strip()]
    if proposed_verified and any(scope.casefold() == "artifact_identity_metadata" for scope in scopes):
        return "artifact_identity_metadata"
    return scopes[0] if scopes else "artifact_identity_candidate"


def _expected_source_types(candidate: Mapping[str, Any]) -> list[str]:
    artifact_type = str(candidate.get("artifact_type") or "").casefold()
    if artifact_type == "manual":
        return ["official_support_page", "manual_page", "stable_catalog_page"]
    if artifact_type == "software":
        return ["official_release_notes", "official_support_page", "stable_catalog_page", "reputable_secondary_reference"]
    if artifact_type == "article":
        return ["publication_record", "stable_catalog_page", "reputable_secondary_reference"]
    return ["official_support_page", "stable_catalog_page", "reputable_secondary_reference"]


def _driver_hardware_fields(observation: Mapping[str, Any]) -> bool:
    identity = observation.get("artifact_identity_fields") if isinstance(observation.get("artifact_identity_fields"), Mapping) else {}
    text = _normalize(json.dumps(identity, sort_keys=True, ensure_ascii=True) + " " + str(observation.get("platform_or_context") or ""))
    return any(marker in text for marker in ("ct", "pci", "isa", "model", "hardware", "device", "sound blaster", "win98"))


def _looks_private_source_identifier(value: str) -> bool:
    normalized = value.strip().casefold()
    if not normalized:
        return False
    return any(marker in normalized for marker in _PRIVATE_SOURCE_MARKERS)


def _contains_secret_marker(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True).casefold()
    return any(marker in text for marker in _SECRET_MARKERS)


def _first_text(*values: Any, default: str = "") -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return default


def _source_observations(document: Mapping[str, Any]) -> list[dict[str, Any]]:
    source_hints = _string_list(document.get("source_hints"))
    evidence_hints = _string_list(document.get("evidence_hints"))
    observations: list[dict[str, Any]] = []
    for position, hint in enumerate(source_hints, start=1):
        observations.append(
            {
                "observation_id": _stable_id("source-observation", document.get("id"), hint),
                "kind": "source_hint",
                "position": position,
                "value": hint,
            }
        )
    for position, hint in enumerate(evidence_hints, start=1):
        observations.append(
            {
                "observation_id": _stable_id("evidence-observation", document.get("id"), hint),
                "kind": "evidence_hint",
                "position": position,
                "value": hint,
            }
        )
    return observations


def _source_authority(document: Mapping[str, Any]) -> str:
    provenance = dict(document.get("provenance") or {})
    source_kind = str(provenance.get("source_kind") or "")
    source_family = str(document.get("source_family") or "")
    if str(document.get("record_state") or "") == "reviewed":
        return "local_reviewed_source_lead"
    if "ia_metadata" in source_kind or source_family == "internet_archive":
        return "archive_metadata_fixture"
    if "fixture" in source_kind:
        return "hard_query_fixture"
    return source_family or "unknown"


def _artifact_type(document: Mapping[str, Any]) -> str:
    text = " ".join([str(document.get("title") or ""), " ".join(_string_list(document.get("matched_queries")))]).casefold()
    if "manual" in text:
        return "manual"
    if "driver" in text:
        return "driver"
    if "firefox" in text or "ftp" in text or "apps" in text:
        return "software"
    if "article" in text or "magazine" in text:
        return "article"
    return str(document.get("type") or document.get("category") or "artifact")


def _platform_or_context(document: Mapping[str, Any], query_key: str) -> str:
    text = " ".join([query_key, str(document.get("title") or ""), str(document.get("summary") or "")]).casefold()
    if "ct1740" in text or "sound blaster" in text:
        return "Sound Blaster CT1740"
    if "win98" in text or "windows 98" in text:
        return "Windows 98"
    if "xp" in text:
        return "Windows XP"
    if "windows 7" in text:
        return "Windows 7"
    if "1994" in text or "ray tracing" in text:
        return "1994 magazine article"
    return ""


def _best_query_key(document: Mapping[str, Any]) -> str:
    values = [*_string_list(document.get("matched_queries")), *_string_list(document.get("query_hints"))]
    normalized = [_normalize(item) for item in values]
    for query in _HARD_QUERY_ORDER:
        if query in normalized:
            return query
    haystack = _normalize(" ".join([str(document.get("title") or ""), str(document.get("summary") or ""), " ".join(values)]))
    for query in _HARD_QUERY_ORDER:
        if query in haystack:
            return query
    return normalized[0] if normalized else ""


def _candidate_sort_key(candidate: Mapping[str, Any]) -> tuple[int, int, str]:
    query_key = _normalize(" ".join(_string_list(candidate.get("matched_queries"))))
    order = min((_HARD_QUERY_ORDER.index(item) for item in _HARD_QUERY_ORDER if item in query_key), default=len(_HARD_QUERY_ORDER))
    excluded = 1 if candidate.get("artifact_gate_excluded") is True else 0
    reviewed_rank = 0 if str(candidate.get("review_state") or "") == "accepted" else 1
    return (excluded, order, f"{reviewed_rank}:{candidate.get('source_index_document_id')}")


def _is_fixture_only(packet: Mapping[str, Any]) -> bool:
    text = json.dumps(packet, sort_keys=True, ensure_ascii=True).casefold()
    return any(marker in text for marker in _FIXTURE_MARKERS) or str(packet.get("source_authority") or "") in {
        "archive_metadata_fixture",
        "hard_query_fixture",
        "local_reviewed_source_lead",
    }


def _evidence_source_is_fixture_only(packet: Mapping[str, Any]) -> bool:
    source_authority = str(packet.get("source_authority") or "").strip().casefold()
    evidence_type = str(packet.get("evidence_type") or "").strip().casefold()
    if source_authority in {"archive_metadata_fixture", "hard_query_fixture", "local_reviewed_source_lead"}:
        return True
    if evidence_type in {"source_metadata_lead", "local_fixture", "repo_record"} and source_authority not in _APPROVED_ARTIFACT_AUTHORITIES:
        return True
    observations = _object_list(packet.get("source_observations"))
    if observations:
        access_methods = {str(item.get("access_method") or "").strip().casefold() for item in observations}
        if access_methods and access_methods <= {"local_fixture", "repo_record", ""}:
            return True
        if source_authority in _APPROVED_ARTIFACT_AUTHORITIES:
            return False
    source_text = json.dumps(
        {
            "source_authority": packet.get("source_authority"),
            "evidence_type": packet.get("evidence_type"),
            "source_hints": packet.get("source_hints"),
        },
        sort_keys=True,
        ensure_ascii=True,
    ).casefold()
    return any(marker in source_text for marker in _FIXTURE_MARKERS)


def _int_report_field(report: Mapping[str, Any], key: str, default: int) -> int:
    value = report.get(key)
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _batch_id(batch_path: str | Path) -> str:
    return f"manual-batch:{Path(batch_path).name}"


def _collection_id(collection_path: str | Path) -> str:
    return f"source-collection:{Path(collection_path).name}"


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(json.dumps(parts, sort_keys=True, ensure_ascii=True).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"


def _path_sha256(path: str | Path) -> str:
    source = Path(path)
    return hashlib.sha256(source.read_bytes()).hexdigest() if source.is_file() else ""


def _counts(values: Any) -> dict[str, int]:
    counter = Counter(str(value or "unknown") for value in values)
    return {key: counter[key] for key in sorted(counter)}


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [str(item) for item in value if str(item or "")]
    return [str(value)] if str(value or "") else []


def _object_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _normalize(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())
