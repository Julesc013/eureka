#!/usr/bin/env python3
"""Report Public Search Runtime Integration Audit v0 status from committed artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO_ROOT / "control" / "audits" / "public-search-runtime-integration-audit-v0" / "public_search_runtime_integration_audit_report.json"
INVENTORY_PATH = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_runtime_integration_status.json"


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
        "classification_matrix": report.get("integration_status_matrix", {}),
        "hard_booleans": {
            "audit_only": report.get("audit_only"),
            "runtime_integration_implemented": report.get("runtime_integration_implemented"),
            "public_search_live_source_fanout_enabled": report.get("public_search_live_source_fanout_enabled"),
            "source_cache_dry_run_integrated_with_public_search": report.get("source_cache_dry_run_integrated_with_public_search"),
            "evidence_ledger_dry_run_integrated_with_public_search": report.get("evidence_ledger_dry_run_integrated_with_public_search"),
            "connector_runtime_integrated_with_public_search": report.get("connector_runtime_integrated_with_public_search"),
            "source_cache_mutated": report.get("source_cache_mutated"),
            "evidence_ledger_mutated": report.get("evidence_ledger_mutated"),
            "candidate_index_mutated": report.get("candidate_index_mutated"),
            "public_index_mutated": report.get("public_index_mutated"),
            "master_index_mutated": report.get("master_index_mutated"),
            "external_calls_performed": report.get("external_calls_performed"),
            "live_source_called": report.get("live_source_called"),
            "telemetry_enabled": report.get("telemetry_enabled"),
            "accounts_enabled": report.get("accounts_enabled"),
            "uploads_enabled": report.get("uploads_enabled"),
            "downloads_enabled": report.get("downloads_enabled"),
            "installs_enabled": report.get("installs_enabled"),
            "execution_enabled": report.get("execution_enabled"),
        },
        "remaining_blockers": report.get("remaining_blockers", []),
        "next_recommended_branch": report.get("next_recommended_branch"),
        "notes": [
            "Read-only report over committed P100 artifacts.",
            "No public search server is started.",
            "No network, live source, connector, telemetry, or mutation behavior is invoked.",
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
        for key, value in status["classification_matrix"].items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
