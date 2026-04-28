from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_publication_inventory.py"
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"


class ValidatePublicationInventoryScriptTest(unittest.TestCase):
    def test_validator_passes_plain_and_json(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", plain.stdout)
        self.assertIn("registered_routes:", plain.stdout)

        payload = self._run_json()
        self.assertEqual(payload["status"], "valid")
        self.assertIn("/lite/", payload["reserved_routes"])
        self.assertIn("modern_web", payload["required_client_profiles"])
        self.assertIn("/data/site_manifest.json", payload["required_public_data_paths"])
        self.assertIn("/demo/data/demo_snapshots.json", payload["required_public_data_paths"])
        self.assertTrue(payload["snapshot_contract_checked"])
        self.assertEqual(payload["errors"], [])

    def test_validator_reports_missing_status_taxonomy_value(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_inventory = Path(temp_dir) / "publication"
            shutil.copytree(PUBLICATION_DIR, temp_inventory)
            contract_path = temp_inventory / "publication_contract.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["public_status_taxonomy"] = [
                item
                for item in contract["public_status_taxonomy"]
                if item.get("id") != "unsafe_for_public_alpha"
            ]
            contract_path.write_text(json.dumps(contract, indent=2), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--inventory-dir",
                    str(temp_inventory),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "invalid")
        self.assertTrue(
            any("unsafe_for_public_alpha" in error for error in payload["errors"])
        )

    def test_validator_rejects_reserved_route_marked_implemented(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_inventory = Path(temp_dir) / "publication"
            shutil.copytree(PUBLICATION_DIR, temp_inventory)
            registry_path = temp_inventory / "page_registry.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            for route in registry["routes"]:
                if route["path"] == "/api/":
                    route["status"] = "implemented"
                    break
            registry_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--inventory-dir",
                    str(temp_inventory),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("reserved route /api/" in error for error in payload["errors"]))

    def _run_json(self) -> dict:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
