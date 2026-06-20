"""Redacted local observability for live discovery."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import tempfile
import time
from typing import Any, Iterable, Mapping, Sequence


EVENT_TYPES = {
    "search_started",
    "search_completed",
    "provider_request_started",
    "provider_request_completed",
    "provider_rate_limited",
    "provider_failed",
    "hunt_started",
    "hunt_paused",
    "hunt_resumed",
    "hunt_cancelled",
    "hunt_completed",
    "fetch_started",
    "fetch_blocked",
    "fetch_failed",
    "fetch_completed",
    "observation_created",
    "preview_document_indexed",
    "duplicate_detected",
    "index_generation_activated",
    "foundry_started",
    "foundry_checkpointed",
    "foundry_completed",
    "circuit_breaker_opened",
    "circuit_breaker_closed",
}

ERROR_CATEGORIES = {
    "configuration",
    "provider_auth",
    "provider_rate_limit",
    "provider_timeout",
    "provider_response",
    "DNS",
    "SSRF",
    "robots",
    "redirect",
    "TLS",
    "MIME",
    "size",
    "decompression",
    "extraction",
    "index",
    "migration",
    "storage",
    "budget",
    "cancelled",
    "internal",
}

FORBIDDEN_KEYS = {
    "api_key",
    "authorization",
    "cookie",
    "credential",
    "headers",
    "password",
    "provider_rank",
    "rank",
    "raw",
    "raw_response",
    "secret",
    "snippet",
    "text",
    "token",
    "url",
}


@dataclass(frozen=True)
class TimedOperation:
    started: float

    @staticmethod
    def start() -> "TimedOperation":
        return TimedOperation(started=time.monotonic())

    def elapsed_ms(self) -> int:
        return max(0, int((time.monotonic() - self.started) * 1000))


class DiscoveryEventStore:
    """Append-only JSONL event store for safe aggregate discovery diagnostics."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, event: Mapping[str, Any]) -> dict[str, Any]:
        safe = sanitize_event(event)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(safe, sort_keys=True) + "\n")
        return safe

    def record(self, event_type: str, *, run_id: str = "", component: str = "search", **fields: Any) -> dict[str, Any]:
        payload = {
            "event_type": event_type,
            "run_id": run_id,
            "component": component,
            **fields,
        }
        return self.append(payload)

    def read(self, *, run_id: str | None = None, limit: int = 500) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if run_id and str(payload.get("run_id") or "") != str(run_id):
                continue
            rows.append(dict(payload))
        return rows[-max(1, min(int(limit or 500), 5000)) :]


def sanitize_event(event: Mapping[str, Any]) -> dict[str, Any]:
    event_type = _event_type(str(event.get("event_type") or "internal"))
    run_id = str(event.get("run_id") or "")
    timestamp = str(event.get("timestamp") or _now())
    component = str(event.get("component") or _component_for_event(event_type))
    cleaned: dict[str, Any] = {
        "schema_version": "eureka.discovery_event.v0",
        "event_id": str(event.get("event_id") or _event_id(event_type, run_id, timestamp, event)),
        "timestamp": timestamp,
        "run_id": run_id,
        "work_unit_id": str(event.get("work_unit_id") or event.get("workunit_id") or ""),
        "event_type": event_type,
        "component": component,
        "provider": str(event.get("provider") or event.get("source_family") or ""),
        "duration_ms": _safe_int(event.get("duration_ms"), default=0),
        "count": _safe_int(event.get("count"), default=0),
        "error_category": _error_category(str(event.get("error_category") or event.get("code") or "")),
        "policy_outcome": str(event.get("policy_outcome") or event.get("status") or ""),
    }
    for key, value in event.items():
        normalized = str(key).strip().casefold()
        if normalized in cleaned or _forbidden_key(normalized):
            continue
        if normalized in {"query", "query_variant"}:
            cleaned[f"{normalized}_hash"] = stable_hash(value)
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            cleaned[normalized] = _redact_scalar(value)
        elif isinstance(value, Mapping):
            cleaned[normalized] = _redact_mapping(value)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            cleaned[normalized] = [_redact_scalar(item) if not isinstance(item, Mapping) else _redact_mapping(item) for item in value[:20]]
    return cleaned


