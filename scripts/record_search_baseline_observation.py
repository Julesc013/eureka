from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.engine.evals import (  # noqa: E402
    load_search_usefulness_queries,
    manual_observation_template,
    validate_search_usefulness_observation_payload,
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Create or validate a manual external-baseline observation template "
            "for Search Usefulness Audit v0. This script performs no web search "
            "and no scraping."
        ),
    )
    parser.add_argument("--query", dest="query_id", help="Query id for a new template.")
    parser.add_argument(
        "--system",
        default="google",
        help="Observed system label, for example google or internet_archive_metadata.",
    )
    parser.add_argument("--output", help="Optional path to write the template JSON.")
    parser.add_argument("--validate", help="Validate an existing observation JSON file.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    output = stdout or sys.stdout

    if args.validate:
        payload = json.loads(Path(args.validate).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            output.write("Observation file must contain one JSON object.\n")
            return 1
        errors = validate_search_usefulness_observation_payload(payload)
        result = {
            "status": "valid" if not errors else "invalid",
            "errors": list(errors),
            "source_path": args.validate,
        }
        if args.json:
            output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
        else:
            output.write(f"Observation validation: {result['status']}\n")
            for error in errors:
                output.write(f"- {error}\n")
        return 0 if not errors else 1

    if not args.query_id:
        output.write("--query is required when not using --validate.\n")
        return 1

    load_result = load_search_usefulness_queries()
    query_by_id = {query.query_id: query for query in load_result.queries}
    query = query_by_id.get(args.query_id)
    if query is None:
        output.write(f"Search-usefulness query '{args.query_id}' was not found.\n")
        return 1

    template = manual_observation_template(query=query, system=args.system)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(template, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    output.write(json.dumps(template, indent=2, sort_keys=True))
    output.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
