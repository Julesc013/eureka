from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_external_baseline_observations import (  # noqa: E402
    DEFAULT_OBSERVATIONS_DIR,
    PENDING_STATUS,
    validate_external_baseline_observations,
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Report manual external baseline observation coverage. This script "
            "does not query external systems."
        )
    )
    parser.add_argument(
        "--observations-dir",
        default=str(DEFAULT_OBSERVATIONS_DIR),
        help="Directory of observation JSON files.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    validation = validate_external_baseline_observations(
        observations_dir=Path(args.observations_dir)
    )
    report = {
        "status": "ready" if validation["status"] == "valid" else "invalid",
        "created_by": "manual_external_baseline_status_report_v0",
        "validation_status": validation["status"],
        "query_count": validation["query_count"],
        "systems": validation["systems"],
        "status_counts_by_system": validation["status_counts_by_system"],
        "query_coverage": validation["query_coverage"],
        "observed_query_ids": {
            system_id: coverage["observed_query_count"]
            for system_id, coverage in validation["query_coverage"].items()
        },
        "missing_observation_slots": {
            system_id: max(
                0,
                coverage["expected_query_count"]
                - coverage["observed_query_count"],
            )
            for system_id, coverage in validation["query_coverage"].items()
        },
        "limitations": [
            "Pending slots are not observed baselines.",
            "This report performs no external querying or scraping.",
            "Future observed records are manual, time-sensitive, and not global truth.",
        ],
        "errors": validation["errors"],
    }
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain_report(report))
    return 0 if report["status"] == "ready" else 1


def _format_plain_report(report: dict[str, object]) -> str:
    lines = [
        "External baseline observation status",
        f"status: {report['status']}",
        f"query_count: {report['query_count']}",
        "",
        "Systems",
    ]
    counts_by_system = report["status_counts_by_system"]
    coverage_by_system = report["query_coverage"]
    assert isinstance(counts_by_system, dict)
    assert isinstance(coverage_by_system, dict)
    for system_id in report["systems"]:  # type: ignore[assignment]
        counts = counts_by_system[system_id]
        coverage = coverage_by_system[system_id]
        lines.append(
            "- "
            f"{system_id}: pending={counts.get(PENDING_STATUS, 0)}, "
            f"observed={counts.get('observed', 0)}, "
            f"expected_queries={coverage['expected_query_count']}"
        )
    if report["errors"]:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])  # type: ignore[union-attr]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
