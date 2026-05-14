from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SOLUTION = ROOT / "control/inventory/local_total_solution_result.json"
BLOCKERS = ROOT / "control/inventory/local_total_blocker_register.json"
WARNINGS = ROOT / "control/inventory/local_total_warning_disposition.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class LocalTotalSolutionTests(unittest.TestCase):
    def test_solution_records_no_forbidden_claims(self):
        payload = load_json(SOLUTION)
        self.assertEqual("local_total_solution_result.v0", payload["schema_version"])
        self.assertFalse(payload["deployment_performed"])
        self.assertFalse(payload["production_readiness_claimed"])
        self.assertFalse(payload["public_launch_readiness_claimed"])
        self.assertFalse(payload["force_push_performed"])
        self.assertFalse(payload["history_rewrite_performed"])

    def test_solution_requires_green_core_gates_before_pass(self):
        payload = load_json(SOLUTION)
        if payload["status"] in {"pass", "pass_with_warnings"}:
            self.assertTrue(payload["all_local_tasks_reviewed"])
            self.assertTrue(payload["all_local_capabilities_present"])
            self.assertEqual(0, payload["hard_blockers_remaining"])
            self.assertTrue(payload["runtime_leakage_gate_pass"])
            self.assertEqual(0, payload["new_unallowlisted_production_findings"])
            self.assertTrue(payload["full_unittest_discovery_pass"])
            self.assertTrue(payload["generated_artifact_cleanliness_pass"])
            self.assertTrue(payload["architecture_boundaries_pass"])
            self.assertTrue(payload["local_service_smoke_pass"])
            self.assertTrue(payload["local_workbench_smoke_pass"])
            self.assertTrue(payload["auto_test_auto_search_pass"])
            self.assertTrue(payload["lan_smoke_pass_or_bounded"])
            self.assertTrue(payload["clean_machine_bootstrap_pass"])

    def test_blockers_and_warning_disposition_are_explicit(self):
        blockers = load_json(BLOCKERS)
        warnings = load_json(WARNINGS)
        self.assertEqual(0, blockers["hard_blockers_remaining"])
        self.assertEqual([], blockers["blockers"])
        for warning in warnings.get("warnings", []):
            self.assertIn(warning["classification"], {"resolved", "harmless_for_next_track", "deferred_with_expiry", "child_task_required"})
            self.assertIn("blocks_main_promotion", warning)


if __name__ == "__main__":
    unittest.main()
