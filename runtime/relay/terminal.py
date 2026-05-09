"""Terminal/text menu renderers for relay snapshots."""

from __future__ import annotations

from typing import Any, Mapping, Sequence


def build_terminal_menu(snapshot_store: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    records = [record for record in snapshot_store.get("records", []) if isinstance(record, Mapping)]
    lines = [
        "Eureka Relay Terminal",
        "=====================",
        "Mode: fixture-only localhost read-only",
        "No live access, downloads, uploads, execution, accounts, or telemetry.",
        "",
        "1. Search fixture snapshot",
        "2. View manifest",
        "3. Browse files index",
        "",
        "Records:",
    ]
    for index, record in enumerate(records, start=1):
        lines.append(f"{index}. {record.get('record_type', 'record')} - {record.get('title', record.get('canonical_ref', ''))}")
    lines.append("")
    lines.append("Blocked actions: write, upload, download, execute, live source access, public bind")
    return "\n".join(lines) + "\n"


def render_terminal_search_results(results: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> str:
    lines = [
        "Eureka Relay Search",
        "===================",
        "Fixture results only. No public ranking or live source fanout.",
        "",
    ]
    for index, record in enumerate(results, start=1):
        lines.extend(
            [
                f"{index}. {record.get('title', record.get('canonical_ref', 'Untitled'))}",
                f"   Identity: {record.get('canonical_ref', '')}",
                f"   Source posture: {record.get('source_posture', '')}",
                f"   Evidence posture: {record.get('evidence_posture', '')}",
                f"   Rights posture: {record.get('rights_posture', '')}",
                f"   Risk posture: {record.get('risk_posture', '')}",
                f"   Action posture: {record.get('action_posture', '')}",
                "",
            ]
        )
    return "\n".join(lines)


def render_terminal_object(record: Mapping[str, Any] | None, policy: Mapping[str, Any] | None = None) -> str:
    if not record:
        return "Eureka Relay Object\n===================\nObject not found in fixture snapshot.\n"
    lines = [
        "Eureka Relay Object",
        "===================",
        f"Identity: {record.get('canonical_ref', '')}",
        f"Title: {record.get('title', '')}",
        f"Summary: {record.get('summary', '')}",
        f"Source posture: {record.get('source_posture', '')}",
        f"Evidence posture: {record.get('evidence_posture', '')}",
        f"Rights posture: {record.get('rights_posture', '')}",
        f"Risk posture: {record.get('risk_posture', '')}",
        f"Action posture: {record.get('action_posture', '')}",
        "Limitations/no-claims: no public truth, no downloads, no execution, no index mutation",
        "",
    ]
    return "\n".join(lines)

