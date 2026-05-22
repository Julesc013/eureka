#!/usr/bin/env python3
"""Build deterministic G0 explanation packets from a fixture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_eval.g0_quality import build_explanation_packet, build_score_breakdown, load_quality_fixture  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", default="examples/search_quality/sample_quality_fixture.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    fixture = load_quality_fixture(args.fixture)
    packets = []
    for record in fixture.get("records", []):
        score = build_score_breakdown(record, fixture.get("query_context", {}), fixture.get("domain_context", {}))
        packets.append(build_explanation_packet(score, record))
    payload = {
        "schema_version": "g0_explanation_output.v0",
        "explanation_packets": packets,
        "explanation_count": len(packets),
        "fake_evidence_created": False,
        "model_provider_used": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"G0 explanation_count={len(packets)}", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
