#!/usr/bin/env python3
"""Smoke the no-JS public search UX MVP examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.public_search import build_public_search_ux_mvp_bundle  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-examples", action="store_true", help="Use committed public-safe examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args(argv)
    if not args.from_examples:
        parser.error("--from-examples is required")

    result = build_public_search_ux_mvp_bundle()
    checks = {
        "bundle_passed": result["status"] == "pass",
        "home_page_no_js_get_form": result["no_js_search_form_passed"],
        "candidate_verified_distinction": result["candidate_verified_distinction_passed"],
        "limited_reviewed_record_distinction": result["limited_reviewed_record_distinction_passed"],
        "no_results_need_page": result["no_results_need_page_added"],
        "public_projection_read_only": result["public_projection_read_only"],
        "boundaries_false": all(
            result.get(key) is False
            for key in (
                "deployment_performed",
                "public_launch_performed",
                "site_dist_written",
                "public_mutation_enabled",
                "public_live_source_fanout_enabled",
                "download_performed",
                "extraction_executed",
                "model_provider_used",
            )
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    payload = {
        "schema_version": "public_search_ux_mvp_smoke_result.v0",
        "task": "PUBLIC-SEARCH-UX-MVP-00",
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": failures,
    }
    print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
