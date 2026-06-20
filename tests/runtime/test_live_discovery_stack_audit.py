from __future__ import annotations

import json
import subprocess
import sys
import unittest


class LiveDiscoveryStackAuditTests(unittest.TestCase):
    def test_audit_has_no_critical_or_high_blockers(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/check_live_discovery_stack_audit.py", "--json"],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass_with_warnings", payload["status"])
        self.assertEqual(0, payload["critical_findings"])
        self.assertEqual(0, payload["high_findings"])
        self.assertFalse(payload["provider_result_payload_persisted"])
        self.assertFalse(payload["production_scale_claimed"])


if __name__ == "__main__":
    unittest.main()
