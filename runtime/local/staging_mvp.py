"""Local staging bundle helpers for the public-alpha MVP."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any

from runtime.local.corpus_gate_closeout import (
    CLOSEOUT_JSON as CORPUS_CLOSEOUT_FILE,
    PUBLIC_ARTIFACT_RECORDS_JSONL,
    PUBLIC_EVIDENCE_SUMMARY_JSONL,
    validate_closeout,
)
from runtime.local.search_index import load_index, render_index_json, stats_payload, validate_index


TASK_ID = "LOCAL-TO-STAGING-DEPLOYMENT-00"
BUNDLE_SCHEMA_VERSION = "eureka.local_staging_public_alpha_bundle.v0"
RUNTIME_CONFIG_SCHEMA_VERSION = "eureka.local_staging_public_runtime_config.v0"
PUBLIC_INDEX_FILE = "public_search_index.json"
MANIFEST_FILE = "manifest.json"
RUNTIME_CONFIG_FILE = "public_runtime_config.json"
REQUIRED_BUNDLE_FILES = frozenset({MANIFEST_FILE, PUBLIC_INDEX_FILE, RUNTIME_CONFIG_FILE})
CORPUS_BUNDLE_FILES = frozenset({CORPUS_CLOSEOUT_FILE, PUBLIC_ARTIFACT_RECORDS_JSONL, PUBLIC_EVIDENCE_SUMMARY_JSONL})
ALLOWED_BUNDLE_FILES = REQUIRED_BUNDLE_FILES | CORPUS_BUNDLE_FILES
SAFE_ACTIONS = ("view_record",)
FORBIDDEN_BUNDLE_MARKERS = (
    ".eureka",
    "local_review_ledger",
    "local_reviewed_records",
    "local_search_index.json",
    "local_search_index.reviewed.json",
    "workbench-token",
    "X-Eureka-Workbench-Token",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "DEEPSEEK_API_KEY",
    "BEGIN PRIVATE KEY",
    "sk-",
)
_WINDOWS_ABSOLUTE_PATH = re.compile(r"\b[A-Za-z]:[\\/]")


def package_bundle(index_path: str | Path, out_dir: str | Path, corpus_gate_closeout: str | Path | None = None) -> dict[str, Any]:
    source_path = Path(index_path)
    output = Path(out_dir)
    corpus_path = Path(corpus_gate_closeout) if corpus_gate_closeout else None
    source_index = load_index(source_path)
    source_errors = validate_index(source_index)
    if source_errors:
        raise ValueError("source index is invalid: " + "; ".join(source_errors))

    public_index = public_safe_index(source_index)
    public_errors = validate_index(public_index)
    if public_errors:
        raise ValueError("public index is invalid after sanitization: " + "; ".join(public_errors))

    runtime_config = public_runtime_config()
    source_index_digest = _file_sha256(source_path)
    public_index_json = render_index_json(public_index)
    runtime_config_json = _stable_json(runtime_config)
    public_index_digest = _sha256_text(public_index_json)
    runtime_config_digest = _sha256_text(runtime_config_json)
    stats = stats_payload(public_index)
    corpus_payload = _corpus_payload(corpus_path) if corpus_path else _empty_corpus_payload()
    manifest = {
        "bundle_schema_version": BUNDLE_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "bundle_id": f"public-alpha:{public_index_digest[:16]}",
        "source_index_digest": source_index_digest,
        "public_index_digest": public_index_digest,
        "runtime_config_digest": runtime_config_digest,
        "document_count": stats["document_count"],
        "status_counts": stats["status_counts"],
        "reviewed_record_count": stats["reviewed_record_count"],
        "public_search_index_artifact_verified_count": stats["artifact_verified_count"],
        "artifact_verified_count": corpus_payload["artifact_verified_count"] if corpus_path else stats["artifact_verified_count"],
        "corpus_gate_status": corpus_payload["corpus_gate_status"],
        "reviewed_artifact_gate_count": corpus_payload["reviewed_artifact_gate_count"],
        "public_artifact_identity_record_count": corpus_payload["public_artifact_identity_record_count"],
        "public_artifact_evidence_summary_count": corpus_payload["public_artifact_evidence_summary_count"],
        "verification_scope_counts": corpus_payload["verification_scope_counts"],
        "binary_verified_count": corpus_payload["binary_verified_count"],
        "download_safe_count": corpus_payload["download_safe_count"],
        "execution_safe_count": corpus_payload["execution_safe_count"],
        "rights_cleared_count": corpus_payload["rights_cleared_count"],
        "artifact_identity_metadata_only": bool(corpus_path),
        "public_alpha_mode": True,
        "read_only": True,
        "live_metadata_enabled": False,
        "public_live_fanout": False,
        "workbench_exposed": False,
        "workbench_enabled": False,
        "downloads_enabled": False,
        "file_fetching_enabled": False,
        "wayback_replay_enabled": False,
        "extraction_enabled": False,
        "install_emulation_enabled": False,
        "marketplace_enabled": False,
        "mutation_enabled": False,
        "public_mutation_enabled": False,
        "private_review_artifacts_included": False,
        "local_paths_included": False,
        "generated_from_commit": _git_head(),
        "deterministic_package": True,
        "files": {
            "public_index": PUBLIC_INDEX_FILE,
            "runtime_config": RUNTIME_CONFIG_FILE,
        },
    }
    if corpus_path:
        manifest.update(
            {
                "corpus_gate_closeout_digest": corpus_payload["corpus_gate_closeout_digest"],
                "public_artifact_identity_records_digest": corpus_payload["public_artifact_identity_records_digest"],
                "public_artifact_evidence_summary_digest": corpus_payload["public_artifact_evidence_summary_digest"],
            }
        )
        manifest["files"].update(
            {
                "corpus_gate_closeout": CORPUS_CLOSEOUT_FILE,
                "public_artifact_identity_records": PUBLIC_ARTIFACT_RECORDS_JSONL,
                "public_artifact_evidence_summary": PUBLIC_EVIDENCE_SUMMARY_JSONL,
            }
        )
    manifest_json = _stable_json(manifest)

    bundle_payload = {
        MANIFEST_FILE: manifest_json,
        PUBLIC_INDEX_FILE: public_index_json,
        RUNTIME_CONFIG_FILE: runtime_config_json,
    }
    if corpus_path:
        bundle_payload[CORPUS_CLOSEOUT_FILE] = corpus_payload["corpus_gate_closeout_body"]
        bundle_payload[PUBLIC_ARTIFACT_RECORDS_JSONL] = corpus_payload["public_artifact_identity_records_body"]
        bundle_payload[PUBLIC_EVIDENCE_SUMMARY_JSONL] = corpus_payload["public_artifact_evidence_summary_body"]
    leakage_errors = []
    for name, body in bundle_payload.items():
        leakage_errors.extend(_leakage_errors(name, body))
    if leakage_errors:
        raise ValueError("public staging bundle would leak private content: " + "; ".join(leakage_errors))

    output.mkdir(parents=True, exist_ok=True)
    expected_files = REQUIRED_BUNDLE_FILES | (CORPUS_BUNDLE_FILES if corpus_path else frozenset())
    for stale in output.iterdir():
        if stale.is_file() and stale.name not in expected_files:
            stale.unlink()
    for name, body in bundle_payload.items():
        (output / name).write_bytes(body.encode("utf-8"))
    return bundle_status(output)


def validate_bundle(bundle_dir: str | Path) -> list[str]:
    bundle = Path(bundle_dir)
    errors: list[str] = []
    if not bundle.is_dir():
        return [f"bundle directory not found: {bundle}"]

    present_files = {path.name for path in bundle.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_BUNDLE_FILES - present_files)
    extra = sorted(present_files - ALLOWED_BUNDLE_FILES)
    errors.extend(f"missing required bundle file: {name}" for name in missing)
    errors.extend(f"unexpected private or unsupported bundle file: {name}" for name in extra)
    if missing:
        return errors

    manifest = _read_json(bundle / MANIFEST_FILE, errors, "manifest")
    public_index = _read_json(bundle / PUBLIC_INDEX_FILE, errors, "public index")
    runtime_config = _read_json(bundle / RUNTIME_CONFIG_FILE, errors, "runtime config")
    if errors:
        return errors
    if not isinstance(manifest, Mapping) or not isinstance(public_index, Mapping) or not isinstance(runtime_config, Mapping):
        return errors + ["bundle JSON roots must be objects"]

    corpus_present = bool(present_files & CORPUS_BUNDLE_FILES)
    if corpus_present and not CORPUS_BUNDLE_FILES <= present_files:
        missing_corpus = sorted(CORPUS_BUNDLE_FILES - present_files)
        errors.extend(f"missing corpus closeout bundle file: {name}" for name in missing_corpus)
    corpus_closeout = _read_json(bundle / CORPUS_CLOSEOUT_FILE, errors, "corpus gate closeout") if CORPUS_CLOSEOUT_FILE in present_files else {}
    corpus_records = _read_jsonl(bundle / PUBLIC_ARTIFACT_RECORDS_JSONL, errors, "public artifact identity records") if PUBLIC_ARTIFACT_RECORDS_JSONL in present_files else []
    corpus_summaries = _read_jsonl(bundle / PUBLIC_EVIDENCE_SUMMARY_JSONL, errors, "public artifact evidence summary") if PUBLIC_EVIDENCE_SUMMARY_JSONL in present_files else []
    errors.extend(_validate_manifest(manifest, public_index, runtime_config, bundle, corpus_closeout, corpus_records, corpus_summaries))
    errors.extend(_validate_runtime_config(runtime_config))
    errors.extend(_validate_public_index(public_index))

    for name in present_files & ALLOWED_BUNDLE_FILES:
        errors.extend(_leakage_errors(name, (bundle / name).read_text(encoding="utf-8")))
    return errors


def bundle_status(bundle_dir: str | Path) -> dict[str, Any]:
    bundle = Path(bundle_dir)
    errors = validate_bundle(bundle)
    payload: dict[str, Any] = {
        "schema_version": "eureka.local_staging_status.v0",
        "task_id": TASK_ID,
        "status": "pass" if not errors else "fail",
        "bundle_schema_version": "",
        "bundle_id": "",
        "public_alpha_mode": False,
        "read_only": False,
        "live_metadata_enabled": False,
        "public_live_fanout": False,
        "workbench_exposed": False,
        "workbench_enabled": False,
        "mutation_enabled": False,
        "document_count": 0,
        "status_counts": {},
        "reviewed_record_count": 0,
        "artifact_verified_count": 0,
        "public_search_index_artifact_verified_count": 0,
        "corpus_gate_status": "not_packaged",
        "reviewed_artifact_gate_count": 0,
        "public_artifact_identity_record_count": 0,
        "public_artifact_evidence_summary_count": 0,
        "verification_scope_counts": {},
        "binary_verified_count": 0,
        "download_safe_count": 0,
        "execution_safe_count": 0,
        "rights_cleared_count": 0,
        "artifact_identity_metadata_only": False,
        "corpus_gate_closeout_digest": "",
        "public_artifact_identity_records_digest": "",
        "public_artifact_evidence_summary_digest": "",
        "public_index_digest": "",
        "runtime_config_digest": "",
        "files": sorted(REQUIRED_BUNDLE_FILES),
        "validation_errors": errors,
    }
    manifest_path = bundle / MANIFEST_FILE
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = {}
        if isinstance(manifest, Mapping):
            payload.update(
                {
                    "bundle_schema_version": str(manifest.get("bundle_schema_version") or ""),
                    "bundle_id": str(manifest.get("bundle_id") or ""),
                    "public_alpha_mode": bool(manifest.get("public_alpha_mode") is True),
                    "read_only": bool(manifest.get("read_only") is True),
                    "live_metadata_enabled": bool(manifest.get("live_metadata_enabled") is True),
                    "public_live_fanout": bool(manifest.get("public_live_fanout") is True),
                    "workbench_exposed": bool(manifest.get("workbench_exposed") is True),
                    "workbench_enabled": bool(manifest.get("workbench_enabled") is True),
                    "mutation_enabled": bool(manifest.get("mutation_enabled") is True),
                    "document_count": int(manifest.get("document_count") or 0),
                    "status_counts": dict(manifest.get("status_counts") or {}),
                    "reviewed_record_count": int(manifest.get("reviewed_record_count") or 0),
                    "artifact_verified_count": int(manifest.get("artifact_verified_count") or 0),
                    "public_search_index_artifact_verified_count": int(manifest.get("public_search_index_artifact_verified_count") or 0),
                    "corpus_gate_status": str(manifest.get("corpus_gate_status") or "not_packaged"),
                    "reviewed_artifact_gate_count": int(manifest.get("reviewed_artifact_gate_count") or 0),
                    "public_artifact_identity_record_count": int(manifest.get("public_artifact_identity_record_count") or 0),
                    "public_artifact_evidence_summary_count": int(manifest.get("public_artifact_evidence_summary_count") or 0),
                    "verification_scope_counts": dict(manifest.get("verification_scope_counts") or {}),
                    "binary_verified_count": int(manifest.get("binary_verified_count") or 0),
                    "download_safe_count": int(manifest.get("download_safe_count") or 0),
                    "execution_safe_count": int(manifest.get("execution_safe_count") or 0),
                    "rights_cleared_count": int(manifest.get("rights_cleared_count") or 0),
                    "artifact_identity_metadata_only": bool(manifest.get("artifact_identity_metadata_only") is True),
                    "corpus_gate_closeout_digest": str(manifest.get("corpus_gate_closeout_digest") or ""),
                    "public_artifact_identity_records_digest": str(manifest.get("public_artifact_identity_records_digest") or ""),
                    "public_artifact_evidence_summary_digest": str(manifest.get("public_artifact_evidence_summary_digest") or ""),
                    "public_index_digest": str(manifest.get("public_index_digest") or ""),
                    "runtime_config_digest": str(manifest.get("runtime_config_digest") or ""),
                    "files": sorted((manifest.get("files") or {}).values()) if isinstance(manifest.get("files"), Mapping) else sorted(REQUIRED_BUNDLE_FILES),
                }
            )
    return payload


def public_index_path(bundle_dir: str | Path) -> Path:
    return Path(bundle_dir) / PUBLIC_INDEX_FILE


def bundle_id(bundle_dir: str | Path) -> str:
    status = bundle_status(bundle_dir)
    return str(status.get("bundle_id") or "")


def public_safe_index(index: Mapping[str, Any]) -> dict[str, Any]:
    public_index = copy.deepcopy(dict(index))
    public_index["source"] = "public_alpha_staging_bundle"
    public_index["source_manifest"] = {
        "source_kind": "public_safe_reviewed_index",
        "private_review_artifacts_included": False,
        "local_paths_redacted": True,
    }
    public_index["reviewed_records_source"] = ""
    public_index["deterministic_build"] = True

    documents = []
    for document in public_index.get("documents") or []:
        if isinstance(document, Mapping):
            documents.append(_public_document(document))
    public_index["documents"] = documents
    public_index["document_count"] = len(documents)
    public_index["status_counts"] = _counts(doc.get("status") for doc in documents)
    public_index["source_family_counts"] = _counts(doc.get("source_family") for doc in documents)
    public_index["reviewed_record_count"] = sum(1 for doc in documents if doc.get("record_state") == "reviewed")
    public_index["review_state_counts"] = _counts(doc.get("review_state") for doc in documents if doc.get("review_state"))
    public_index["artifact_verified_count"] = sum(1 for doc in documents if doc.get("artifact_verified") is True)
    public_index["source_digest"] = ""
    public_index["source_digest"] = _stable_digest(public_index)
    return public_index


def public_runtime_config() -> dict[str, Any]:
    return {
        "runtime_config_schema_version": RUNTIME_CONFIG_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "public_alpha_mode": True,
        "read_only": True,
        "metadata_fallback": "none",
        "live_metadata_enabled": False,
        "network_used": False,
        "workbench_enabled": False,
        "workbench_exposed": False,
        "public_live_fanout": False,
        "downloads_enabled": False,
        "file_fetching_enabled": False,
        "wayback_replay_enabled": False,
        "extraction_enabled": False,
        "install_emulation_enabled": False,
        "marketplace_enabled": False,
        "mutation_enabled": False,
        "public_mutation_enabled": False,
        "safe_actions": list(SAFE_ACTIONS),
    }


def render_status_text(status: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            f"status: {status.get('status')}",
            f"bundle_schema_version: {status.get('bundle_schema_version')}",
            f"bundle_id: {status.get('bundle_id')}",
            f"document_count: {status.get('document_count')}",
            f"status_counts: {json.dumps(status.get('status_counts') or {}, sort_keys=True)}",
            f"reviewed_record_count: {status.get('reviewed_record_count')}",
            f"artifact_verified_count: {status.get('artifact_verified_count')}",
            f"corpus_gate_status: {status.get('corpus_gate_status')}",
            f"reviewed_artifact_gate_count: {status.get('reviewed_artifact_gate_count')}",
            f"public_artifact_identity_record_count: {status.get('public_artifact_identity_record_count')}",
            f"verification_scope_counts: {json.dumps(status.get('verification_scope_counts') or {}, sort_keys=True)}",
            f"binary_verified_count: {status.get('binary_verified_count')}",
            f"download_safe_count: {status.get('download_safe_count')}",
            f"execution_safe_count: {status.get('execution_safe_count')}",
            f"rights_cleared_count: {status.get('rights_cleared_count')}",
            f"read_only: {str(status.get('read_only')).lower()}",
            f"live_metadata_enabled: {str(status.get('live_metadata_enabled')).lower()}",
            f"workbench_exposed: {str(status.get('workbench_exposed')).lower()}",
            f"public_live_fanout: {str(status.get('public_live_fanout')).lower()}",
            f"mutation_enabled: {str(status.get('mutation_enabled')).lower()}",
            f"public_index_digest: {status.get('public_index_digest')}",
            f"runtime_config_digest: {status.get('runtime_config_digest')}",
            f"validation_errors: {json.dumps(status.get('validation_errors') or [])}",
        ]
    ) + "\n"


def _public_document(document: Mapping[str, Any]) -> dict[str, Any]:
    blocked_keys = {
        "reviewer",
        "review_reason",
        "reviewed_at",
    }
    sanitized = {
        str(key): _sanitize_value(value, drop_urls=str(key) in {"source_hints"})
        for key, value in document.items()
        if str(key) not in blocked_keys
    }
    provenance = sanitized.get("provenance") if isinstance(sanitized.get("provenance"), Mapping) else {}
    sanitized["provenance"] = {
        str(key): value
        for key, value in provenance.items()
        if str(key) not in {"source_ref", "ledger_path", "records_path", "index_path"}
    }
    sanitized["provenance"]["source_kind"] = _sanitize_text(provenance.get("source_kind") or "public_safe_index")
    sanitized["provenance"]["local_paths_redacted"] = True
    sanitized["artifact_verified"] = bool(sanitized.get("artifact_verified") is True)
    sanitized["accepted_truth"] = bool(sanitized.get("accepted_truth") is True)
    sanitized["verified"] = bool(sanitized.get("verified") is True)
    return sanitized


def _sanitize_value(value: Any, *, drop_urls: bool = False) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _sanitize_value(item, drop_urls=drop_urls) for key, item in value.items()}
    if isinstance(value, list):
        cleaned = [_sanitize_value(item, drop_urls=drop_urls) for item in value]
        return [item for item in cleaned if not (drop_urls and isinstance(item, str) and _looks_like_url(item))]
    if isinstance(value, tuple):
        cleaned = [_sanitize_value(item, drop_urls=drop_urls) for item in value]
        return [item for item in cleaned if not (drop_urls and isinstance(item, str) and _looks_like_url(item))]
    if isinstance(value, str):
        text = _sanitize_text(value)
        if drop_urls and _looks_like_url(text):
            return ""
        return text
    return value


def _sanitize_text(value: Any) -> str:
    text = str(value or "")
    text = text.replace("\\", "/")
    for marker in FORBIDDEN_BUNDLE_MARKERS:
        text = text.replace(marker, "[redacted]")
    parts = [part for part in text.split("/") if part not in {"Users", "Jules", "Projects", "Eureka", "eureka"}]
    return "/".join(parts)


def _validate_manifest(
    manifest: Mapping[str, Any],
    public_index: Mapping[str, Any],
    runtime_config: Mapping[str, Any],
    bundle: Path,
    corpus_closeout: Mapping[str, Any],
    corpus_records: Sequence[Mapping[str, Any]],
    corpus_summaries: Sequence[Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    expected_bools = {
        "public_alpha_mode": True,
        "read_only": True,
        "live_metadata_enabled": False,
        "public_live_fanout": False,
        "workbench_exposed": False,
        "workbench_enabled": False,
        "downloads_enabled": False,
        "file_fetching_enabled": False,
        "wayback_replay_enabled": False,
        "extraction_enabled": False,
        "install_emulation_enabled": False,
        "marketplace_enabled": False,
        "mutation_enabled": False,
        "public_mutation_enabled": False,
        "private_review_artifacts_included": False,
        "local_paths_included": False,
        "deterministic_package": True,
    }
    if manifest.get("bundle_schema_version") != BUNDLE_SCHEMA_VERSION:
        errors.append(f"manifest.bundle_schema_version must be {BUNDLE_SCHEMA_VERSION}")
    for key, expected in expected_bools.items():
        if bool(manifest.get(key) is True) != expected:
            errors.append(f"manifest.{key} must be {str(expected).lower()}")
    stats = stats_payload(public_index)
    if int(manifest.get("document_count") or 0) != stats["document_count"]:
        errors.append("manifest.document_count must match public index")
    if dict(manifest.get("status_counts") or {}) != stats["status_counts"]:
        errors.append("manifest.status_counts must match public index")
    if int(manifest.get("reviewed_record_count") or 0) != stats["reviewed_record_count"]:
        errors.append("manifest.reviewed_record_count must match public index")
    if int(manifest.get("public_search_index_artifact_verified_count") or 0) != stats["artifact_verified_count"]:
        errors.append("manifest.public_search_index_artifact_verified_count must match public index")
    corpus_packaged = bool(corpus_closeout)
    if not corpus_packaged:
        if int(manifest.get("artifact_verified_count") or 0) != stats["artifact_verified_count"]:
            errors.append("manifest.artifact_verified_count must match public index when no corpus closeout is packaged")
        if str(manifest.get("corpus_gate_status") or "not_packaged") != "not_packaged":
            errors.append("manifest.corpus_gate_status must be not_packaged when no corpus closeout is packaged")
    else:
        errors.extend(_validate_corpus_manifest(manifest, corpus_closeout, corpus_records, corpus_summaries, bundle))
    if str(manifest.get("public_index_digest") or "") != _file_sha256(bundle / PUBLIC_INDEX_FILE):
        errors.append("manifest.public_index_digest must match public_search_index.json")
    if str(manifest.get("runtime_config_digest") or "") != _file_sha256(bundle / RUNTIME_CONFIG_FILE):
        errors.append("manifest.runtime_config_digest must match public_runtime_config.json")
    if runtime_config.get("metadata_fallback") != "none":
        errors.append("runtime config metadata_fallback must be none")
    return errors


def _validate_corpus_manifest(
    manifest: Mapping[str, Any],
    corpus_closeout: Mapping[str, Any],
    corpus_records: Sequence[Mapping[str, Any]],
    corpus_summaries: Sequence[Mapping[str, Any]],
    bundle: Path,
) -> list[str]:
    errors: list[str] = []
    if corpus_closeout.get("corpus_gate_status") != "pass":
        errors.append("corpus_gate_closeout.corpus_gate_status must be pass")
    comparisons = (
        "corpus_gate_status",
        "reviewed_artifact_gate_count",
        "artifact_verified_count",
        "public_artifact_identity_record_count",
        "public_artifact_evidence_summary_count",
        "binary_verified_count",
        "download_safe_count",
        "execution_safe_count",
        "rights_cleared_count",
    )
    for key in comparisons:
        if manifest.get(key) != corpus_closeout.get(key):
            errors.append(f"manifest.{key} must match corpus gate closeout")
    if dict(manifest.get("verification_scope_counts") or {}) != dict(corpus_closeout.get("verification_scope_counts") or {}):
        errors.append("manifest.verification_scope_counts must match corpus gate closeout")
    if int(manifest.get("artifact_verified_count") or 0) != len(corpus_records):
        errors.append("manifest.artifact_verified_count must match public artifact identity records")
    if int(manifest.get("public_artifact_evidence_summary_count") or 0) != len(corpus_summaries):
        errors.append("manifest.public_artifact_evidence_summary_count must match public evidence summaries")
    if int(manifest.get("binary_verified_count") or 0) != 0:
        errors.append("manifest.binary_verified_count must remain 0")
    if int(manifest.get("download_safe_count") or 0) != 0:
        errors.append("manifest.download_safe_count must remain 0")
    if int(manifest.get("execution_safe_count") or 0) != 0:
        errors.append("manifest.execution_safe_count must remain 0")
    if int(manifest.get("rights_cleared_count") or 0) != 0:
        errors.append("manifest.rights_cleared_count must remain 0")
    if manifest.get("artifact_identity_metadata_only") is not True:
        errors.append("manifest.artifact_identity_metadata_only must be true with corpus closeout")
    if str(manifest.get("corpus_gate_closeout_digest") or "") != _file_sha256(bundle / CORPUS_CLOSEOUT_FILE):
        errors.append("manifest.corpus_gate_closeout_digest must match corpus_gate_closeout.json")
    if str(manifest.get("public_artifact_identity_records_digest") or "") != _file_sha256(bundle / PUBLIC_ARTIFACT_RECORDS_JSONL):
        errors.append("manifest.public_artifact_identity_records_digest must match public_artifact_identity_records.jsonl")
    if str(manifest.get("public_artifact_evidence_summary_digest") or "") != _file_sha256(bundle / PUBLIC_EVIDENCE_SUMMARY_JSONL):
        errors.append("manifest.public_artifact_evidence_summary_digest must match public_artifact_evidence_summary.jsonl")
    for index, record in enumerate(corpus_records, start=1):
        for key in ("binary_verified", "download_safe", "execution_safe", "rights_cleared"):
            if record.get(key) is True:
                errors.append(f"public artifact identity record[{index}].{key} cannot be true")
    for index, summary in enumerate(corpus_summaries, start=1):
        for key in ("binary_verified", "download_safe", "execution_safe", "rights_cleared"):
            if summary.get(key) is True:
                errors.append(f"public evidence summary[{index}].{key} cannot be true")
    return errors


def _validate_runtime_config(config: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if config.get("runtime_config_schema_version") != RUNTIME_CONFIG_SCHEMA_VERSION:
        errors.append(f"runtime_config_schema_version must be {RUNTIME_CONFIG_SCHEMA_VERSION}")
    expected = public_runtime_config()
    for key, expected_value in expected.items():
        if key == "safe_actions":
            if list(config.get(key) or []) != list(SAFE_ACTIONS):
                errors.append("runtime_config.safe_actions must be read-only")
            continue
        if config.get(key) != expected_value:
            errors.append(f"runtime_config.{key} must be {expected_value!r}")
    return errors


def _validate_public_index(index: Mapping[str, Any]) -> list[str]:
    errors = validate_index(index)
    if str(index.get("reviewed_records_source") or ""):
        errors.append("public index must not expose reviewed_records_source")
    for document in index.get("documents") or []:
        if not isinstance(document, Mapping):
            continue
        for hint in document.get("source_hints") or []:
            if isinstance(hint, str) and _looks_like_url(hint):
                errors.append(f"{document.get('id')}: public source_hints must not expose direct URLs")
    return errors


def _corpus_payload(corpus_path: Path) -> dict[str, Any]:
    errors = validate_closeout(corpus_path)
    if errors:
        raise ValueError("corpus gate closeout is invalid: " + "; ".join(errors))
    closeout_path = corpus_path / CORPUS_CLOSEOUT_FILE
    records_path = corpus_path / PUBLIC_ARTIFACT_RECORDS_JSONL
    summaries_path = corpus_path / PUBLIC_EVIDENCE_SUMMARY_JSONL
    closeout = json.loads(closeout_path.read_text(encoding="utf-8"))
    records_body = records_path.read_text(encoding="utf-8")
    summaries_body = summaries_path.read_text(encoding="utf-8")
    closeout_body = _stable_json(closeout)
    return {
        "corpus_gate_status": str(closeout.get("corpus_gate_status") or "unknown"),
        "reviewed_artifact_gate_count": int(closeout.get("reviewed_artifact_gate_count") or 0),
        "artifact_verified_count": int(closeout.get("artifact_verified_count") or 0),
        "public_artifact_identity_record_count": int(closeout.get("public_artifact_identity_record_count") or 0),
        "public_artifact_evidence_summary_count": int(closeout.get("public_artifact_evidence_summary_count") or 0),
        "verification_scope_counts": dict(closeout.get("verification_scope_counts") or {}),
        "binary_verified_count": int(closeout.get("binary_verified_count") or 0),
        "download_safe_count": int(closeout.get("download_safe_count") or 0),
        "execution_safe_count": int(closeout.get("execution_safe_count") or 0),
        "rights_cleared_count": int(closeout.get("rights_cleared_count") or 0),
        "corpus_gate_closeout_digest": _sha256_text(closeout_body),
        "public_artifact_identity_records_digest": _sha256_text(records_body),
        "public_artifact_evidence_summary_digest": _sha256_text(summaries_body),
        "corpus_gate_closeout_body": closeout_body,
        "public_artifact_identity_records_body": records_body,
        "public_artifact_evidence_summary_body": summaries_body,
    }


def _empty_corpus_payload() -> dict[str, Any]:
    return {
        "corpus_gate_status": "not_packaged",
        "reviewed_artifact_gate_count": 0,
        "artifact_verified_count": 0,
        "public_artifact_identity_record_count": 0,
        "public_artifact_evidence_summary_count": 0,
        "verification_scope_counts": {},
        "binary_verified_count": 0,
        "download_safe_count": 0,
        "execution_safe_count": 0,
        "rights_cleared_count": 0,
    }


def _read_json(path: Path, errors: list[str], label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        errors.append(f"{label} could not be read: {type(exc).__name__}")
    except json.JSONDecodeError as exc:
        errors.append(f"{label} is invalid JSON: {exc.msg}")
    return {}


def _read_jsonl(path: Path, errors: list[str], label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            loaded = json.loads(line)
            if isinstance(loaded, dict):
                rows.append(loaded)
            else:
                errors.append(f"{label} contains a non-object JSONL row")
    except OSError as exc:
        errors.append(f"{label} could not be read: {type(exc).__name__}")
    except json.JSONDecodeError as exc:
        errors.append(f"{label} is invalid JSONL: {exc.msg}")
    return rows


def _leakage_errors(name: str, body: str) -> list[str]:
    errors = []
    lowered = body.lower()
    for marker in FORBIDDEN_BUNDLE_MARKERS:
        if marker.lower() in lowered:
            errors.append(f"{name} contains forbidden marker {marker}")
    if _WINDOWS_ABSOLUTE_PATH.search(body):
        errors.append(f"{name} contains a Windows absolute path")
    if "/Users/" in body or "\\Users\\" in body:
        errors.append(f"{name} contains a user-home path")
    return errors


def _counts(values: Sequence[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value or "unknown")
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _stable_digest(value: Mapping[str, Any]) -> str:
    return _sha256_text(_stable_json(value))


def _stable_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _looks_like_url(value: str) -> bool:
    text = value.strip().casefold()
    return text.startswith("http://") or text.startswith("https://")


def _git_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return ""
    return result.stdout.strip()
