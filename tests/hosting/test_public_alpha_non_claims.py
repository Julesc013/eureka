import json
import unittest
from pathlib import Path

from scripts.validate_hosting_readiness import REQUIRED_NON_CLAIMS, detect_forbidden_hosting_claims

REPO_ROOT = Path(__file__).resolve().parents[2]


class PublicAlphaNonClaimsTests(unittest.TestCase):
    def load_json(self, relative: str) -> dict:
        return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))

    def test_public_alpha_non_claims_are_defined(self) -> None:
        payload = self.load_json("examples/hosting/public_alpha_non_claims_v0.json")
        for key in REQUIRED_NON_CLAIMS:
            self.assertTrue(payload[key], key)
        self.assertTrue(payload["source_limitations_required"])
        self.assertTrue(payload["evidence_limitations_required"])
        self.assertTrue(payload["review_limitations_required"])

    def test_public_alpha_live_claim_without_evidence_fails(self) -> None:
        errors = detect_forbidden_hosting_claims({"public_alpha_live_claimed": True, "message": "public alpha is live"})
        self.assertGreaterEqual(len(errors), 2)

    def test_upload_account_telemetry_and_live_fanout_claims_fail(self) -> None:
        payload = {
            "enabled_uploads": True,
            "enabled_accounts": True,
            "enabled_telemetry": True,
            "enabled_live_source_fanout": True,
        }
        self.assertEqual(len(detect_forbidden_hosting_claims(payload)), 4)

    def test_secret_like_values_fail(self) -> None:
        errors = detect_forbidden_hosting_claims({"provider_token_fixture": "sk-live-example-secret"})
        self.assertEqual(len(errors), 1)


if __name__ == "__main__":
    unittest.main()
