import json
import unittest
from pathlib import Path

from runtime.hosting.blocked_requests import validate_blocked_request_report

REPO_ROOT = Path(__file__).resolve().parents[2]


class PublicAlphaBlockedRequestTests(unittest.TestCase):
    def test_blocked_request_reports_validate(self) -> None:
        for path in (REPO_ROOT / "examples/hosting/blocked_requests").glob("*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(payload["blocked"], path)
            self.assertEqual(validate_blocked_request_report(payload, {})["status"], "pass", path)

    def test_risky_enabled_claim_is_rejected(self) -> None:
        payload = json.loads((REPO_ROOT / "examples/hosting/blocked_requests/download_blocked_request_report_v0.json").read_text(encoding="utf-8"))
        payload["blocked"] = False
        self.assertEqual(validate_blocked_request_report(payload, {})["status"], "fail")


if __name__ == "__main__":
    unittest.main()
