#!/usr/bin/env python3
"""Validate PUBLIC-SEARCH-UX-MODEL-00."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.public_alpha import build_public_search_ux_model_bundle  # noqa: E402


CONTRACTS = [
    "contracts/view/models/public_search/search_page_view_model.v0.json",
    "contracts/view/models/public_search/result_card_view_model.v0.json",
    "contracts/view/models/public_search/object_page_view_model.v0.json",
    "contracts/view/models/public_search/candidate_page_view_model.v0.json",
    "contracts/view/models/public_search/need_page_view_model.v0.json",
    "contracts/view/models/public_search/source_page_view_model.v0.json",
    "contracts/view/models/public_search/evidence_page_view_model.v0.json",
    "contracts/view/models/public_search/no_results_need_view_model.v0.json",
    "contracts/view/models/public_search/search_coverage_view_model.v0.json",
    "contracts/view/models/public_search/action_posture_view_model.v0.json",
    "contracts/view/models/public_search/capability_profile_view_model.v0.json",
]
EXAMPLES = [
    "examples/view_models/public_search/search_page_view_model.json",
    "examples/view_models/public_search/result_card_reviewed.json",
    "examples/view_models/public_search/result_card_candidate.json",
    "examples/view_models/public_search/result_card_known_need.json",
    "examples/view_models/public_search/result_card_absence.json",
    "examples/view_models/public_search/result_card_source_lead.json",
]
DOCS = [
    "docs/architecture/PUBLIC_SEARCH_UX_MODEL.md",
    "docs/operations/PUBLIC_SEARCH_UX_MODEL_RUNBOOK.md",
    "docs/reference/PUBLIC_SEARCH_VIEW_MODELS.md",
    "docs/reference/PUBLIC_SEARCH_RESULT_CARD_VIEW_MODEL.md",
]
INVENTORY = [
    "control/inventory/public_search_ux_model_input_state.json",
    "control/inventory/public_search_ux_model_contract_authority_matrix.json",
    "control/inventory/public_search_ux_model_result_card_matrix.json",
    "control/inventory/public_search_ux_model_projection_matrix.json",
    "control/inventory/public_search_ux_model_boundary_report.json",
    "control/inventory/public_search_ux_model_validation_matrix.json",
    "control/inventory/public_search_ux_model_result.json",
    "control/inventory/public_search_ux_model_next_task_decision.json",
]
RESULT_CARD_FIELDS = {
    "title",
    "url",
    "status",
    "object_type",
    "domain",
    "source_family",
    "source_label",
    "snippet",
    "match_reasons",
    "evidence_summary",
    "confidence_label",
    "risk_label",
    "rights_label",
    "compatibility_label",
    "action_posture",
    "review_required",
    "accepted_truth",
    "limitations",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.parse_args(argv)
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate() -> dict[str, Any]:
    checks = {
        "contracts_exist": _paths_exist(CONTRACTS),
        "policy_exists": (REPO_ROOT / "control/policies/public_search_ux_model_policy.json").exists(),
        "examples_exist": _paths_exist(EXAMPLES),
        "docs_exist": _paths_exist(DOCS),
        "inventory_exists": _paths_exist(INVENTORY),
        "cli_help_works": _cli_help_works(),
        "no_duplicate_contract_authority": not (REPO_ROOT / "contracts/views").exists(),
    }
    checks.update(_runtime_checks())
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "schema_version": "public_search_ux_model_validation.v0",
        "task": "PUBLIC-SEARCH-UX-MODEL-00",
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": failures,
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
    }


def _runtime_checks() -> dict[str, bool]:
    bundle = build_public_search_ux_model_bundle()
    cards = list(bundle["search_page"]["result_cards"])
    statuses = {card["status"] for card in cards}
    projections = bundle["projections"]
    return {
        "bundle_builds": bundle["status"] == "pass",
        "required_statuses_present": {"verified", "candidate", "known_need", "absence", "source_lead"}.issubset(statuses),
        "result_card_required_fields_present": all(RESULT_CARD_FIELDS.issubset(card) for card in cards),
        "candidate_like_cards_not_accepted_truth": all(
            card["accepted_truth"] is False and card["review_required"] is True
            for card in cards
            if card["status"] != "verified"
        ),
        "action_postures_disable_unsafe_actions": all(
            card["action_posture"].get("downloads_enabled") is False
            and card["action_posture"].get("extraction_enabled") is False
            and card["action_posture"].get("model_provider_enabled") is False
            and card["action_posture"].get("public_mutation_enabled") is False
            for card in cards
        ),
        "verified_card_distinct": any(
            card["status"] == "verified" and card["accepted_truth"] is True and card["review_required"] is False
            for card in cards
        ),
        "projection_profiles_present": set(projections) == {"public_web", "operator_workbench", "api_json", "classic_html", "text"},
        "public_projections_read_only": all(
            projection["read_only"] is True
            and projection["public_mutation_enabled"] is False
            and projection["public_live_source_fanout_enabled"] is False
            for projection in projections.values()
        ),
        "agents_do_not_need_html_scrape": projections["api_json"]["html_scrape_required_for_agents"] is False,
        "no_results_need_present": bundle["pages"]["no_results_need"]["accepted_truth"] is False,
        "boundaries_false": all(
            bundle.get(key) is False
            for key in (
                "deployment_performed",
                "public_launch_performed",
                "production_readiness_claimed",
                "public_launch_readiness_claimed",
                "accepted_truth_created",
                "reviewed_index_mutated",
                "master_index_mutated",
                "public_index_mutated",
                "public_mutation_enabled",
                "public_live_source_fanout_enabled",
                "download_performed",
                "extraction_executed",
                "model_provider_used",
            )
        ),
    }


def _paths_exist(paths: Sequence[str]) -> bool:
    return all((REPO_ROOT / path).exists() for path in paths)


def _cli_help_works() -> bool:
    completed = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts/eureka_public_search_ux_model.py"), "--help"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return completed.returncode == 0


if __name__ == "__main__":
    raise SystemExit(main())
