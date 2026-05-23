#!/usr/bin/env python3
"""Initialize an explicit SQLite review queue store."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.review.queue import ReviewQueueStore
from runtime.review.queue.validation import validate_review_queue_path


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    db_path = Path(args.db)
    errors = list(validate_review_queue_path(db_path))
    if errors:
        result = {"schema_version": "review_queue_init_result.v0", "status": "fail", "errors": errors}
        print(json.dumps(result, indent=2, sort_keys=True) if args.json else "\n".join(errors), file=stderr if not args.json else stdout)
        return 2

    with ReviewQueueStore.open(db_path) as store:
        applied = store.init()
        integrity = store.check_integrity() if args.check else {}
        result = {
            "schema_version": "review_queue_init_result.v0",
            "status": "pass" if not integrity or integrity.get("status") == "pass" else "fail",
            "db": str(db_path),
            "applied_migrations": applied,
            "integrity": integrity,
            "public_index_writes_enabled": False,
            "master_index_writes_enabled": False,
        }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"review queue store init: {result['status']}", file=stdout)
        print(f"db: {result['db']}", file=stdout)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
