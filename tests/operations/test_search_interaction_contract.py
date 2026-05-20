from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class SearchInteractionContractTest(unittest.TestCase):
    def test_all_packet_contracts_exist_with_required_fields(self) -> None:
        packets = json.loads((REPO_ROOT / "control/inventory/search_interaction_packet_inventory.json").read_text(encoding="utf-8"))["packets"]
        for packet in packets:
            path = REPO_ROOT / packet["contract_path"]
            with self.subTest(packet=packet["packet_id"]):
                self.assertTrue(path.is_file())
                schema = json.loads(path.read_text(encoding="utf-8"))
                self.assertIn("schema_version", schema["required"])
                self.assertIn("packet_type", schema["required"])
                self.assertFalse(packet["owns_truth"])

    def test_feedback_creates_plan_patch_not_truth(self) -> None:
        feedback = json.loads((REPO_ROOT / "control/inventory/search_interaction_feedback_event_matrix.json").read_text(encoding="utf-8"))
        for item in feedback["feedback_events"]:
            self.assertTrue(item["creates_plan_patch"])
        policy = json.loads((REPO_ROOT / "control/policies/search_interaction_feedback_policy.json").read_text(encoding="utf-8"))
        self.assertFalse(policy["feedback_is_truth"])
        self.assertFalse(policy["feedback_mutates_master_index"])

    def test_result_lane_truth_levels_are_explicit(self) -> None:
        lanes = json.loads((REPO_ROOT / "control/inventory/search_interaction_result_lane_contract_matrix.json").read_text(encoding="utf-8"))
        for lane in lanes["lanes"]:
            self.assertTrue(lane["truth_level"])
            if lane["lane_kind"] != "reviewed_local_results":
                self.assertNotEqual("reviewed", lane["truth_level"])


if __name__ == "__main__":
    unittest.main()
