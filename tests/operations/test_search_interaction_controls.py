from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class SearchInteractionControlsTest(unittest.TestCase):
    def test_public_and_native_restrictions(self) -> None:
        projections = {
            item["projection_profile"]: item
            for item in json.loads((REPO_ROOT / "control/inventory/search_interaction_projection_matrix.json").read_text(encoding="utf-8"))["profiles"]
        }
        self.assertFalse(projections["public_web"]["can_run_source_probe"])
        self.assertFalse(projections["public_web"]["can_review_promote"])
        self.assertFalse(projections["native_desktop_read_only"]["can_mutate"])

    def test_unsafe_commands_are_unavailable(self) -> None:
        matrix = json.loads((REPO_ROOT / "control/inventory/search_interaction_control_command_matrix.json").read_text(encoding="utf-8"))
        for command in ["download", "extract", "call_model_provider", "deploy_public_projection", "run_source_probe"]:
            self.assertIn(command, matrix["unavailable_commands"])


if __name__ == "__main__":
    unittest.main()
