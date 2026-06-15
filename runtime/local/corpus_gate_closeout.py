"""Public-alpha corpus gate closeout helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
import re
from typing import Any


TASK_ID = "PUBLIC-ALPHA-CORPUS-GATE-CLOSEOUT-00"
REPORT_SCHEMA_VERSION = "eureka.public_alpha_corpus_gate_closeout.v0"
PUBLIC_ARTIFACT_RECORD_SCHEMA_VERSION = "eureka.public_alpha_artifact_identity_record.v0"
PUBLIC_EVIDENCE_SUMMARY_SCHEMA_VERSION = "eureka.public_alpha_artifact_evidence_summary.v0"

CLOSEOUT_JSON = "corpus_gate_closeout.json"
CLOSEOUT_MD = "CORPUS_GATE_CLOSEOUT.md"
PUBLIC_ARTIFACT_RECORDS_JSONL = "public_artifact_identity_records.jsonl"
PUBLIC_EVIDENCE_SUMMARY_JSONL = "public_artifact_evidence_summary.jsonl"

DEFAULT_GATE_TARGET = 25
REVIEWED_RECORDS_FILE = "reviewed_artifact_records.jsonl"
MANUAL_EVIDENCE_FILE = "manual_evidence_packets.jsonl"

IDENTITY_SCOPE = "artifact_identity_metadata"
SAFETY_FIELDS = ("binary_verified", "download_safe", "execution_safe", "rights_cleared")
FORBIDDEN_PUBLIC_MARKERS = (
    ".eureka",
    ".aide",
    "local_review_ledger",
    "local_reviewed_records",
    "local_search_index",
    "workbench-token",
    "X-Eureka-Workbench-Token",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "DEEPSEEK_API_KEY",
    "BEGIN PRIVATE KEY",
    "sk-",
)
SECRET_MARKERS = ("api_key", "apikey", "authorization:", "bearer ", "secret", "token=")
UNSAFE_ACTION_KEYS = (
    "download_url",
    "install_url",
    "emulate_url",
    "review_action",
    "mutation_action",
    "accept_action",
    "rebuild_action",
)
_WINDOWS_ABSOLUTE_PATH = re.compile(r"\b[A-Za-z]:[\\/]")


def closeout_corpus_gate(
    *,
    artifact_gate_report: str | Path,
    manual_batch: str | Path,
    out_dir: str | Path,
) -> dict[str, Any]:
    """Write public-safe corpus gate closeout artifacts."""

    report_path = Path(artifact_gate_report)
    batch_path = Path(manual_batch)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    gate_report = _read_json(report_path)
    records = read_jsonl(batch_path / REVIEWED_RECORDS_FILE)
    packets = read_jsonl(batch_path / MANUAL_EVIDENCE_FILE) if (batch_path / MANUAL_EVIDENCE_FILE).is_file() else []
    counted_records = _counted_records(records)
    source_errors = _source_public_safety_errors(counted_records)
    if source_errors:
        joined = "; ".join(source_errors[:10])
        if len(source_errors) > 10:
            joined += f"; plus {len(source_errors) - 10} more"
        raise ValueError(f"source reviewed artifact records are not public-safe: {joined}")

    public_records: list[dict[str, Any]] = []
    public_summaries: list[dict[str, Any]] = []
    for record in counted_records:
        public_record = _public_artifact_record(record)
        summary = _public_evidence_summary(record, public_artifact_id=public_record["public_artifact_id"])
        public_record["evidence_summary_refs"] = [summary["evidence_summary_id"]]
        public_records.append(public_record)
        public_summaries.append(summary)

    public_records = sorted(public_records, key=lambda item: (str(item.get("title") or ""), str(item.get("public_artifact_id") or "")))
    public_summaries = sorted(public_summaries, key=lambda item: (str(item.get("public_artifact_id") or ""), str(item.get("evidence_summary_id") or "")))

    records_path = out_path / PUBLIC_ARTIFACT_RECORDS_JSONL
    summaries_path = out_path / PUBLIC_EVIDENCE_SUMMARY_JSONL
    write_jsonl(records_path, public_records)
    write_jsonl(summaries_path, public_summaries)

    closeout = _closeout_report(
        gate_report=gate_report,
        artifact_gate_report_path=report_path,
        manual_batch_path=batch_path,
        public_records=public_records,
        public_summaries=public_summaries,
        records_path=records_path,
        summaries_path=summaries_path,
        packets=packets,
    )
    closeout_path = out_path / CLOSEOUT_JSON
    write_json(closeout_path, closeout)
    (out_path / CLOSEOUT_MD).write_text(render_closeout_markdown(closeout), encoding="utf-8")
    return closeout


def validate_closeout(closeout_dir: str | Path) -> list[str]:
    closeout_path = Path(closeout_dir)
    errors: list[str] = []
    required = {
        "closeout": closeout_path / CLOSEOUT_JSON,
        "markdown": closeout_path / CLOSEOUT_MD,
        "public_artifact_identity_records": closeout_path / PUBLIC_ARTIFACT_RECORDS_JSONL,
        "public_artifact_evidence_summary": closeout_path / PUBLIC_EVIDENCE_SUMMARY_JSONL,
    }
    for label, path in required.items():
        if not path.is_file():
            errors.append(f"missing {label}: {path}")
    if errors:
        return errors

    try:
        closeout = _read_json(required["closeout"])
        records = read_jsonl(required["public_artifact_identity_records"])
        summaries = read_jsonl(required["public_artifact_evidence_summary"])
    except (OSError, json.JSONDecodeError) as exc:
        return [f"closeout artifacts could not be read: {type(exc).__name__}"]

    errors.extend(_validate_closeout_payload(closeout, records=records, summaries=summaries, closeout_dir=closeout_path))
    errors.extend(_public_payload_errors("corpus_gate_closeout.json", closeout))
    errors.extend(_public_payload_errors(PUBLIC_ARTIFACT_RECORDS_JSONL, records))
    errors.extend(_public_payload_errors(PUBLIC_EVIDENCE_SUMMARY_JSONL, summaries))
    return _dedupe(errors)


def closeout_status(closeout_dir: str | Path) -> dict[str, Any]:
    closeout_path = Path(closeout_dir)
    errors = validate_closeout(closeout_path)
    payload: dict[str, Any] = {
        "schema_version": "eureka.public_alpha_corpus_gate_closeout_status.v0",
        "task_id": TASK_ID,
        "status": "pass" if not errors else "fail",
        "closeout": str(closeout_path),
        "corpus_gate_status": "unknown",
        "reviewed_artifact_gate_count": 0,
        "artifact_verified_count": 0,
        "public_artifact_identity_record_count": 0,
        "public_artifact_evidence_summary_count": 0,
        "verification_scope_counts": {},
        "binary_verified_count": 0,
        "download_safe_count": 0,
        "execution_safe_count": 0,
        "rights_cleared_count": 0,
        "validation_errors": errors,
    }
    report_path = closeout_path / CLOSEOUT_JSON
    if report_path.is_file():
        try:
            report = _read_json(report_path)
        except (OSError, json.JSONDecodeError):
            report = {}
        if isinstance(report, Mapping):
            payload.update(
                {
                    "corpus_gate_status": str(report.get("corpus_gate_status") or "unknown"),
                    "reviewed_artifact_gate_count": int(report.get("reviewed_artifact_gate_count") or 0),
                    "artifact_verified_count": int(report.get("artifact_verified_count") or 0),
                    "public_artifact_identity_record_count": int(report.get("public_artifact_identity_record_count") or 0),
                    "public_artifact_evidence_summary_count": int(report.get("public_artifact_evidence_summary_count") or 0),
                    "verification_scope_counts": dict(report.get("verification_scope_counts") or {}),
                    "binary_verified_count": int(report.get("binary_verified_count") or 0),
                    "download_safe_count": int(report.get("download_safe_count") or 0),
                    "execution_safe_count": int(report.get("execution_safe_count") or 0),
                    "rights_cleared_count": int(report.get("rights_cleared_count") or 0),
                }
            )
    return payload


def render_status_text(status: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            f"status: {status.get('status')}",
            f"corpus_gate_status: {status.get('corpus_gate_status')}",
            f"reviewed_artifact_gate_count: {status.get('reviewed_artifact_gate_count')}/{DEFAULT_GATE_TARGET}",
            f"artifact_verified_count: {status.get('artifact_verified_count')}",
            f"public_artifact_identity_record_count: {status.get('public_artifact_identity_record_count')}",
            f"public_artifact_evidence_summary_count: {status.get('public_artifact_evidence_summary_count')}",
            f"verification_scope_counts: {json.dumps(status.get('verification_scope_counts') or {}, sort_keys=True)}",
            f"binary_verified_count: {status.get('binary_verified_count')}",
            f"download_safe_count: {status.get('download_safe_count')}",
            f"execution_safe_count: {status.get('execution_safe_count')}",
            f"rights_cleared_count: {status.get('rights_cleared_count')}",
            f"validation_errors: {json.dumps(status.get('validation_errors') or [])}",
        ]
    ) + "\n"


def render_closeout_markdown(report: Mapping[str, Any]) -> str:
    blockers = report.get("blockers") or []
    warnings = report.get("warnings") or []
    blocker_lines = [f"- {item.get('id')}: {item.get('message')}" for item in blockers if isinstance(item, Mapping)] or ["- none"]
    warning_lines = [f"- {item}" for item in warnings] or ["- none"]
    return "\n".join(
        [
            "# Public Alpha Corpus Gate Closeout",
            "",
            f"- Status: {report.get('status')}",
            f"- Corpus gate status: {report.get('corpus_gate_status')}",
            f"- Reviewed artifact gate count: {report.get('reviewed_artifact_gate_count')}/{report.get('gate_target_reviewed_artifacts')}",
            f"- Artifact verified count: {report.get('artifact_verified_count')}",
            f"- Public artifact identity records: {report.get('public_artifact_identity_record_count')}",
            f"- Public evidence summaries: {report.get('public_artifact_evidence_summary_count')}",
            f"- Verification scopes: {json.dumps(report.get('verification_scope_counts') or {}, sort_keys=True)}",
            f"- Binary verified count: {report.get('binary_verified_count')}",
            f"- Download safe count: {report.get('download_safe_count')}",
            f"- Execution safe count: {report.get('execution_safe_count')}",
            f"- Rights cleared count: {report.get('rights_cleared_count')}",
            "",
            "Artifact verified means artifact identity metadata only. It does not mean binary, download, execution, rights, malware, production, or public-launch safety.",
            "",
            "## Blockers",
            "",
            *blocker_lines,
            "",
            "## Warnings",
            "",
            *warning_lines,
            "",
            "This generated closeout is public-alpha operational evidence only. It is not canon, release promotion, deployment, or launch approval.",
            "",
        ]
    )


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        loaded = json.loads(line)
        if isinstance(loaded, dict):
            rows.append(loaded)
    return rows


def write_jsonl(path: str | Path, rows: Sequence[Mapping[str, Any]]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(dict(row), sort_keys=True, ensure_ascii=True) + "\n")


def write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(dict(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def _closeout_report(
    *,
    gate_report: Mapping[str, Any],
    artifact_gate_report_path: Path,
    manual_batch_path: Path,
    public_records: Sequence[Mapping[str, Any]],
    public_summaries: Sequence[Mapping[str, Any]],
    records_path: Path,
    summaries_path: Path,
    packets: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    blockers = []
    gate_target = int(gate_report.get("gate_target_reviewed_artifacts") or DEFAULT_GATE_TARGET)
    reviewed_count = int(gate_report.get("reviewed_artifact_gate_count") or 0)
    artifact_verified_count = int(gate_report.get("artifact_verified_count") or 0)
    if reviewed_count < gate_target:
        blockers.append(
            {
                "id": "reviewed_artifact_gate_count_below_target",
                "message": f"reviewed artifact gate count is {reviewed_count}/{gate_target}",
                "status": "blocked",
            }
        )
    if artifact_verified_count < gate_target:
        blockers.append(
            {
                "id": "artifact_verified_count_below_target",
                "message": f"artifact verified count is {artifact_verified_count}/{gate_target}",
                "status": "blocked",
            }
        )
    if len(public_records) != reviewed_count:
        blockers.append(
            {
                "id": "public_identity_record_count_mismatch",
                "message": "public artifact identity record count does not match reviewed artifact gate count",
                "status": "blocked",
            }
        )

    verification_scope_counts = _counts(record.get("verification_scope") for record in public_records)
    report = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "status": "PASS" if not blockers else "FAIL",
        "corpus_gate_status": "pass" if not blockers else "blocked",
        "gate_target_reviewed_artifacts": gate_target,
        "reviewed_artifact_gate_count": reviewed_count,
        "artifact_verified_count": artifact_verified_count,
        "public_artifact_identity_record_count": len(public_records),
        "public_artifact_evidence_summary_count": len(public_summaries),
        "verification_scope_counts": verification_scope_counts,
        "evidence_packet_count": int(gate_report.get("evidence_packet_count") or len(packets)),
        "source_authority_counts": dict(gate_report.get("source_authority_counts") or _counts(record.get("source_authority") for record in public_records)),
        "binary_verified_count": sum(1 for record in public_records if record.get("binary_verified") is True),
        "download_safe_count": sum(1 for record in public_records if record.get("download_safe") is True),
        "execution_safe_count": sum(1 for record in public_records if record.get("execution_safe") is True),
        "rights_cleared_count": sum(1 for record in public_records if record.get("rights_cleared") is True),
        "source_artifact_gate_report_digest": _file_sha256(artifact_gate_report_path),
        "public_artifact_identity_records_digest": _file_sha256(records_path),
        "public_artifact_evidence_summary_digest": _file_sha256(summaries_path),
        "launch_gate_payload": {
            "corpus_gate_closeout_status": "pass" if not blockers else "blocked",
            "corpus_gate_status": "pass" if not blockers else "blocked",
            "reviewed_artifact_gate_count": reviewed_count,
            "artifact_verified_count": artifact_verified_count,
            "public_artifact_identity_record_count": len(public_records),
            "verification_scope_counts": verification_scope_counts,
            "artifact_identity_metadata_only": True,
            "binary_verified_count": 0,
            "download_safe_count": 0,
            "execution_safe_count": 0,
            "rights_cleared_count": 0,
        },
        "blockers": blockers,
        "warnings": [
            "artifact_verified means artifact identity metadata only",
            "binary/download/execution/rights safety is not asserted",
            "corpus closeout is generated operational evidence, not public launch approval",
        ],
        "generated_at": "1970-01-01T00:00:00Z",
        "manual_batch_id": _safe_text(gate_report.get("batch_id") or manual_batch_path.name),
        "no_download_performed": True,
        "file_fetch_performed": False,
        "wayback_replay_used": False,
        "truth_promotion_performed": False,
        "public_launch_ready_claimed": False,
    }
    return report


def _public_artifact_record(record: Mapping[str, Any]) -> dict[str, Any]:
    identity = _public_identity_fields(record.get("artifact_identity_fields"))
    reviewed_id = _safe_text(record.get("reviewed_artifact_record_id"))
    public_id = _stable_public_id(record)
    observations = _public_observations(record.get("source_observations"))
    return {
        "schema_version": PUBLIC_ARTIFACT_RECORD_SCHEMA_VERSION,
        "public_artifact_id": public_id,
        "title": _safe_text(record.get("title")),
        "artifact_type": _safe_text(record.get("artifact_type") or "unknown"),
        "version_or_identity_fields": identity,
        "platform_or_context": _safe_text(record.get("platform_or_context")),
        "artifact_verified": True,
        "verification_scope": _safe_text(record.get("verification_scope") or IDENTITY_SCOPE),
        "binary_verified": bool(record.get("binary_verified") is True),
        "download_safe": bool(record.get("download_safe") is True),
        "execution_safe": bool(record.get("execution_safe") is True),
        "rights_cleared": bool(record.get("rights_cleared") is True),
        "evidence_summary_refs": [],
        "source_authority_summary": {
            "source_authority": _safe_text(record.get("source_authority")),
            "source_count": len(observations),
            "source_types": sorted({str(item.get("source_type") or "unknown") for item in observations}),
            "observed_fields": _safe_list(record.get("observed_fields")),
        },
        "reviewed_artifact_record_id": reviewed_id,
        "provenance_summary": {
            "batch_id": _safe_text(record.get("batch_id")),
            "review_state": _safe_text(record.get("review_state")),
            "source_evidence_packet_id": _safe_text(record.get("source_evidence_packet_id")),
            "source_authority": _safe_text(record.get("source_authority")),
            "verification_scope": _safe_text(record.get("verification_scope") or IDENTITY_SCOPE),
        },
        "no_download_performed": True,
        "file_fetch_performed": False,
        "wayback_replay_used": False,
        "public_safe": True,
        "artifact_identity_metadata_only": True,
    }


def _public_evidence_summary(record: Mapping[str, Any], *, public_artifact_id: str) -> dict[str, Any]:
    observations = _public_observations(record.get("source_observations"))
    first = observations[0] if observations else {}
    public_urls = [str(item.get("source_url") or "") for item in observations if _looks_like_url(str(item.get("source_url") or ""))]
    source_identifiers = _safe_list(record.get("source_identifiers"))
    evidence_summary_id = "public-evidence:" + _sha256_text(public_artifact_id + "|" + _safe_text(record.get("source_evidence_packet_id")))[:16]
    return {
        "schema_version": PUBLIC_EVIDENCE_SUMMARY_SCHEMA_VERSION,
        "evidence_summary_id": evidence_summary_id,
        "public_artifact_id": public_artifact_id,
        "evidence_source_type": _safe_text(record.get("evidence_type") or first.get("source_type") or "source_collection_observation"),
        "source_authority": _safe_text(record.get("source_authority")),
        "source_title": _safe_text(first.get("source_title") or record.get("title")),
        "source_identifier": _safe_text((source_identifiers or [_safe_text(first.get("source_identifier"))])[0]),
        "public_urls": public_urls,
        "observed_fields": _safe_list(record.get("observed_fields")),
        "short_evidence_summary": _safe_text(first.get("short_evidence_summary") or f"Public source metadata supports the artifact identity for {record.get('title') or 'this artifact'}."),
        "limitations": [
            "supports artifact identity metadata only",
            "does not verify binaries, downloads, execution safety, rights, malware status, or launch readiness",
            "no download, file fetch, or Wayback replay was performed by this closeout",
        ],
        "verification_scope_supported": _safe_text(record.get("verification_scope") or IDENTITY_SCOPE),
        "no_download_performed": True,
        "file_fetch_performed": False,
        "binary_verified": bool(record.get("binary_verified") is True),
        "download_safe": bool(record.get("download_safe") is True),
        "execution_safe": bool(record.get("execution_safe") is True),
        "rights_cleared": bool(record.get("rights_cleared") is True),
    }


def _counted_records(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    counted = [
        dict(record)
        for record in records
        if record.get("artifact_verified") is True and record.get("gate_eligible") is True
    ]
    return sorted(counted, key=lambda item: (str(item.get("dedupe_identity_key") or ""), str(item.get("reviewed_artifact_record_id") or "")))


def _validate_closeout_payload(
    closeout: Mapping[str, Any],
    *,
    records: Sequence[Mapping[str, Any]],
    summaries: Sequence[Mapping[str, Any]],
    closeout_dir: Path,
) -> list[str]:
    errors: list[str] = []
    required = (
        "task_id",
        "status",
        "corpus_gate_status",
        "gate_target_reviewed_artifacts",
        "reviewed_artifact_gate_count",
        "artifact_verified_count",
        "public_artifact_identity_record_count",
        "verification_scope_counts",
        "evidence_packet_count",
        "source_authority_counts",
        "binary_verified_count",
        "download_safe_count",
        "execution_safe_count",
        "rights_cleared_count",
        "source_artifact_gate_report_digest",
        "public_artifact_identity_records_digest",
        "public_artifact_evidence_summary_digest",
        "launch_gate_payload",
        "blockers",
        "warnings",
    )
    for key in required:
        if key not in closeout:
            errors.append(f"missing required field: {key}")
    if errors:
        return errors
    if closeout.get("task_id") != TASK_ID:
        errors.append(f"task_id must be {TASK_ID}")
    if closeout.get("status") not in {"PASS", "PASS_WITH_WARNINGS", "FAIL"}:
        errors.append("status must be PASS, PASS_WITH_WARNINGS, or FAIL")
    if closeout.get("corpus_gate_status") not in {"pass", "fail", "blocked"}:
        errors.append("corpus_gate_status must be pass, fail, or blocked")
    target = int(closeout.get("gate_target_reviewed_artifacts") or DEFAULT_GATE_TARGET)
    reviewed_count = int(closeout.get("reviewed_artifact_gate_count") or 0)
    verified_count = int(closeout.get("artifact_verified_count") or 0)
    if reviewed_count < target:
        errors.append(f"reviewed_artifact_gate_count must be at least {target}")
    if verified_count < target:
        errors.append(f"artifact_verified_count must be at least {target}")
    if len(records) != reviewed_count:
        errors.append("public artifact identity record count must match reviewed_artifact_gate_count")
    if int(closeout.get("public_artifact_identity_record_count") or 0) != len(records):
        errors.append("public_artifact_identity_record_count must match public_artifact_identity_records.jsonl")
    if int(closeout.get("public_artifact_evidence_summary_count") or 0) != len(summaries):
        errors.append("public_artifact_evidence_summary_count must match public_artifact_evidence_summary.jsonl")
    if str(closeout.get("public_artifact_identity_records_digest") or "") != _file_sha256(closeout_dir / PUBLIC_ARTIFACT_RECORDS_JSONL):
        errors.append("public_artifact_identity_records_digest must match public_artifact_identity_records.jsonl")
    if str(closeout.get("public_artifact_evidence_summary_digest") or "") != _file_sha256(closeout_dir / PUBLIC_EVIDENCE_SUMMARY_JSONL):
        errors.append("public_artifact_evidence_summary_digest must match public_artifact_evidence_summary.jsonl")
    ids = [str(record.get("public_artifact_id") or "") for record in records]
    if len(set(ids)) != len(ids):
        errors.append("public_artifact_id values must be unique")
    identity_keys = [
        _identity_key(record)
        for record in records
    ]
    if len(set(identity_keys)) != len(identity_keys):
        errors.append("duplicate artifact identity appears in public records")
    summary_ids = {str(summary.get("evidence_summary_id") or "") for summary in summaries}
    for index, record in enumerate(records, start=1):
        errors.extend(f"record[{index}]: {error}" for error in _validate_public_record(record, summary_ids))
    for index, summary in enumerate(summaries, start=1):
        errors.extend(f"summary[{index}]: {error}" for error in _validate_public_summary(summary))
    return errors


def _validate_public_record(record: Mapping[str, Any], summary_ids: set[str]) -> list[str]:
    errors: list[str] = []
    for key in ("public_artifact_id", "title", "artifact_type", "platform_or_context", "verification_scope"):
        if not str(record.get(key) or "").strip():
            errors.append(f"{key} is required")
    identity = record.get("version_or_identity_fields")
    if not isinstance(identity, Mapping) or not identity:
        errors.append("version_or_identity_fields are required")
    if record.get("artifact_verified") is not True:
        errors.append("artifact_verified must be true for counted public identity records")
    if record.get("verification_scope") != IDENTITY_SCOPE:
        errors.append("verification_scope must be artifact_identity_metadata")
    for field in SAFETY_FIELDS:
        if record.get(field) is True:
            errors.append(f"{field} cannot be true without approved proof")
    if record.get("no_download_performed") is not True:
        errors.append("no_download_performed must be true")
    if record.get("file_fetch_performed") is not False:
        errors.append("file_fetch_performed must be false")
    if record.get("wayback_replay_used") is not False:
        errors.append("wayback_replay_used must be false")
    if record.get("public_safe") is not True:
        errors.append("public_safe must be true")
    refs = [str(ref or "") for ref in record.get("evidence_summary_refs") or []]
    if not refs:
        errors.append("evidence_summary_refs are required")
    for ref in refs:
        if ref not in summary_ids:
            errors.append(f"unknown evidence_summary_ref: {ref}")
    return errors


def _validate_public_summary(summary: Mapping[str, Any]) -> list[str]:
    errors = []
    for key in ("evidence_summary_id", "public_artifact_id", "evidence_source_type", "source_authority", "source_title", "verification_scope_supported"):
        if not str(summary.get(key) or "").strip():
            errors.append(f"{key} is required")
    if summary.get("verification_scope_supported") != IDENTITY_SCOPE:
        errors.append("verification_scope_supported must be artifact_identity_metadata")
    for field in SAFETY_FIELDS:
        if summary.get(field) is True:
            errors.append(f"{field} cannot be true without approved proof")
    if summary.get("no_download_performed") is not True:
        errors.append("no_download_performed must be true")
    if summary.get("file_fetch_performed") is not False:
        errors.append("file_fetch_performed must be false")
    return errors


def _public_payload_errors(label: str, value: Any) -> list[str]:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True) if not isinstance(value, str) else value
    lowered = text.casefold()
    errors = []
    for marker in FORBIDDEN_PUBLIC_MARKERS:
        if marker.casefold() in lowered:
            errors.append(f"{label} contains forbidden marker {marker}")
    for marker in SECRET_MARKERS:
        if marker.casefold() in lowered:
            errors.append(f"{label} contains forbidden secret marker {marker}")
    if _WINDOWS_ABSOLUTE_PATH.search(text):
        errors.append(f"{label} contains a Windows absolute path")
    if "/Users/" in text or "\\Users\\" in text:
        errors.append(f"{label} contains a user-home path")
    for key in UNSAFE_ACTION_KEYS:
        if key.casefold() in lowered:
            errors.append(f"{label} exposes unsafe action key {key}")
    return errors


def _source_public_safety_errors(records: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    for index, record in enumerate(records, start=1):
        for field in SAFETY_FIELDS:
            if record.get(field) is True:
                errors.append(f"record[{index}]: {field} cannot be true without approved proof")
        for key in UNSAFE_ACTION_KEYS:
            if key in record:
                errors.append(f"record[{index}]: exposes unsafe action key {key}")
        probe = {
            "title": record.get("title"),
            "artifact_type": record.get("artifact_type"),
            "platform_or_context": record.get("platform_or_context"),
            "artifact_identity_fields": _raw_public_identity_fields(record.get("artifact_identity_fields")),
            "source_authority": record.get("source_authority"),
            "source_identifiers": record.get("source_identifiers"),
            "observed_fields": record.get("observed_fields"),
            "source_observations": _raw_public_observations(record.get("source_observations")),
        }
        errors.extend(f"record[{index}]: {error}" for error in _public_payload_errors("source reviewed artifact record", probe))
    return _dedupe(errors)


def _raw_public_identity_fields(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {}
    blocked = {
        "reviewed_record_id",
        "source_index_document_id",
        "local_path",
        "path",
        "download_url",
        "install_url",
        "emulate_url",
    }
    return {str(key): item for key, item in value.items() if str(key) not in blocked}


def _raw_public_observations(value: Any) -> list[dict[str, Any]]:
    observations = []
    for item in value if isinstance(value, list) else []:
        if not isinstance(item, Mapping):
            continue
        observations.append(
            {
                "source_title": item.get("source_title"),
                "source_type": item.get("source_type"),
                "source_authority": item.get("source_authority"),
                "source_identifier": item.get("source_identifier"),
                "source_url": item.get("source_url"),
                "observed_artifact_fields": item.get("observed_artifact_fields"),
                "short_evidence_summary": item.get("short_evidence_summary"),
            }
        )
    return observations


def _public_identity_fields(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {}
    blocked = {
        "reviewed_record_id",
        "source_index_document_id",
        "local_path",
        "path",
        "download_url",
        "install_url",
        "emulate_url",
    }
    result = {}
    for key, item in value.items():
        key_text = str(key)
        if key_text in blocked:
            continue
        result[key_text] = _safe_value(item)
    return result


def _public_observations(value: Any) -> list[dict[str, Any]]:
    observations = []
    for item in value if isinstance(value, list) else []:
        if not isinstance(item, Mapping):
            continue
        observations.append(
            {
                "source_title": _safe_text(item.get("source_title")),
                "source_type": _safe_text(item.get("source_type")),
                "source_authority": _safe_text(item.get("source_authority")),
                "source_identifier": _safe_text(item.get("source_identifier")),
                "source_url": _safe_url(item.get("source_url")),
                "observed_artifact_fields": _safe_list(item.get("observed_artifact_fields")),
                "short_evidence_summary": _safe_text(item.get("short_evidence_summary")),
            }
        )
    return observations


def _safe_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _safe_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_safe_value(item) for item in value]
    if isinstance(value, tuple):
        return [_safe_value(item) for item in value]
    if isinstance(value, str):
        return _safe_text(value)
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return _safe_text(value)


def _safe_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_safe_text(item) for item in value if str(item or "").strip()]
    if isinstance(value, tuple):
        return [_safe_text(item) for item in value if str(item or "").strip()]
    if str(value or "").strip():
        return [_safe_text(value)]
    return []


def _safe_text(value: Any) -> str:
    text = str(value or "")
    for marker in FORBIDDEN_PUBLIC_MARKERS:
        text = text.replace(marker, "[redacted]")
    if _WINDOWS_ABSOLUTE_PATH.search(text):
        text = _WINDOWS_ABSOLUTE_PATH.sub("[redacted-path]", text)
    text = text.replace("\\", "/")
    return text.strip()


def _safe_url(value: Any) -> str:
    text = str(value or "").strip()
    if _looks_like_url(text):
        return text
    return _safe_text(text)


def _stable_public_id(record: Mapping[str, Any]) -> str:
    source = str(record.get("dedupe_identity_key") or record.get("reviewed_artifact_record_id") or record.get("title") or "")
    return "public-artifact:" + _sha256_text(source)[:16]


def _identity_key(record: Mapping[str, Any]) -> str:
    fields = record.get("version_or_identity_fields") if isinstance(record.get("version_or_identity_fields"), Mapping) else {}
    parts = [
        record.get("title"),
        record.get("artifact_type"),
        record.get("platform_or_context"),
        fields.get("product"),
        fields.get("version"),
        fields.get("release_date"),
        record.get("verification_scope"),
    ]
    return "|".join(_normalize(part) for part in parts if str(part or "").strip())


def _counts(values: Sequence[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value or "unknown")
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _dedupe(values: Sequence[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _normalize(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def _read_json(path: str | Path) -> dict[str, Any]:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def _file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _looks_like_url(value: str) -> bool:
    text = value.strip().casefold()
    return text.startswith("http://") or text.startswith("https://")
