#!/usr/bin/env python3
"""Run a deterministic offline smoke over the local workbench play demo pack."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance.paths import resolve_instance_root
from validate_play_seed_pack import smoke_report


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True, help="Explicit local instance root, usually ../instances/default.")
    parser.add_argument("--operator-token", required=True, help="Operator token label for smoke reporting; not persisted.")
    parser.add_argument("--base-url", help="Optional local workbench URL. PLAY-00 smoke does not contact it.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    instance = str(resolve_instance_root(args.instance, REPO_ROOT))
    result = smoke_report(instance, args.operator_token, args.base_url)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result['status']}", file=stdout)
        print(f"known_hit_query: {result['checks']['known_hit_query']}", file=stdout)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
