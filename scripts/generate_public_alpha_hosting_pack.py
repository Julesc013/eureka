from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY_PATH = REPO_ROOT / "control" / "inventory" / "public_alpha_routes.json"
DEFAULT_OUTPUT_PATH = (
    REPO_ROOT
    / "docs"
    / "operations"
    / "public_alpha_hosting_pack"
    / "ROUTE_SAFETY_SUMMARY.md"
)
CREATED_BY_SLICE = "public_alpha_hosting_pack_v0"
CLASSIFICATION_ORDER = (
    "safe_public_alpha",
    "blocked_public_alpha",
    "local_dev_only",
    "review_required",
    "deferred",
)
CLASSIFICATION_LABELS = {
    "safe_public_alpha": "Safe Public Alpha",
    "blocked_public_alpha": "Blocked Public Alpha",
    "local_dev_only": "Local Dev Only",
    "review_required": "Review Required",
    "deferred": "Deferred",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the Public Alpha Hosting Pack route safety summary.",
    )
    parser.add_argument(
        "--inventory",
        default=str(DEFAULT_INVENTORY_PATH),
        help="Path to the public-alpha route inventory JSON.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output Markdown path. Defaults to stdout unless --check is used.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit nonzero if the checked output path is stale.",
    )
    args = parser.parse_args(argv)

    inventory_path = Path(args.inventory)
    output_path = Path(args.output) if args.output else DEFAULT_OUTPUT_PATH
    summary = format_route_safety_summary(load_inventory(inventory_path))

    if args.check:
        if not output_path.exists():
            sys.stderr.write(f"Missing route safety summary: {output_path}\n")
            return 1
        current = output_path.read_text(encoding="utf-8")
        if current != summary:
            sys.stderr.write(f"Route safety summary is stale: {output_path}\n")
            return 1
        return 0

    if args.output:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(summary, encoding="utf-8")
    else:
        sys.stdout.write(summary)
    return 0


def load_inventory(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def format_route_safety_summary(inventory: Mapping[str, object]) -> str:
    routes = _routes(inventory)
    counts = Counter(str(route["classification"]) for route in routes)
    total_routes = len(routes)
    version = str(inventory.get("version", "unknown"))

    lines = [
        "# Route Safety Summary",
        "",
        "This summary is generated from `control/inventory/public_alpha_routes.json`.",
        "The JSON inventory is the machine-readable source of truth for route",
        "classification. This document is an operator-readable summary for the",
        "Public Alpha Hosting Pack v0.",
        "",
        "## Current Inventory Status",
        "",
        f"- inventory kind: `{inventory.get('inventory_kind', 'unknown')}`",
        f"- inventory version: `{version}`",
        f"- total routes: {total_routes}",
    ]
    for classification in CLASSIFICATION_ORDER:
        lines.append(
            f"- {classification}: {counts.get(classification, 0)}"
        )
    lines.extend(
        [
            "",
            "These counts describe the constrained public-alpha demo posture only.",
            "They do not approve open-internet exposure or production deployment.",
            "",
            "## Category Examples",
            "",
        ]
    )

    for classification in CLASSIFICATION_ORDER:
        examples = [
            str(route["route_pattern"])
            for route in routes
            if str(route["classification"]) == classification
        ][:8]
        lines.append(f"### {CLASSIFICATION_LABELS[classification]}")
        lines.append("")
        if examples:
            lines.extend(f"- `{example}`" for example in examples)
        else:
            lines.append("- none currently inventoried")
        lines.append("")

    lines.extend(
        [
            "## Operator Notes",
            "",
            "- `safe_public_alpha` routes are safe only for the supervised demo",
            "  rehearsal posture when `public_alpha` mode is confirmed.",
            "- `blocked_public_alpha` routes are route variants that policy blocks in",
            "  `public_alpha` mode, usually because they expose caller-provided local",
            "  filesystem parameters.",
            "- `local_dev_only` routes remain available only to a trusted local operator",
            "  in `local_dev` mode.",
            "- `review_required` routes, currently manifest export routes, return",
            "  bounded JSON but still need explicit manual review before any real",
            "  hosted demo exposure.",
            "- `deferred` is currently empty; future entries must stay explicit rather",
            "  than silently disappearing from the inventory.",
            "",
            f"created_by_slice: `{CREATED_BY_SLICE}`",
            "",
        ]
    )
    return "\n".join(lines)


def _routes(inventory: Mapping[str, object]) -> list[Mapping[str, object]]:
    routes = inventory.get("routes")
    if not isinstance(routes, list):
        raise ValueError("Route inventory must contain a routes list.")
    result: list[Mapping[str, object]] = []
    for route in routes:
        if not isinstance(route, Mapping):
            raise ValueError(f"Route inventory entry must be an object: {route!r}")
        result.append(route)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
