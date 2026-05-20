from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class WorkbenchRouteMatrixTest(unittest.TestCase):
    def test_required_routes_present(self) -> None:
        matrix = json.loads(
            (REPO_ROOT / "control/inventory/workbench_route_matrix.json").read_text(encoding="utf-8")
        )
        routes = {item["route_id"]: item for item in matrix["routes"]}
        for route_id in [
            "search", "hunt", "hunt_detail", "need", "need_detail", "workunit", "workunit_detail",
            "source", "source_detail", "source_cache", "evidence", "evidence_detail", "candidate",
            "candidate_detail", "review", "promotion", "index", "ia", "syn", "domain", "scout",
            "extraction", "snapshots", "relay", "ops", "audit",
        ]:
            with self.subTest(route_id=route_id):
                self.assertIn(route_id, routes)

    def test_public_write_actions_are_blocked(self) -> None:
        matrix = json.loads(
            (REPO_ROOT / "control/inventory/workbench_route_matrix.json").read_text(encoding="utf-8")
        )
        for route in matrix["routes"]:
            self.assertFalse(route["write_actions_allowed_public"])
            self.assertIn("deployment", route["blocked_actions"])
            self.assertIn("extraction", route["blocked_actions"])


if __name__ == "__main__":
    unittest.main()
