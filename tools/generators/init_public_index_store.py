#!/usr/bin/env python3
"""Initialize a local reviewed public index SQLite store."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.public_index import PublicIndexStore
from runtime.public_index.validation import validate_public_index_path


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    errors = validate_public_index_path(args.db)
    if errors:
        print(json.dumps({"status": "fail", "errors": list(errors)}, indent=2, sort_keys=True), file=stderr)
        return 2
    with PublicIndexStore.open(args.db) as store:
        migrations = store.init()
        integrity = store.check_integrity() if args.check else {}
    result = {
        "schema_version": "public_index_init_result.v0",
        "status": "pass" if not integrity or integrity.get("status") == "pass" else "fail",
        "db": args.db,
        "migrations": migrations,
        "integrity": integrity,
        "master_index_mutated": False,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"initialized reviewed public index store: {args.db}", file=stdout)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