def metrics_from_events(events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    durations: dict[str, list[int]] = {}
    providers: dict[str, int] = {}
    for event in events:
        event_type = str(event.get("event_type") or "")
        counts[event_type] = counts.get(event_type, 0) + 1
        provider = str(event.get("provider") or "")
        if provider:
            providers[provider] = providers.get(provider, 0) + 1
        duration = _safe_int(event.get("duration_ms"), default=0)
        if duration > 0:
            durations.setdefault(event_type, []).append(duration)
    provider_requests = max(counts.get("provider_request_started", 0), counts.get("provider_request_completed", 0))
    fetch_attempts = counts.get("fetch_started", 0)
    duplicates = counts.get("duplicate_detected", 0)
    preview_upserts = counts.get("preview_document_indexed", 0)
    return {
        "schema_version": "eureka.discovery_metrics.v0",
        "status": "pass",
        "search_count": counts.get("search_started", 0),
        "search_completed": counts.get("search_completed", 0),
        "provider_requests": provider_requests,
        "provider_failures": counts.get("provider_failed", 0),
        "rate_limits": counts.get("provider_rate_limited", 0),
        "fetch_attempts": fetch_attempts,
        "fetch_successes": counts.get("fetch_completed", 0),
        "robots_blocks": _count_policy(events, "robots"),
        "ssrf_blocks": _count_policy(events, "SSRF"),
        "mime_size_blocks": _count_policy(events, "MIME") + _count_policy(events, "size"),
        "observations_created": counts.get("observation_created", 0),
        "preview_index_upserts": preview_upserts,
        "duplicate_rate": round(duplicates / max(1, duplicates + preview_upserts), 4),
        "hunt_completed": counts.get("hunt_completed", 0),
        "hunt_cancelled": counts.get("hunt_cancelled", 0),
        "foundry_completed": counts.get("foundry_completed", 0),
        "circuit_breaker_state": "open" if counts.get("circuit_breaker_opened", 0) > counts.get("circuit_breaker_closed", 0) else "closed",
        "event_counts": counts,
        "providers": providers,
        "latency_ms": {event_type: _summary(values) for event_type, values in durations.items()},
        "remote_telemetry": False,
        "provider_payload_persisted": False,
        "credential_value_exposed": False,
    }


def export_diagnostic_bundle(
    *,
    run_id: str,
    out_dir: str | Path,
    events: Sequence[Mapping[str, Any]],
    capability_state: Mapping[str, Any] | None = None,
    provider_statuses: Sequence[Mapping[str, Any]] = (),
    run_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    safe_events = [sanitize_event(event) for event in events]
    metrics = metrics_from_events(safe_events)
    summary = {
        "schema_version": "eureka.discovery_diagnostics_export.v0",
        "status": "pass",
        "run_id": str(run_id or ""),
        "event_count": len(safe_events),
        "metrics": metrics,
        "run_summary": _redact_mapping(run_summary or {}),
        "redacted": True,
        "provider_payload_included": False,
        "private_content_included": False,
        "credential_value_exposed": False,
    }
    _write_json(root / "summary.json", summary)
    _write_json(root / "metrics.json", metrics)
    _write_json(root / "provider_capabilities.json", {"providers": [_redact_mapping(item) for item in provider_statuses]})
    _write_json(root / "capability_state.json", _redact_mapping(capability_state or {}))
    _write_json(root / "error_taxonomy.json", {"categories": sorted(ERROR_CATEGORIES)})
    _write_jsonl(root / "events.jsonl", safe_events)
    return {
        "schema_version": "eureka.discovery_diagnostics_export_result.v0",
        "status": "pass",
        "run_id": str(run_id or ""),
        "out_dir": str(root),
        "files": sorted(item.name for item in root.iterdir()),
        "provider_payload_persisted": False,
        "credential_value_exposed": False,
    }


def stable_hash(value: Any) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:16]


def _summary(values: Sequence[int]) -> dict[str, int]:
    ordered = sorted(int(value) for value in values)
    if not ordered:
        return {"p50": 0, "p95": 0, "p99": 0}
    return {"p50": _percentile(ordered, 50), "p95": _percentile(ordered, 95), "p99": _percentile(ordered, 99)}


def _percentile(values: Sequence[int], pct: int) -> int:
    index = min(len(values) - 1, max(0, int(round((pct / 100) * (len(values) - 1)))))
    return int(values[index])


def _count_policy(events: Sequence[Mapping[str, Any]], category: str) -> int:
    return sum(1 for event in events if str(event.get("error_category") or "") == category or str(event.get("policy_outcome") or "") == category)


def _event_type(value: str) -> str:
    if value == "document_indexed":
        return "preview_document_indexed"
    if value == "duplicate_removed":
        return "duplicate_detected"
    if value == "provider_request_failed":
        return "provider_failed"
    if value == "provider_results_received":
        return "provider_request_completed"
    return value if value in EVENT_TYPES else "internal"


def _component_for_event(event_type: str) -> str:
    if event_type.startswith("provider_"):
        return "provider"
    if event_type.startswith("fetch_") or event_type == "observation_created":
        return "fetch"
    if event_type.startswith("hunt_"):
        return "hunt"
    if event_type.startswith("foundry_") or event_type.startswith("circuit_breaker_"):
        return "foundry"
    if event_type.startswith("index_") or event_type == "preview_document_indexed":
        return "preview_index"
    return "search"


def _error_category(value: str) -> str:
    text = str(value or "").strip()
    lowered = text.casefold()
    if not text:
        return ""
    if "rate" in lowered:
        return "provider_rate_limit"
    if "timeout" in lowered:
        return "provider_timeout"
    if "auth" in lowered or "credential" in lowered:
        return "provider_auth"
    if "ssrf" in lowered or "private" in lowered:
        return "SSRF"
    if "robot" in lowered:
        return "robots"
    if "mime" in lowered:
        return "MIME"
    if "size" in lowered:
        return "size"
    if text in ERROR_CATEGORIES:
        return text
    return "internal"


def _forbidden_key(key: str) -> bool:
    return any(part in FORBIDDEN_KEYS for part in key.replace("-", "_").split("_")) or key in FORBIDDEN_KEYS


def _redact_mapping(payload: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in payload.items():
        normalized = str(key).strip().casefold()
        if _forbidden_key(normalized):
            result[normalized] = "[redacted]"
        elif isinstance(value, Mapping):
            result[normalized] = _redact_mapping(value)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            result[normalized] = [_redact_mapping(item) if isinstance(item, Mapping) else _redact_scalar(item) for item in value[:50]]
        else:
            result[normalized] = _redact_scalar(value)
    return result


def _redact_scalar(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    redacted = value
    for env_name in ("BRAVE_SEARCH_API_KEY", "BRAVE_API_KEY", "EUREKA_OPERATOR_TOKEN"):
        secret = os.environ.get(env_name)
        if secret:
            redacted = redacted.replace(secret, "[redacted]")
    return redacted


def _safe_int(value: Any, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _event_id(event_type: str, run_id: str, timestamp: str, event: Mapping[str, Any]) -> str:
    return "event:" + hashlib.sha256(json.dumps(_redact_mapping({**dict(event), "event_type": event_type, "run_id": run_id, "timestamp": timestamp}), sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    _atomic_write(path, json.dumps(dict(payload), indent=2, sort_keys=True) + "\n")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    _atomic_write(path, "\n".join(json.dumps(dict(row), sort_keys=True) for row in rows) + "\n")


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
        handle.write(text)
        temp = Path(handle.name)
    temp.replace(path)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
