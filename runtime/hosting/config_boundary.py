"""Runtime config boundary helpers for local hosting rehearsal."""

from __future__ import annotations

RISKY_CONFIG_KEYS = {
    "LIVE_PROBES_ENABLED",
    "SOURCE_SYNC_ENABLED",
    "CONNECTOR_IA_ENABLED",
    "CONNECTOR_H1_ENABLED",
    "DOWNLOADS_ENABLED",
    "UPLOADS_ENABLED",
    "ACCOUNTS_ENABLED",
    "TELEMETRY_ENABLED",
    "PUBLIC_INDEX_WRITE_ENABLED",
    "MASTER_INDEX_WRITE_ENABLED",
    "RELAY_PUBLIC_BIND_ENABLED",
}


def load_runtime_config_boundaries(policy: dict | None) -> list[dict]:
    payload = policy or {}
    if "config_boundaries" in payload:
        return list(payload["config_boundaries"])
    return list(payload.get("boundaries", []))


def validate_runtime_config_defaults(boundaries: list[dict], policy: dict | None = None) -> dict:
    errors: list[str] = []
    for entry in boundaries:
        key = entry.get("config_key")
        if entry.get("fail_closed_default") is not True:
            errors.append(f"{key}: fail_closed_default must be true")
        if key in RISKY_CONFIG_KEYS and str(entry.get("safe_default")).casefold() != "false":
            errors.append(f"{key}: risky default must be false")
    return {"schema_version": "runtime_config_default_check.v0", "status": "fail" if errors else "pass", "errors": errors}


def assert_risky_defaults_disabled(boundaries: list[dict], policy: dict | None = None) -> bool:
    report = validate_runtime_config_defaults(boundaries, policy)
    if report["errors"]:
        raise ValueError("; ".join(report["errors"]))
    return True
