import json
import unittest
from pathlib import Path

from scripts.validate_hosting_readiness import REQUIRED_CONTRACTS, REQUIRED_CONFIG_KEYS, validate_hosting_readiness

REPO_ROOT = Path(__file__).resolve().parents[2]


class HostingContractTests(unittest.TestCase):
    def load_json(self, relative: str) -> dict:
        return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))

    def test_contract_json_files_exist(self) -> None:
        for relative in REQUIRED_CONTRACTS:
            self.assertTrue((REPO_ROOT / relative).is_file(), relative)
            self.assertIn("schema_version", self.load_json(relative).get("properties", {}))

    def test_host_profile_examples_validate(self) -> None:
        for path in (REPO_ROOT / "examples" / "hosting" / "host_profiles").glob("*.json"):
            payload = self.load_json(path.relative_to(REPO_ROOT).as_posix())
            self.assertEqual(payload["schema_version"], "host_profile.v0")
            self.assertFalse(payload["product_boundary"]["enabled_hosting"])

    def test_environment_examples_validate(self) -> None:
        for path in (REPO_ROOT / "examples" / "hosting" / "environments").glob("*.json"):
            payload = self.load_json(path.relative_to(REPO_ROOT).as_posix())
            self.assertEqual(payload["schema_version"], "deployment_environment.v0")
            self.assertFalse(payload["truth_boundary"]["public_alpha_live_claimed"])

    def test_runtime_config_boundaries_cover_required_keys(self) -> None:
        payload = self.load_json("examples/hosting/config/runtime_config_boundary_v0.json")
        seen = {entry["config_key"] for entry in payload["config_boundaries"]}
        self.assertEqual(seen, set(REQUIRED_CONFIG_KEYS))
        for entry in payload["config_boundaries"]:
            self.assertTrue(entry["fail_closed_default"])

    def test_validator_passes_current_repo(self) -> None:
        report = validate_hosting_readiness(REPO_ROOT)
        self.assertEqual(report["status"], "pass", report)


if __name__ == "__main__":
    unittest.main()
