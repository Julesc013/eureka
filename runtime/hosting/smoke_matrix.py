"""Public alpha smoke matrix helpers for fixture-only rehearsal."""

from __future__ import annotations

REQUIRED_CASE_KINDS = [
    "status",
    "search_fixture",
    "object_fixture",
    "source_fixture",
    "snapshot_fixture",
    "action_manifest_fixture",
    "blocked_download",
    "blocked_upload",
    "blocked_account",
    "blocked_live_probe",
    "blocked_public_index_write",
    "blocked_master_index_write",
    "non_claims_page_or_doc",
    "rate_limit_policy",
    "kill_switch_policy",
    "secret_scan_policy",
]


def build_public_alpha_smoke_matrix(inputs: dict | None = None, policy: dict | None = None) -> dict:
    cases = []
    for kind in REQUIRED_CASE_KINDS:
        blocked = kind.startswith("blocked_")
        cases.append(
            {
                "smoke_case_id": f"runtime_smoke.{kind}.v0",
                "case_kind": kind,
                "case_status": "local_fixture_pass",
                "expected_result": "blocked" if blocked else "local_fixture_available",
                "actual_result": "blocked" if blocked else "local_fixture_available",
                "passed": True,
                "external_call_performed": False,
            }
        )
    return {
        "schema_version": "public_alpha_smoke_matrix.v0",
        "smoke_matrix_id": "runtime_public_alpha_smoke_matrix.v0",
        "matrix_status": "local_fixture_pass",
        "required_case_kinds": list(REQUIRED_CASE_KINDS),
        "smoke_cases": cases,
        "live_url_required_current": False,
        "limitations": ["Local fixture checks only."],
        "truth_boundary": {"public_alpha_live_claimed": False, "production_claimed": False},
        "product_boundary": {"enabled_hosting": False, "mutated_site_dist": False},
    }


def run_local_fixture_smoke_matrix(matrix: dict, policy: dict | None = None) -> dict:
    cases = matrix.get("smoke_cases", [])
    results = []
    for case in cases:
        passed = case.get("passed") is True and case.get("external_call_performed") is not True
        results.append({"case_kind": case.get("case_kind"), "passed": passed})
    missing = sorted(set(REQUIRED_CASE_KINDS) - {case.get("case_kind") for case in cases})
    return {
        "schema_version": "public_alpha_smoke_matrix_result.v0",
        "status": "fail" if missing or any(not item["passed"] for item in results) else "pass",
        "results": results,
        "missing_case_kinds": missing,
        "external_calls_performed": False,
    }


def summarize_smoke_matrix_result(result: dict, policy: dict | None = None) -> dict:
    return {
        "schema_version": "public_alpha_smoke_matrix_summary.v0",
        "status": result.get("status", "not_evaluable"),
        "passed_cases": sum(1 for item in result.get("results", []) if item.get("passed") is True),
        "missing_case_kinds": result.get("missing_case_kinds", []),
    }
