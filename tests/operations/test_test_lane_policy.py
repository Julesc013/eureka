from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class TestLanePolicyTests(unittest.TestCase):
    def test_required_lanes_and_promotion_policy(self) -> None:
        policy = json.loads((REPO_ROOT / "control/policies/test_lane_policy.json").read_text(encoding="utf-8"))
        matrix = json.loads((REPO_ROOT / "control/inventory/test_lane_matrix.json").read_text(encoding="utf-8"))
        lanes = {row["lane_id"]: row for row in matrix["lanes"]}
        self.assertFalse(policy["full_discovery_per_commit_required"])
        self.assertTrue(policy["full_discovery_for_promotion_required"])
        self.assertTrue(policy["skip_reasons_required"])
        self.assertFalse(policy["test_requirements_weakened"])
        self.assertIn("L3_full_discovery", lanes)
        self.assertFalse(lanes["L3_full_discovery"]["required_for_commit"])
        self.assertTrue(lanes["L3_full_discovery"]["required_for_promotion"])


if __name__ == "__main__":
    unittest.main()

