from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
POLICY = PUBLICATION_DIR / "action_policy.json"
VALIDATOR = REPO_ROOT / "scripts" / "validate_action_policy.py"
DOCS = [
    REPO_ROOT / "docs" / "reference" / "ACTION_DOWNLOAD_INSTALL_POLICY.md",
    REPO_ROOT / "docs" / "reference" / "EXECUTABLE_RISK_POLICY.md",
    REPO_ROOT / "docs" / "reference" / "RIGHTS_AND_ACCESS_POLICY.md",
    REPO_ROOT / "docs" / "reference" / "INSTALL_HANDOFF_CONTRACT.md",
]


class ActionDownloadInstallPolicyTestCase(unittest.TestCase):
    def test_action_policy_inventory_is_policy_only(self) -> None:
        payload = _load_json(POLICY)

        self.assertEqual(payload["schema_version"], "0.1.0")
        self.assertEqual(payload["status"], "policy_only")
        self.assertTrue(payload["no_install_automation_implemented"])
        self.assertTrue(payload["no_download_surface_implemented"])
        self.assertTrue(payload["no_malware_scanning_claim"])
        self.assertTrue(payload["no_rights_clearance_claim"])
        self.assertEqual(payload["created_by_slice"], "native_action_download_install_policy_v0")

    def test_required_action_classes_are_present(self) -> None:
        payload = _load_json(POLICY)
        safe = {item["id"] for item in payload["current_safe_actions"]}
        bounded = {item["id"] for item in payload["current_bounded_actions"]}
        future = set(payload["future_gated_actions"])
        prohibited = set(payload["prohibited_until_policy"])

        self.assertTrue(
            {
                "inspect",
                "preview",
                "read",
                "cite",
                "export_manifest",
                "view_provenance",
                "compare",
                "view_absence_report",
                "view_source",
            }.issubset(safe)
        )
        self.assertTrue(
            {
                "fetch_fixture_payload",
                "member_preview",
                "local_export_manifest",
                "local_store_artifact_fixture",
            }.issubset(bounded)
        )
        self.assertTrue(
            {
                "download",
                "download_member",
                "mirror",
                "install_handoff",
                "package_manager_handoff",
                "execute",
                "restore_manifest_apply",
                "uninstall",
                "rollback",
                "scan_for_malware",
            }.issubset(future)
        )
        self.assertTrue(
            {
                "silent_install",
                "auto_execute",
                "privileged_install",
                "upload_private_files",
                "bypass_rights_warning",
                "bypass_hash_warning",
            }.issubset(prohibited)
        )

    def test_public_alpha_and_static_defaults_disable_risky_actions(self) -> None:
        payload = _load_json(POLICY)
        for defaults_name in ("public_alpha_defaults", "static_site_defaults"):
            defaults = payload[defaults_name]
            with self.subTest(defaults=defaults_name):
                self.assertFalse(defaults["downloads_enabled"])
                self.assertFalse(defaults["install_handoff_enabled"])
                self.assertFalse(defaults["package_manager_handoff_enabled"])
                self.assertFalse(defaults["mirror_enabled"])
                self.assertFalse(defaults["execute_enabled"])
                self.assertFalse(defaults["malware_scanning_enabled"])
                self.assertFalse(defaults["rights_clearance_claimed"])

    def test_policy_docs_exist_and_state_limits(self) -> None:
        for path in DOCS:
            self.assertTrue(path.is_file(), path)
        text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS).casefold()

        for phrase in (
            "no malware safety claim exists",
            "no rights clearance claim exists",
            "install handoff is user-initiated delegation",
            "install automation is not implemented",
            "hashes do not prove safety",
            "source metadata is not rights clearance",
        ):
            self.assertIn(phrase, text)

    def test_install_handoff_is_not_install_automation(self) -> None:
        text = (REPO_ROOT / "docs" / "reference" / "INSTALL_HANDOFF_CONTRACT.md").read_text(
            encoding="utf-8"
        ).casefold()

        self.assertIn("install handoff is user-initiated delegation", text)
        self.assertIn("not silent installation", text)
        self.assertIn("not package-manager mutation", text)
        self.assertIn("not privilege escalation", text)

    def test_related_contracts_reference_action_policy(self) -> None:
        native = _load_json(PUBLICATION_DIR / "native_client_contract.json")
        snapshot = _load_json(PUBLICATION_DIR / "snapshot_consumer_contract.json")
        relay = _load_json(PUBLICATION_DIR / "relay_surface.json")

        self.assertIn("action_policy_dependency", native)
        self.assertIn("action_policy_dependency", snapshot)
        self.assertIn("action_policy_dependency", relay)
        self.assertFalse(native["action_policy_dependency"]["downloads_enabled"])
        self.assertFalse(snapshot["action_policy_dependency"]["downloads_enabled"])
        self.assertFalse(relay["action_policy_dependency"]["downloads_enabled"])

    def test_static_site_does_not_claim_installer_or_app_store_behavior(self) -> None:
        text = (REPO_ROOT / "public_site" / "limitations.html").read_text(
            encoding="utf-8"
        ).casefold()

        self.assertIn("no installer automation", text)
        self.assertIn("download", text)
        self.assertNotIn("app store workflow is available", text)
        self.assertNotIn("installer available", text)
        self.assertNotIn("downloads are enabled", text)

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
