from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
HANDOFF = ROOT / "external_full_discovery_handoff.json"


class ExternalFullDiscoveryHandoffWave03Tests(unittest.TestCase):
    def test_handoff_uses_external_output_and_compact_return_artifacts(self) -> None:
        payload = json.loads(HANDOFF.read_text(encoding="utf-8"))

        self.assertEqual("external_full_discovery_handoff.v0", payload["schema_version"])
        self.assertEqual("WAITING_FOR_EXTERNAL_FULL_DISCOVERY", payload["status"])
        self.assertTrue(payload["run_outside_ai"])
        self.assertFalse(payload["full_discovery_run_inside_ai"])
        self.assertIn("python scripts/run_full_unittest_discovery.py", payload["command"])
        self.assertIn("../eureka-test-runs/live-product-hardening-wave-03", payload["suggested_output_dir"])
        self.assertIn("../eureka-test-runs/live-product-hardening-wave-03/full_unittest_summary.json", payload["paste_back"])
        self.assertTrue(any("stdout" in item for item in payload["do_not_paste"]))
        self.assertTrue(any("stderr" in item for item in payload["do_not_paste"]))
        self.assertFalse(payload["raw_logs_committed"])
        self.assertFalse(payload["public_exposure"])
        self.assertFalse(payload["reviewed_master_mutation"])


if __name__ == "__main__":
    unittest.main()
