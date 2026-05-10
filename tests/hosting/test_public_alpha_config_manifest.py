
import copy
import json
import unittest
from pathlib import Path

from scripts.check_public_alpha_config_manifest import check_config_manifest
from scripts.validate_public_alpha_deployment_plan import detect_forbidden_deployment_claims

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = REPO_ROOT / "examples/hosting/deployment/public_alpha_config_manifest_v0.json"


class PublicAlphaConfigManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_config_manifest_validates(self) -> None:
        self.assertEqual(check_config_manifest(self.config), [])

    def test_config_defaults_disable_risky_features(self) -> None:
        variables = {item["config_key"]: item for item in self.config["config_variables"]}
        self.assertFalse(variables["LIVE_PROBES_ENABLED"]["safe_default"])
        self.assertFalse(variables["DOWNLOADS_ENABLED"]["safe_default"])
        self.assertFalse(variables["UPLOADS_ENABLED"]["safe_default"])
        self.assertFalse(variables["TELEMETRY_ENABLED"]["safe_default"])
        self.assertTrue(variables["KILL_SWITCH_GLOBAL"]["safe_default"])

    def test_risky_default_true_fails(self) -> None:
        broken = copy.deepcopy(self.config)
        for item in broken["config_variables"]:
            if item["config_key"] == "DOWNLOADS_ENABLED":
                item["safe_default"] = True
        self.assertTrue(any("DOWNLOADS_ENABLED" in error for error in check_config_manifest(broken)))

    def test_provider_token_fixture_fails(self) -> None:
        self.assertTrue(detect_forbidden_deployment_claims({"token": "ghp_1234567890abcdef"}))

    def test_deployment_and_claim_true_fail(self) -> None:
        broken = {"deployment_allowed_current": True, "public_alpha_live_claimed": True, "production_claimed": True}
        errors = detect_forbidden_deployment_claims(broken)
        self.assertEqual(len(errors), 3)


if __name__ == "__main__":
    unittest.main()
