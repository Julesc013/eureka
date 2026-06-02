#!/usr/bin/env python3
"""Validate PUBLIC-SEARCH-UX-MVP-00."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.public_search import build_public_search_ux_mvp_bundle  # noqa: E402


CONTRACTS = [
    "contracts/view/models/public_search/search_home_page_view_model.v0.json",
    "contracts/view/models/public_search/search_page_view_model.v0.json",
    "contracts/view/models/public_search/result_card_view_model.v0.json",
    "contracts/view/models/public_search/object_page_view_model.v0.json",
    "contracts/view/models/public_search/candidate_page_view_model.v0.json",
    "contracts/view/models/public_search/need_page_view_model.v0.json",
    "contracts/view/models/public_search/source_page_view_model.v0.json",
    "contracts/view/models/public_search/evidence_page_view_model.v0.json",
    "contracts/view/models/public_search/no_results_need_view_model.v0.json",
    "contracts/view/models/public_search/status_page_view_model.v0.json",
]
POLICIES = [
    "control/policies/public_search_ux_mvp_policy.json",
    "control/policies/public_search_result_card_policy.json",
    "control/policies/public_search_no_js_policy.json",
    "control/policies/public_search_accessibility_policy.json",
    "control/policies/public_search_non_claim_policy.json",
    "control/policies/public_search_projection_policy.json",
]
EXAMPLES = [
    "examples/public_search_ux/home_page.html",
    "examples/public_search_ux/search_results_page.html",
    "examples/public_search_ux/result_cards.html",
    "examples/public_search_ux/object_page.html",
    "examples/public_search_ux/candidate_page.html",
    "examples/public_search_ux/need_page.html",
    "examples/public_search_ux/source_page.html",
    "examples/public_search_ux/evidence_page.html",
    "examples/public_search_ux/status_page.html",
    "examples/public_search_ux/no_results_need_page.html",
    "examples/public_search_ux/text_projection.txt",
    "examples/public_search_ux/boundary_report.json",
]
MATRICES = [
    "control/inventory/public_search_ux_mvp_input_state.json",
    "control/inventory/public_search_ux_mvp_route_matrix.json",
    "control/inventory/public_search_ux_mvp_page_matrix.json",
    "control/inventory/public_search_ux_mvp_result_card_matrix.json",
    "control/inventory/public_search_ux_mvp_status_badge_matrix.json",
    "control/inventory/public_search_ux_mvp_no_results_matrix.json",
    "control/inventory/public_search_ux_mvp_accessibility_matrix.json",
    "control/inventory/public_search_ux_mvp_projection_matrix.json",
    "control/inventory/public_search_ux_mvp_boundary_report.json",
    "control/inventory/public_search_ux_mvp_smoke_result.json",
    "control/inventory/public_search_ux_mvp_validation_matrix.json",
    "control/inventory/public_search_ux_mvp_result.json",
    "control/inventory/public_search_ux_mvp_next_task_decision.json",
    "control/inventory/public_search_ux_mvp_failure_repair_log.json",
]
DOCS = [
    "docs/architecture/PUBLIC_SEARCH_UX_MVP.md",
    "docs/architecture/PUBLIC_SEARCH_RESULT_CARD.md",
    "docs/operations/PUBLIC_SEARCH_UX_MVP_RUNBOOK.md",
    "docs/operations/POST_PUBLIC_SEARCH_UX_MVP_PLAN.md",
    "docs/reference/PUBLIC_SEARCH_PAGE.md",
    "docs/reference/PUBLIC_SEARCH_RESULT_CARD.md",
    "docs/reference/PUBLIC_SEARCH_STATUS_BADGES.md",
    "docs/reference/PUBLIC_SEARCH_NO_RESULTS.md",
]
CLIS = [
    "scripts/eureka_public_search_render.py",
    "scripts/eureka_public_search_ux_smoke.py",
    "scripts/eureka_public_search_route_smoke.py",
]


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.parse_args(argv)
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate() -> dict[str, Any]:
    bundle = build_public_search_ux_mvp_bundle()
    html = "\n".join(bundle["html_examples"].values())
    cards = list(bundle["result_cards"])
    statuses = {card["status"] for card in cards}
    checks = {
        "contracts_exist": _paths_exist(CONTRACTS),
        "policies_exist": _paths_exist(POLICIES),
        "matrices_exist": _paths_exist(MATRICES),
        "examples_exist": _paths_exist(EXAMPLES),
        "docs_exist": _paths_exist(DOCS),
        "cli_help_works": _cli_help_works(),
        "bundle_passes": bundle["status"] == "pass",
        "home_page_builds": bundle["home_page_added"] is True,
        "results_page_builds": bundle["search_results_page_added"] is True,
        "detail_pages_build": all(
            bundle[key] is True
            for key in (
                "object_page_added",
                "candidate_page_added",
                "need_page_added",
                "source_page_added",
                "evidence_page_added",
                "status_page_added",
            )
        ),
        "no_results_need_page_builds": bundle["no_results_need_page_added"] is True,
        "required_statuses_present": {
            "verified",
            "reviewed_metadata_record",
            "reviewed_source_lead",
            "candidate",
            "near_miss",
            "known_need",
            "absence",
        }.issubset(statuses),
        "result_cards_have_public_fields": all(
            {
                "title",
                "href",
                "url",
                "status",
                "status_label",
                "domain_id",
                "domain",
                "source_family",
                "snippet",
                "action_posture",
                "review_required",
                "accepted_truth",
            }.issubset(card)
            for card in cards
        ),
        "no_js_get_form": bundle["no_js_search_form_passed"] is True and "<script" not in html.lower(),
        "candidate_verified_distinct": bundle["candidate_verified_distinction_passed"] is True,
        "limited_reviewed_distinct": bundle["limited_reviewed_record_distinction_passed"] is True,
        "status_badges_visible": "Candidate" in html and "Verified" in html and "limited claim" in html,
        "no_results_has_need_or_next_actions": bool(bundle["no_results"].get("next_actions")),
        "accessibility_smoke_passes": all(bundle["accessibility"].values()),
        "public_projection_read_only": bundle["public_projection_read_only"] is True,
        "boundaries_false": _boundaries_false(bundle),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "schema_version": "public_search_ux_mvp_validation.v0",
        "task": "PUBLIC-SEARCH-UX-MVP-00",
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": failures,
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "site_dist_written": False,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
    }


def _paths_exist(paths: Sequence[str]) -> bool:
    return all((REPO_ROOT / path).exists() for path in paths)


def _cli_help_works() -> bool:
    for path in CLIS:
        completed = subprocess.run(
            [sys.executable, str(REPO_ROOT / path), "--help"],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            return False
    return True


def _boundaries_false(bundle: dict[str, Any]) -> bool:
    return all(
        bundle.get(key) is False
        for key in (
            "site_dist_written",
            "deployment_performed",
            "public_launch_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
            "public_mutation_enabled",
            "public_live_source_fanout_enabled",
            "download_performed",
            "file_fetch_performed",
            "ocr_performed",
            "extraction_executed",
            "model_provider_used",
            "accepted_truth_created",
            "reviewed_index_mutated",
            "master_index_mutated",
            "public_index_mutated",
            "verified_download_claim_created",
            "malware_clean_claim_created",
            "rights_clearance_claim_created",
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
