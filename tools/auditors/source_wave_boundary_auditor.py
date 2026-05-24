#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


UNSAFE_FIELDS = (
    "live_source_call_performed",
    "source_probe_executed",
    "raw_live_source_response_committed",
    "source_cache_write_performed",
    "evidence_write_performed",
    "candidate_index_mutated",
    "reviewed_index_mutated",
    "master_index_mutated",
    "operator_instance_mutated",
    "download_performed",
    "upload_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)


def audit_boundary(payload: Mapping[str, Any]) -> dict[str, Any]:
    violations = [field for field in UNSAFE_FIELDS if payload.get(field) is not False]
    return {
        "schema_version": "source_wave_boundary_audit.v0",
        "status": "pass" if not violations else "fail",
        "violations": violations,
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        print("usage: source_wave_boundary_auditor.py <boundary-json>", file=sys.stderr)
        return 2
    payload = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    result = audit_boundary(payload)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
