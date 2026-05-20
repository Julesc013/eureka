from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(rel: str) -> dict:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


class WorkbenchFoundationTest(unittest.TestCase):
    def test_workbench_is_internal_superset(self) -> None:
        doctrine = load_json("control/inventory/workbench_surface_doctrine.json")
        self.assertTrue(doctrine["workbench_is_internal_superset"])
        self.assertTrue(doctrine["public_web_is_restricted_projection"])
        self.assertTrue(doctrine["same_kernel_and_packet_semantics"])
        self.assertFalse(doctrine["production_readiness_claimed"])

    def test_view_model_packet_locations_are_reserved(self) -> None:
        locations = {
            item["path"]: item
            for item in load_json("control/inventory/workbench_packet_location_matrix.json")["locations"]
        }
        for path in [
            "contracts/search_interaction/",
            "contracts/workbench/",
            "contracts/view_models/",
            "contracts/projections/",
            "contracts/domain/",
            "contracts/scout/",
            "contracts/snapshots/",
            "contracts/relay/",
        ]:
            with self.subTest(path=path):
                self.assertIn(path, locations)
                self.assertFalse(locations[path]["runtime_owns_contracts"])
                self.assertFalse(locations[path]["surfaces_own_contracts"])

    def test_result_records_no_runtime_or_ui_implementation(self) -> None:
        result = load_json("control/inventory/workbench_foundation_result.json")
        self.assertEqual("pass", result["status"])
        self.assertFalse(result["runtime_behavior_changed"])
        self.assertFalse(result["html_ui_implemented"])
        self.assertFalse(result["search_interaction_implemented"])
        self.assertFalse(result["ia_hunt_bridge_implemented"])
        self.assertTrue(result["validator_added"])
        self.assertTrue(result["tests_added"])


if __name__ == "__main__":
    unittest.main()
