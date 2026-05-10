"""Summary helpers for public alpha readiness rehearsal."""

from __future__ import annotations


def summarize_public_alpha_readiness(payloads: list[dict], policy: dict | None = None) -> dict:
    schema_counts: dict[str, int] = {}
    for payload in payloads:
        version = str(payload.get("schema_version", "unknown"))
        schema_counts[version] = schema_counts.get(version, 0) + 1
    return {
        "schema_version": "public_alpha_readiness_summary.v0",
        "status": "pass",
        "schema_counts": schema_counts,
        "next_phase": "READY_FOR_MVP_ALPHA_AUDIT",
        "scope": {
            "local_fixture_rehearsal": True,
            "deployed_backend": False,
            "deployed_static_site": False,
            "dns_changed": False,
            "site_dist_mutated": False,
            "public_alpha_live_claimed": False,
            "production_claimed": False,
        },
    }


def format_public_alpha_summary(summary: dict) -> str:
    lines = ["# Public Alpha Readiness Summary", "", f"Status: {summary.get('status')}", f"Next phase: {summary.get('next_phase')}"]
    for key, value in sorted(summary.get("schema_counts", {}).items()):
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("Local fixture rehearsal only; no deployment, DNS change, public endpoint, or production claim is present.")
    return "\n".join(lines)
