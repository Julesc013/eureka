from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.local.portable_bundle import build_portable_bundle, validate_portable_bundle, version_payload
from runtime.local.portable_instance import CURRENT_INSTANCE_SCHEMA_VERSION, REPO_ROOT, bundle_command, version_command


class PortableBundleTests(unittest.TestCase):
    def test_version_payload_reports_local_preview_boundaries(self) -> None:
        payload = version_payload(repo_root=REPO_ROOT, instance_schema_version=CURRENT_INSTANCE_SCHEMA_VERSION)

        self.assertEqual("eureka.local_preview_version.v0", payload["schema_version"])
        self.assertEqual("eureka.discovery_provider_registry.v0", payload["provider_registry_schema"])
        self.assertFalse(payload["public_exposure"])
        self.assertFalse(payload["public_live_fanout"])
        self.assertFalse(payload["reviewed_master_mutation"])

    def test_bundle_create_and_verify_excludes_private_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            bundle_dir = Path(temp) / "bundle"

            created = build_portable_bundle(repo_root=REPO_ROOT, out_dir=bundle_dir, instance_schema_version=CURRENT_INSTANCE_SCHEMA_VERSION)
            verified = validate_portable_bundle(bundle_dir, repo_root=REPO_ROOT)

            self.assertEqual("pass", created["status"])
            self.assertEqual("pass", verified["status"])
            self.assertFalse(created["provider_result_payload_included"])
            self.assertFalse(created["credential_value_exposed"])
            self.assertFalse(created["private_instance_data_included"])
            self.assertTrue((bundle_dir / "launch.ps1").is_file())
            self.assertTrue((bundle_dir / "launch.sh").is_file())

    def test_portable_commands_create_verify_and_rehearse_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            instance = root / "controller"
            bundle_dir = root / "bundle"
            rehearsal = root / "rehearsal"

            version = version_command(instance=instance)
            created = bundle_command("create", instance=instance, out_dir=bundle_dir)
            verified = bundle_command("verify", instance=instance, bundle=bundle_dir)
            rehearsed = bundle_command("rehearse", instance=instance, bundle=bundle_dir, target=rehearsal)

            self.assertEqual("pass", version["status"])
            self.assertEqual("pass", created["status"])
            self.assertEqual("pass", verified["status"])
            self.assertEqual("pass", rehearsed["status"])
            self.assertFalse(rehearsed["network_provider_calls"])
            self.assertFalse(rehearsed["reviewed_master_mutation"])
            self.assertFalse(rehearsed["public_index_mutation"])
            self.assertEqual("pass", rehearsed["steps"]["bundle_verify"]["status"])
            self.assertIn(rehearsed["steps"]["doctor"]["status"], {"pass", "pass_with_warnings"})


if __name__ == "__main__":
    unittest.main()
