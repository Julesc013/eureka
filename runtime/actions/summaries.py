"""Summary helpers for J0 action artifacts."""

from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence


def summarize_action_records(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    schemas = Counter(str(record.get("schema_version", "unknown")) for record in records)
    actions = Counter(str(record.get("action_family", record.get("blocked_action_family", "none"))) for record in records)
    blocked = sum(1 for record in records if record.get("action_status") == "blocked_by_policy" or record.get("schema_version") == "blocked_action_report.v0")
    return {
        "schema_version": "action_summary.v0",
        "record_count": len(records),
        "schema_counts": dict(sorted(schemas.items())),
        "action_family_counts": dict(sorted(actions.items())),
        "blocked_record_count": blocked,
        "download_enabled": False,
        "mirror_enabled": False,
        "install_enabled": False,
        "execute_enabled": False,
        "emulate_enabled": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def format_action_summary(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Action Manifest Summary",
        "",
        f"- Records: {summary.get('record_count', 0)}",
        f"- Blocked records: {summary.get('blocked_record_count', 0)}",
        f"- Download enabled: {str(summary.get('download_enabled', False)).lower()}",
        f"- Mirror enabled: {str(summary.get('mirror_enabled', False)).lower()}",
        f"- Install enabled: {str(summary.get('install_enabled', False)).lower()}",
        f"- Execute enabled: {str(summary.get('execute_enabled', False)).lower()}",
        f"- Emulate enabled: {str(summary.get('emulate_enabled', False)).lower()}",
        f"- Public index mutated: {str(summary.get('public_index_mutated', False)).lower()}",
        f"- Master index mutated: {str(summary.get('master_index_mutated', False)).lower()}",
    ]
    return "\n".join(lines) + "\n"
