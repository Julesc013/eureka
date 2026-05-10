#!/usr/bin/env python3
"""Check public launch evidence packet remains operator-gated."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.hosting.launch_evidence import validate_public_launch_evidence_packet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="examples/hosting/launch/public_launch_evidence_packet_required_v0.json")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    packet = json.loads((REPO_ROOT / args.input).read_text(encoding="utf-8"))
    result = validate_public_launch_evidence_packet(packet, {})
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Public launch evidence status: {result['status']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
