from __future__ import annotations

import json
import subprocess
import sys
import unittest


class RealLiveSearchHuntAcceptanceTests(unittest.TestCase):
    def test_deterministic_acceptance_harness_passes_without_live_key(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/check_live_search_hunt_acceptance.py", "--json"],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertIn(payload["status"], {"pass", "pass_with_warnings"})
        deterministic = payload["deterministic"]
        self.assertEqual("pass", deterministic["status"])
        self.assertGreaterEqual(deterministic["transient_leads"], 1)
        self.assertGreaterEqual(deterministic["fetches"], 1)
        self.assertGreaterEqual(deterministic["observations"], 1)
        self.assertGreaterEqual(deterministic["documents"], 1)
        self.assertGreaterEqual(deterministic["restart_result_count"], 1)
        self.assertFalse(payload["provider_result_payload_persisted"])
        self.assertFalse(payload["reviewed_master_mutation"])
        self.assertFalse(payload["public_index_mutation"])


if __name__ == "__main__":
    unittest.main()
