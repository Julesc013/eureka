from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = REPO_ROOT / "control" / "inventory" / "publication" / "snapshot_consumer_contract.json"
PROFILES = REPO_ROOT / "control" / "inventory" / "publication" / "snapshot_consumer_profiles.json"
SEED_ROOT = REPO_ROOT / "snapshots" / "examples" / "static_snapshot_v0"
DOC = REPO_ROOT / "docs" / "reference" / "SNAPSHOT_CONSUMER_CONTRACT.md"
VALIDATOR = REPO_ROOT / "scripts" / "validate_snapshot_consumer_contract.py"


class SignedSnapshotConsumerContractTestCase(unittest.TestCase):
    def test_contract_inventory_exists_and_is_design_only(self) -> None:
        contract = _load_json(CONTRACT)

        self.assertEqual(contract["schema_version"], "0.1.0")
        self.assertEqual(contract["status"], "design_only")
        self.assertFalse(contract["production_consumer_implemented"])
        self.assertFalse(contract["native_consumer_implemented"])
        self.assertFalse(contract["relay_consumer_implemented"])
        self.assertEqual(contract["created_by_slice"], "signed_snapshot_consumer_contract_v0")

    def test_required_read_order_matches_seed_snapshot_files(self) -> None:
        contract = _load_json(CONTRACT)
        expected = [
            "README_FIRST.txt",
            "SNAPSHOT_MANIFEST.json",
            "BUILD_MANIFEST.json",
            "CHECKSUMS.SHA256",
            "SOURCE_SUMMARY.json",
            "EVAL_SUMMARY.json",
            "ROUTE_SUMMARY.json",
            "PAGE_REGISTRY.json",
        ]

        self.assertEqual(contract["required_read_order"], expected)
        for relative in expected:
            self.assertTrue((SEED_ROOT / relative).is_file(), relative)

    def test_profiles_exist_and_remain_future_or_design_only(self) -> None:
        profiles = _load_json(PROFILES)
        by_id = {profile["id"]: profile for profile in profiles["profiles"]}

        self.assertEqual(
            set(by_id),
            {
                "minimal_file_tree_consumer",
                "text_snapshot_consumer",
                "lite_html_snapshot_consumer",
                "relay_snapshot_consumer",
                "native_snapshot_consumer",
                "audit_tool_consumer",
            },
        )
        for profile in by_id.values():
            with self.subTest(profile=profile["id"]):
                self.assertIn(profile["status"], {"design_only", "future_deferred"})
                self.assertNotEqual(profile["current_implementation_status"], "implemented")
                self.assertFalse(profile["can_verify_signatures"])
                self.assertFalse(profile["can_handle_private_data"])
                self.assertFalse(profile["requires_live_backend"])

    def test_minimum_consumer_profile_does_not_require_live_backend(self) -> None:
        contract = _load_json(CONTRACT)
        minimum = contract["minimum_consumer_profile"]

        self.assertEqual(minimum["profile_id"], "minimal_file_tree_consumer")
        self.assertFalse(minimum["requires_live_backend"])
        self.assertFalse(minimum["requires_network"])
        self.assertIn("warn or fail closed when checksum verification is unavailable", minimum["required_capabilities"])

    def test_docs_state_limitations(self) -> None:
        text = DOC.read_text(encoding="utf-8").casefold()

        for phrase in (
            "there is no production consumer in v0",
            "v0 signatures are placeholders",
            "no real signing keys",
            "no private keys are stored",
            "does not implement a snapshot reader runtime",
            "does not implement a relay",
            "does not implement a native client",
        ):
            self.assertIn(phrase, text)

    def test_validator_passes_and_json_parses(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(plain.returncode, 0, plain.stderr)

        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertFalse(payload["production_consumer_implemented"])
        self.assertFalse(payload["native_consumer_implemented"])
        self.assertFalse(payload["relay_consumer_implemented"])

    def test_no_private_key_files_added(self) -> None:
        forbidden_suffixes = {".pem", ".key", ".pfx", ".p12", ".crt", ".cer"}
        offenders: list[str] = []
        for path in REPO_ROOT.rglob("*"):
            if ".git" in path.parts or not path.is_file():
                continue
            if path.suffix.casefold() in forbidden_suffixes:
                offenders.append(str(path.relative_to(REPO_ROOT)))
        self.assertEqual(offenders, [])


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
