from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class LocalApplianceFutureTrackGateTests(unittest.TestCase):
    def test_future_gate_rejects_scaffold_only_completion(self) -> None:
        payload = json.loads((ROOT / "control/inventory/local_appliance_future_track_gate.json").read_text())
        self.assertFalse(payload["scaffold_only_completion_allowed"])
        self.assertFalse(payload["direct_master_index_mutation_allowed"])
        self.assertFalse(payload["hidden_state_allowed"])
        self.assertIn("avoid scaffold-only completion", payload["requirements"])

    def test_future_gate_names_required_tracks(self) -> None:
        payload = json.loads((ROOT / "control/inventory/local_appliance_future_track_gate.json").read_text())
        for track in ("HUNT", "SYN", "F", "G", "H", "I", "J", "K", "D", "C", "E", "L"):
            self.assertIn(track, payload["future_tracks"])


if __name__ == "__main__":
    unittest.main()
