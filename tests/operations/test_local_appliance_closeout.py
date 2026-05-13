from __future__ import annotations

import json
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_local_appliance_closeout import build_blocker_register, build_closeout_records
from validate_local_appliance_closeout import validate


class LocalApplianceCloseoutTests(unittest.TestCase):
    def test_closeout_records_complete_local_track_with_warning(self) -> None:
        records = build_closeout_records(ROOT)
        closeout = records["closeout_result"]
        self.assertEqual("pass_with_warnings", closeout["status"])
        self.assertTrue(closeout["local_track_complete"])
        self.assertTrue(closeout["all_required_capabilities_implemented"])
        self.assertTrue(closeout["all_required_capabilities_tested"])
        self.assertEqual(0, closeout["hard_blockers_remaining"])
        self.assertGreater(closeout["warnings_remaining"], 0)

    def test_closeout_blocks_if_required_result_missing(self) -> None:
        blockers = build_blocker_register(ROOT, ["control/inventory/missing.json"], [], {}, False)
        self.assertEqual(1, blockers["hard_blockers_remaining"])
        self.assertIn("LOCAL-REMEDIATION", blockers["blockers"][0]["next_task"])

    def test_required_runtime_surfaces_are_present_in_matrix(self) -> None:
        matrix = json.loads((ROOT / "control/inventory/local_appliance_capability_matrix.json").read_text())
        capability_ids = {row["capability_id"] for row in matrix["capabilities"]}
        self.assertIn("read_only_localhost_service", capability_ids)
        self.assertIn("html_workbench", capability_ids)
        self.assertIn("workunit_queue", capability_ids)
        self.assertIn("auto_test_auto_search_harness", capability_ids)
        self.assertIn("clean_machine_bootstrap", capability_ids)

    def test_validator_passes_with_disposed_warnings(self) -> None:
        result = validate(ROOT, run_local_validators=False, include_full_discovery=False)
        self.assertIn(result["status"], {"pass", "pass_with_warnings"})
        self.assertTrue(result["local_track_complete"])


if __name__ == "__main__":
    unittest.main()
