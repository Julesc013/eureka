#!/usr/bin/env python3
"""Report Connector Approval and Runtime Planning Audit v0 status."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO_ROOT / "control" / "audits" / "connector-approval-runtime-planning-audit-v0" / "connector_approval_runtime_planning_audit_report.json"
INVENTORY_PATH = REPO_ROOT / "control" / "inventory" / "connectors" / "connector_approval_runtime_planning_status.json"


def load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, Mapping):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def build_status() -> dict[str, Any]:
    report = load_json(REPORT_PATH)
    inventory = load_json(INVENTORY_PATH)
    return {
        "status": "ok",
        "report_id": report.get("report_id"),
        "inventory_id": inventory.get("inventory_id"),
        "connector_status_matrix": report.get("connector_status_matrix", {}),
        "aggregate_status": inventory.get("aggregate_status"),
        "hard_booleans": {
            "audit_only": report.get("audit_only"),
            "connector_runtime_implemented_by_this_milestone": report.get("connector_runtime_implemented_by_this_milestone"),
            "live_connector_runtime_enabled": report.get("live_connector_runtime_enabled"),
            "public_search_connector_fanout_enabled": report.get("public_search_connector_fanout_enabled"),
            "external_calls_performed": report.get("external_calls_performed"),
            "live_source_called": report.get("live_source_called"),
            "credentials_configured": report.get("credentials_configured"),
            "tokens_enabled": report.get("tokens_enabled"),
            "downloads_enabled": report.get("downloads_enabled"),
            "installs_enabled": report.get("installs_enabled"),
            "execution_enabled": report.get("execution_enabled"),
            "source_cache_mutated": report.get("source_cache_mutated"),
            "evidence_ledger_mutated": report.get("evidence_ledger_mutated"),
            "candidate_index_mutated": report.get("candidate_index_mutated"),
            "public_index_mutated": report.get("public_index_mutated"),
            "master_index_mutated": report.get("master_index_mutated"),
            "deployment_performed": report.get("deployment_performed"),
            "telemetry_enabled": report.get("telemetry_enabled"),
            "accounts_enabled": report.get("accounts_enabled"),
        },
        "remaining_blockers": report.get("remaining_blockers", []),
        "next_recommended_branch": report.get("next_recommended_branch"),
        "notes": [
            "Read-only report over committed P101 artifacts.",
            "No connector module is imported.",
            "No network, live source, connector runtime, credential, telemetry, or mutation behavior is invoked.",
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    status = build_status()
    if args.json:
        print(json.dumps(status, indent=2, sort_keys=True))
    else:
        print(f"status: {status['status']}")
        print(f"aggregate_status: {status['aggregate_status']}")
        for connector_id, row in status["connector_status_matrix"].items():
            print(f"{connector_id}: {row.get('readiness_decision')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
