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
ARTIFACT_GATE_SCHEMA_VERSION = "eureka.reviewed_artifact_gate_seed.v0"
CANDIDATE_SCHEMA_VERSION = "eureka.artifact_gate_candidate.v0"
EVIDENCE_PACKET_SCHEMA_VERSION = "eureka.artifact_gate_evidence_packet.v0"
REVIEWED_ARTIFACT_RECORD_SCHEMA_VERSION = "eureka.reviewed_artifact_gate_record.v0"
DEFAULT_GATE_TARGET = 25
DEFAULT_GATE_DIR = ".eureka/artifact-gate/public-alpha-seed"
DEFAULT_CANDIDATES_FILE = "candidates.jsonl"
DEFAULT_EVIDENCE_TEMPLATE_FILE = "evidence_template.jsonl"
DEFAULT_EVIDENCE_PACKETS_FILE = "evidence_packets.jsonl"
DEFAULT_REVIEWED_ARTIFACT_RECORDS_FILE = "reviewed_artifact_records.jsonl"
DEFAULT_GATE_REPORT_FILE = "artifact_gate_report.json"
DEFAULT_GATE_REPORT_MD = "ARTIFACT_GATE_REPORT.md"

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
        if _is_fixture_only(packet):
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


def _int_report_field(report: Mapping[str, Any], key: str, default: int) -> int:
    value = report.get(key)
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


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
