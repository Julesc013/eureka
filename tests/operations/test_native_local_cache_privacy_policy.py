from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
POLICY = PUBLICATION_DIR / "local_cache_privacy_policy.json"
VALIDATOR = REPO_ROOT / "scripts" / "validate_local_cache_privacy_policy.py"
DOCS = [
    REPO_ROOT / "docs" / "reference" / "LOCAL_CACHE_PRIVACY_POLICY.md",
    REPO_ROOT / "docs" / "reference" / "NATIVE_LOCAL_CACHE_CONTRACT.md",
    REPO_ROOT / "docs" / "reference" / "TELEMETRY_AND_LOGGING_POLICY.md",
]


class NativeLocalCachePrivacyPolicyTestCase(unittest.TestCase):
    def test_policy_inventory_is_policy_only(self) -> None:
        payload = _load_json(POLICY)

        self.assertEqual(payload["schema_version"], "0.1.0")
        self.assertEqual(payload["status"], "policy_only")
        self.assertTrue(payload["no_cache_runtime_implemented"])
        self.assertTrue(payload["no_private_ingestion_implemented"])
        self.assertTrue(payload["no_telemetry_implemented"])
        self.assertTrue(payload["no_accounts_implemented"])
        self.assertTrue(payload["no_cloud_sync_implemented"])
        self.assertEqual(payload["privacy_default"], "local_private_off_by_default")
        self.assertEqual(payload["created_by_slice"], "native_local_cache_privacy_policy_v0")

    def test_required_prohibited_behaviors_are_present(self) -> None:
        payload = _load_json(POLICY)
        prohibited = set(payload["prohibited_behaviors"])

        self.assertTrue(
            {
                "automatic_local_archive_scan",
                "private_file_ingestion_by_default",
                "private_uploads",
                "telemetry_by_default",
                "analytics_by_default",
                "cloud_sync_by_default",
                "public_path_leakage",
                "credential_export",
                "old_client_private_relay",
            }.issubset(prohibited)
        )

    def test_docs_state_privacy_first_limits(self) -> None:
        for path in DOCS:
            self.assertTrue(path.is_file(), path)
        text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS).casefold()

        for phrase in (
            "no telemetry is implemented",
            "telemetry must be off by default",
            "no private paths in public reports",
            "must not automatically scan user directories",
            "clear public cache",
            "clear private cache",
            "future requirements, not implemented behavior",
        ):
            self.assertIn(phrase, text)

    def test_related_contracts_reference_policy(self) -> None:
        native = _load_json(PUBLICATION_DIR / "native_client_contract.json")
        relay = _load_json(PUBLICATION_DIR / "relay_surface.json")
        snapshot = _load_json(PUBLICATION_DIR / "snapshot_consumer_contract.json")

        for payload in (native, relay, snapshot):
            self.assertIn("local_cache_privacy_policy_dependency", payload)
            dependency = payload["local_cache_privacy_policy_dependency"]
            self.assertEqual(
                dependency["policy"],
                "control/inventory/publication/local_cache_privacy_policy.json",
            )
            self.assertEqual(dependency["status"], "policy_only")

        self.assertFalse(native["local_cache_privacy_policy_dependency"]["telemetry_implemented"])
        self.assertFalse(relay["local_cache_privacy_policy_dependency"]["telemetry_enabled"])
        self.assertFalse(
            snapshot["local_cache_privacy_policy_dependency"]["snapshots_include_private_data"]
        )

    def test_public_alpha_and_relay_keep_private_data_closed(self) -> None:
        public_alpha = (REPO_ROOT / "docs" / "operations" / "PUBLIC_ALPHA_SAFE_MODE.md").read_text(
            encoding="utf-8"
        ).casefold()
        relay_security = (
            REPO_ROOT / "docs" / "reference" / "RELAY_SECURITY_AND_PRIVACY.md"
        ).read_text(encoding="utf-8").casefold()

        self.assertIn("does not enable private cache", public_alpha)
        self.assertIn("private path exposure", public_alpha)
        self.assertIn("no private cache or diagnostics data", relay_security)
        self.assertIn("no telemetry or analytics through relay surfaces", relay_security)

    def test_validator_passes_and_json_parses(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.assertIn("status: valid", plain.stdout)

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


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
