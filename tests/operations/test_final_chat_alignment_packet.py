from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "control/inventory/final_chat_alignment_packet.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class FinalChatAlignmentPacketTests(unittest.TestCase):
    def test_packet_has_implemented_and_not_implemented_sections(self) -> None:
        payload = load_json(PACKET)
        self.assertEqual("final_chat_alignment_packet.v0", payload["schema_version"])
        self.assertIn("implemented", payload)
        self.assertIn("not_implemented", payload)
        self.assertGreater(len(payload["implemented"]["LOCAL capabilities"]), 5)
        self.assertIn("Search Hunt Session runtime", payload["not_implemented"])

    def test_packet_records_promotion_and_warnings(self) -> None:
        payload = load_json(PACKET)
        self.assertIn("promotion_status", payload)
        self.assertIn("warnings", payload)
        self.assertEqual(0, payload["hard_blockers_remaining"])
        self.assertIn("production readiness", payload["must_not_claim"])


if __name__ == "__main__":
    unittest.main()
