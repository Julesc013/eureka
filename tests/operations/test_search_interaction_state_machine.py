from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class SearchInteractionStateMachineTest(unittest.TestCase):
    def test_required_states_and_terminal_states(self) -> None:
        machine = json.loads((REPO_ROOT / "control/inventory/search_interaction_state_machine.json").read_text(encoding="utf-8"))
        for state in ["accepted", "compiled", "hunt_running", "review_items_available", "completed", "cancelled", "failed"]:
            self.assertIn(state, machine["states"])
        self.assertEqual({"completed", "cancelled", "failed"}, set(machine["terminal_states"]))

    def test_illegal_transitions_are_recorded(self) -> None:
        machine = json.loads((REPO_ROOT / "control/inventory/search_interaction_state_machine.json").read_text(encoding="utf-8"))
        self.assertIn(["completed", "hunt_running"], machine["illegal_transitions"])
        self.assertIn(["cancelled", "hunt_running"], machine["illegal_transitions"])
        self.assertIn(["failed", "completed"], machine["illegal_transitions"])


if __name__ == "__main__":
    unittest.main()
