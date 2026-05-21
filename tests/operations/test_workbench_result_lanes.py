from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class WorkbenchResultLaneInventoryTest(unittest.TestCase):
    def test_matrices_include_required_lanes(self) -> None:
        schema = json.loads((REPO_ROOT / "control/inventory/workbench_result_lane_schema_matrix.json").read_text(encoding="utf-8"))
        lanes = {item["lane_kind"]: item for item in schema["lanes"]}
        self.assertIn("ia_metadata_candidates", lanes)
        self.assertEqual("ia_metadata_candidate_not_truth", lanes["ia_metadata_candidates"]["truth_level"])
        self.assertTrue(lanes["ia_metadata_candidates"]["review_required_default"])

    def test_public_and_native_projection_restrictions_are_recorded(self) -> None:
        projection = json.loads((REPO_ROOT / "control/inventory/workbench_result_lane_projection_matrix.json").read_text(encoding="utf-8"))
        public = [row for row in projection["projections"] if row["projection_profile"] == "public_web"]
        native = [row for row in projection["projections"] if row["projection_profile"] == "native_desktop_read_only"]
        self.assertTrue(public)
        self.assertTrue(native)
        self.assertTrue(all(row["can_run_source_probe"] is False for row in public))
        self.assertTrue(all(row["can_mutate_store"] is False for row in native))

    def test_examples_are_deterministic_and_non_claiming(self) -> None:
        report = json.loads((REPO_ROOT / "examples/workbench/result_lanes/expected_boundary_report.json").read_text(encoding="utf-8"))
        self.assertFalse(report["source_probe_executed"])
        self.assertFalse(report["live_ia_call_performed"])
        self.assertFalse(report["deployment_performed"])
        self.assertTrue(report["unsafe_actions_blocked"])


if __name__ == "__main__":
    unittest.main()
