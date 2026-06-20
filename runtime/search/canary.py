"""Operator live canary preflight and sanitized evidence helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


CANARY_EVIDENCE_SCHEMA_VERSION = "eureka.operator_live_canary_evidence.v0"
FORBIDDEN_EVIDENCE_KEYS = {"url", "urls", "snippet", "snippets", "provider_rank", "raw_response", "api_key", "authorization", "cookie"}


def sanitize_canary_evidence(payload: Mapping[str, Any], *, query: str = "", query_label: str = "") -> dict[str, Any]:
    live = payload.get("live_canary") if isinstance(payload.get("live_canary"), Mapping) else {}
    query_hash = hashlib.sha256(str(query or "").encode("utf-8")).hexdigest() if query else ""
    evidence = {
        "schema_version": CANARY_EVIDENCE_SCHEMA_VERSION,
        "status": str(live.get("status") or payload.get("status") or ""),
        "reason": str(live.get("reason") or ""),
        "provider": str(live.get("provider") or ""),
        "query_supplied": bool(live.get("query_supplied") or query),
        "query_hash": query_hash,
        "query_label": str(query_label or ""),
        "live_provider_configured": bool(live.get("live_provider_configured", False)),
        "live_result_count": int(live.get("live_result_count") or 0),
        "queries_attempted": int(live.get("queries_attempted") or 0),
        "transient_lead_count": int(live.get("transient_lead_count") or 0),
        "fetch_attempt_count": int(live.get("fetch_attempt_count") or 0),
        "pages_fetched": int(live.get("pages_fetched") or 0),
        "observations_created": int(live.get("observations_created") or 0),
        "documents_indexed": int(live.get("documents_indexed") or 0),
        "restart_local_search_hits": int(live.get("restart_local_search_hits") or 0),
        "provider_result_payload_persisted": bool(live.get("provider_result_payload_persisted", False)),
        "reviewed_master_mutation": bool(live.get("reviewed_master_mutation", False)),
        "public_index_mutation": bool(live.get("public_index_mutation", False)),
        "credential_value_exposed": False,
        "provider_payload_fields_included": [],
    }
    errors = validate_canary_evidence(evidence)
    evidence["validation_status"] = "pass" if not errors else "fail"
    evidence["validation_errors"] = errors
    return evidence


def validate_canary_evidence(evidence: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if evidence.get("schema_version") != CANARY_EVIDENCE_SCHEMA_VERSION:
        errors.append(f"schema_version must be {CANARY_EVIDENCE_SCHEMA_VERSION}")
    if evidence.get("provider_result_payload_persisted") is not False:
        errors.append("provider result payload must not be persisted")
    if evidence.get("credential_value_exposed") is not False:
        errors.append("credential value must not be exposed")
    if evidence.get("reviewed_master_mutation") is not False:
        errors.append("reviewed/master mutation must be false")
    if evidence.get("public_index_mutation") is not False:
        errors.append("public index mutation must be false")
    forbidden = sorted(FORBIDDEN_EVIDENCE_KEYS.intersection(_keys_recursive(evidence)))
    if forbidden:
        errors.append("forbidden evidence fields present: " + ", ".join(forbidden))
    text = json.dumps(dict(evidence), sort_keys=True)
    if "http://" in text or "https://" in text:
        errors.append("evidence must not include live URLs")
    return errors


def write_canary_evidence(path: str | Path, evidence: Mapping[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(dict(evidence), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def _keys_recursive(value: Any) -> set[str]:
    if isinstance(value, Mapping):
        keys = {str(key).casefold() for key in value.keys()}
        for item in value.values():
            keys.update(_keys_recursive(item))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys.update(_keys_recursive(item))
        return keys
    return set()
