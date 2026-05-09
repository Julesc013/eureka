"""Relay runtime summaries for audits and scripts."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping


def summarize_relay_artifacts(items: Iterable[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    schemas = Counter(str(item.get("schema_version", "unknown")) for item in items)
    blocked = 0
    for item in items:
        status = str(item.get("route_status", item.get("relay_profile_status", item.get("status_code", "")))).casefold()
        if "blocked" in status or item.get("status_code") == 403:
            blocked += 1
    return {
        "schema_version": "relay_summary.v0",
        "artifact_count": sum(schemas.values()),
        "schema_counts": dict(sorted(schemas.items())),
        "blocked_artifact_count": blocked,
        "localhost_readonly_enabled": True,
        "public_bind_allowed": False,
        "write_routes_enabled": False,
        "downloads_enabled": False,
        "action_execution_enabled": False,
        "accounts_enabled": False,
        "telemetry_enabled": False,
    }


def summarize_relay_artifacts_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Relay Runtime Summary",
        "",
        "D-BUNDLE-02 relay artifacts are fixture-only, localhost-only, and read-only.",
        "",
        f"- Artifact count: {summary.get('artifact_count', 0)}",
        f"- Blocked artifacts: {summary.get('blocked_artifact_count', 0)}",
        "- Public bind: false",
        "- Write routes: false",
        "- Downloads: false",
        "- Action execution: false",
        "- Accounts: false",
        "- Telemetry: false",
        "",
        "## Schema Counts",
    ]
    for schema, count in sorted((summary.get("schema_counts") or {}).items()):
        lines.append(f"- {schema}: {count}")
    return "\n".join(lines) + "\n"

