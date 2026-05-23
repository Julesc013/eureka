from __future__ import annotations

import copy
import json
from pathlib import Path
import socket
from unittest import mock
import unittest

from scripts.validate_local_source_cache_runtime_plan import (
    output_path_allowed,
    validate_local_source_cache_runtime_plan,
    validate_plan_record,
)


ROOT = Path(__file__).resolve().parents[2]
PLAN_EXAMPLE = ROOT / "examples/sources/cache/plans/minimal_local_source_cache_plan_v0.json"
FUTURE_PROBE_EXAMPLE = ROOT / "examples/sources/cache/plans/approved_metadata_probe_future_plan_v0.json"


class LocalSourceCacheRuntimePlanTests(unittest.TestCase):
    def test_valid_source_cache_plans_pass(self) -> None:
        report = validate_local_source_cache_runtime_plan(ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_current_plan_enabling_runtime_fails(self) -> None:
        plan = _plan()
        plan["runtime_status"] = "implemented"
        plan["product_boundary"]["implemented_source_cache_runtime"] = True

        errors = validate_plan_record(plan, "synthetic")

        self.assertTrue(_has_error(errors, "runtime_status"))
        self.assertTrue(_has_error(errors, "implemented_source_cache_runtime"))

    def test_current_plan_enabling_live_probes_fails(self) -> None:
        plan = _plan()
        plan["current_source_access_modes"].append("approved_metadata_probe_future")
        plan["product_boundary"]["enabled_live_probes"] = True

        errors = validate_plan_record(plan, "synthetic")

        self.assertTrue(_has_error(errors, "future source access modes cannot be current"))
        self.assertTrue(_has_error(errors, "enabled_live_probes"))

    def test_current_plan_enabling_source_sync_fails(self) -> None:
        plan = _plan()
        plan["product_boundary"]["enabled_source_sync"] = True

        errors = validate_plan_record(plan, "synthetic")

        self.assertTrue(_has_error(errors, "enabled_source_sync"))

    def test_approved_metadata_probe_future_without_gates_fails(self) -> None:
        plan = _future_probe_plan()
        del plan["future_approval_gates"]["kill_switch"]

        errors = validate_plan_record(plan, "synthetic")

        self.assertTrue(_has_error(errors, "future source access modes require approval gates"))

    def test_google_scraping_mode_fails(self) -> None:
        plan = _plan()
        plan["current_source_access_modes"].append("google_result_page_scraping")

        errors = validate_plan_record(plan, "synthetic")

        self.assertTrue(_has_error(errors, "forbidden source access modes"))

    def test_unapproved_arbitrary_url_fetch_fails(self) -> None:
        plan = _plan()
        plan["current_source_access_modes"].append("arbitrary_url_fetch")

        errors = validate_plan_record(plan, "synthetic")

        self.assertTrue(_has_error(errors, "forbidden source access modes"))

    def test_automatic_evidence_acceptance_fails(self) -> None:
        plan = _plan()
        plan["review_gates"]["automatic_evidence_acceptance_allowed"] = True

        errors = validate_plan_record(plan, "synthetic")

        self.assertTrue(_has_error(errors, "automatic_evidence_acceptance_allowed"))

    def test_automatic_public_index_use_fails(self) -> None:
        plan = _plan()
        plan["review_gates"]["automatic_public_index_use_allowed"] = True

        errors = validate_plan_record(plan, "synthetic")

        self.assertTrue(_has_error(errors, "automatic_public_index_use_allowed"))

    def test_automatic_master_index_mutation_fails(self) -> None:
        plan = _plan()
        plan["review_gates"]["automatic_master_index_mutation_allowed"] = True
        plan["truth_boundary"]["source_cache_record_can_mutate_master_index"] = True

        errors = validate_plan_record(plan, "synthetic")

        self.assertTrue(_has_error(errors, "automatic_master_index_mutation_allowed"))
        self.assertTrue(_has_error(errors, "source_cache_record_can_mutate_master_index"))

    def test_forbidden_output_root_fails(self) -> None:
        self.assertFalse(output_path_allowed(ROOT / "site/dist/source_cache.json", ROOT))
        self.assertFalse(output_path_allowed(ROOT / "runtime/source/cache.json", ROOT))
        self.assertFalse(output_path_allowed(ROOT / "contracts/source/cache.json", ROOT))

    def test_private_path_outside_documented_future_roots_fails(self) -> None:
        plan = _plan()
        plan["notes"] = ["C:\\Users\\Example\\private-source-cache"]

        from scripts.validate_local_source_cache_runtime_plan import _scan_payload_for_forbidden_content

        errors = _scan_payload_for_forbidden_content(plan, "synthetic")

        self.assertTrue(_has_error(errors, "private path"))

    def test_rights_malware_installability_exhaustive_claim_fails(self) -> None:
        plan = _plan()
        plan["notes"] = [
            "rights clearance confirmed",
            "malware safety confirmed",
            "verified installability",
            "exhaustive global search complete",
        ]

        from scripts.validate_local_source_cache_runtime_plan import _scan_payload_for_forbidden_content

        errors = _scan_payload_for_forbidden_content(plan, "synthetic")

        self.assertGreaterEqual(len(errors), 4)

    def test_credential_api_key_fixture_fails(self) -> None:
        plan = _plan()
        plan["notes"] = ["api_key=abcdef1234567890"]

        from scripts.validate_local_source_cache_runtime_plan import _scan_payload_for_forbidden_content

        errors = _scan_payload_for_forbidden_content(plan, "synthetic")

        self.assertTrue(_has_error(errors, "credential/API-key"))

    def test_validator_does_not_create_local_state(self) -> None:
        before = _private_root_state()

        report = validate_local_source_cache_runtime_plan(ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(before, _private_root_state())

    def test_validator_does_not_call_network_model_or_provider(self) -> None:
        with mock.patch.object(socket, "create_connection", side_effect=AssertionError("network call blocked")):
            report = validate_local_source_cache_runtime_plan(ROOT)

        self.assertEqual(report["status"], "valid")


def _plan() -> dict[str, object]:
    return json.loads(PLAN_EXAMPLE.read_text(encoding="utf-8"))


def _future_probe_plan() -> dict[str, object]:
    return json.loads(FUTURE_PROBE_EXAMPLE.read_text(encoding="utf-8"))


def _has_error(errors: list[str], needle: str) -> bool:
    return any(needle in error for error in errors)


def _private_root_state() -> dict[str, bool]:
    return {
        ".aide.local/eureka/source_cache": (ROOT / ".aide.local" / "eureka" / "source_cache").exists(),
        ".local/eureka/source_cache": (ROOT / ".local" / "eureka" / "source_cache").exists(),
        ".cache/eureka/source_cache": (ROOT / ".cache" / "eureka" / "source_cache").exists(),
    }


if __name__ == "__main__":
    unittest.main()
