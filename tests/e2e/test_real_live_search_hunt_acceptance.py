from __future__ import annotations

import json
import subprocess
import sys
import unittest


class RealLiveSearchHuntAcceptanceTests(unittest.TestCase):
    def test_deterministic_acceptance_harness_passes_without_live_key(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/check_live_search_hunt_acceptance.py",
                "--live-canary",
                "--query",
                "unit test unseen query",
                "--max-queries",
                "3",
                "--max-fetches",
                "3",
                "--json",
            ],
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
        self.assertIn(payload["live_canary"]["status"], {"waiting", "pass", "fail"})
        if payload["live_canary"]["status"] == "pass":
            self.assertEqual("pass", payload["checks"][-1]["status"])
            self.assertGreaterEqual(payload["live_canary"]["fetch_attempt_count"], 1)
            self.assertGreaterEqual(payload["live_canary"]["pages_fetched"], 1)
            self.assertGreaterEqual(payload["live_canary"]["observations_created"], 1)
            self.assertGreaterEqual(payload["live_canary"]["documents_indexed"], 1)
            self.assertGreaterEqual(payload["live_canary"]["restart_local_search_hits"], 1)
        else:
            self.assertEqual("waiting", payload["checks"][-1]["status"])


if __name__ == "__main__":
    unittest.main()
