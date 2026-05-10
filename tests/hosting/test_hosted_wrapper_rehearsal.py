import json
import unittest
from pathlib import Path

from scripts.validate_hosted_wrapper_rehearsal import REQUIRED_CONTRACTS, validate_hosted_wrapper_rehearsal
from runtime.hosting.readiness import build_hosted_wrapper_rehearsal

REPO_ROOT = Path(__file__).resolve().parents[2]


class HostedWrapperRehearsalTests(unittest.TestCase):
    def load_json(self, relative: str) -> dict:
        return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))

    def test_rehearsal_contracts_exist(self) -> None:
        for relative in REQUIRED_CONTRACTS:
            self.assertTrue((REPO_ROOT / relative).is_file(), relative)
            self.assertIn("schema_version", self.load_json(relative).get("properties", {}))

    def test_local_fixture_rehearsal_passes_boundaries(self) -> None:
        payload = self.load_json("examples/hosting/rehearsal/hosted_wrapper_rehearsal_local_fixture_v0.json")
        rehearsal = build_hosted_wrapper_rehearsal(payload, {})
        self.assertEqual(rehearsal["rehearsal_status"], "local_fixture_rehearsal")
        self.assertFalse(rehearsal["rehearsal_scope"]["deployment_performed"])
        self.assertFalse(rehearsal["rehearsal_scope"]["provider_api_called"])

    def test_validator_passes_current_repo(self) -> None:
        report = validate_hosted_wrapper_rehearsal(REPO_ROOT)
        self.assertEqual(report["status"], "pass", report)


if __name__ == "__main__":
    unittest.main()
