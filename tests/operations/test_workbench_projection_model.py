from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(rel: str) -> dict:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


class WorkbenchProjectionModelTest(unittest.TestCase):
    def test_required_projection_profiles_present(self) -> None:
        matrix = load_json("control/inventory/workbench_projection_matrix.json")
        profiles = set(matrix["projection_profiles"])
        for profile in [
            "operator_workbench",
            "local_user_read_only",
            "public_web",
            "public_api",
            "cli",
            "tui",
            "relay_client",
            "snapshot_client",
            "native_desktop_read_only",
            "mobile_read_only",
            "future_marketplace_admin",
        ]:
            self.assertIn(profile, profiles)

    def test_public_and_native_restrictions(self) -> None:
        rows = {
            item["projection_profile"]: item
            for item in load_json("control/inventory/workbench_projection_matrix.json")["rows"]
        }
        self.assertFalse(rows["public_web"]["can_run_source_probe"])
        self.assertFalse(rows["public_web"]["can_rebuild_index"])
        self.assertFalse(rows["native_desktop_read_only"]["can_mutate_instance"])
        for profile in ["public_web", "native_desktop_read_only"]:
            self.assertFalse(rows[profile]["can_download"])
            self.assertFalse(rows[profile]["can_extract"])
            self.assertFalse(rows[profile]["can_call_model"])
            self.assertFalse(rows[profile]["can_deploy"])

    def test_operator_only_permissions_are_classified(self) -> None:
        permissions = {
            item["permission_id"]: item
            for item in load_json("control/inventory/workbench_permission_matrix.json")["permissions"]
        }
        self.assertTrue(permissions["review_candidate"]["operator_workbench"])
        self.assertFalse(permissions["review_candidate"]["public_web"])
        self.assertFalse(permissions["run_source_probe"]["public_web"])
        self.assertFalse(permissions["mutate_master_index"]["operator_workbench"])


if __name__ == "__main__":
    unittest.main()
