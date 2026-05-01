from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_local_staging_manifest.py"
EXAMPLE_ROOT = REPO_ROOT / "examples" / "local_staging_manifests" / "minimal_local_staging_manifest_v0"
EXAMPLE_MANIFEST = EXAMPLE_ROOT / "LOCAL_STAGING_MANIFEST.json"


class ValidateLocalStagingManifestScriptTestCase(unittest.TestCase):
    def test_default_and_all_examples_json_pass(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Local Staging Manifest validation", plain.stdout)
        self.assertIn("status: valid", plain.stdout)

        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--all-examples", "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["summary"], {"total": 1, "passed": 1, "failed": 0})
        self.assertFalse(payload["staging_performed"])
        self.assertFalse(payload["import_performed"])
        self.assertFalse(payload["indexing_performed"])
        self.assertFalse(payload["upload_performed"])
        self.assertFalse(payload["public_search_mutated"])
        self.assertFalse(payload["local_index_mutated"])
        self.assertFalse(payload["master_index_mutation_performed"])

    def test_explicit_manifest_and_root_pass(self) -> None:
        for args in [
            ["--manifest", str(EXAMPLE_MANIFEST)],
            ["--manifest-root", str(EXAMPLE_ROOT), "--strict"],
        ]:
            with self.subTest(args=args):
                completed = subprocess.run(
                    [sys.executable, str(VALIDATOR), *args, "--json"],
                    cwd=REPO_ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                payload = json.loads(completed.stdout)
                self.assertTrue(payload["ok"], payload["errors"])
                self.assertEqual(payload["checked_manifests"][0]["manifest_id"], "example.local_staging_manifest.minimal_v0")

    def test_public_search_mutation_fails(self) -> None:
        payload = _load_example()
        payload["public_search_mutated"] = True
        payload["no_mutation_guarantees"]["public_search_mutated"] = True
        completed = _run_temp_manifest(payload)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("public_search_mutated must be false", completed.stdout)

    def test_local_index_mutation_fails(self) -> None:
        payload = _load_example()
        payload["local_index_mutated"] = True
        payload["no_mutation_guarantees"]["local_index_mutated"] = True
        completed = _run_temp_manifest(payload)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("local_index_mutated must be false", completed.stdout)

    def test_master_index_mutation_fails(self) -> None:
        payload = _load_example()
        payload["master_index_mutated"] = True
        payload["no_mutation_guarantees"]["master_index_mutated"] = True
        completed = _run_temp_manifest(payload)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("master_index_mutated must be false", completed.stdout)

    def test_private_absolute_path_fails(self) -> None:
        payload = _load_example()
        payload["source_validate_report_ref"]["limitations"].append(r"C:\Users\Example\private-report.json")
        completed = _run_temp_manifest(payload)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("private absolute paths", completed.stdout)

    def test_invalid_staged_entity_type_fails(self) -> None:
        payload = _load_example()
        payload["staged_entities"][0]["entity_type"] = "canonical_record"
        completed = _run_temp_manifest(payload)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("staged_entities[0].entity_type", completed.stdout)

    def test_missing_reset_delete_export_policy_fails(self) -> None:
        payload = _load_example()
        del payload["reset_delete_export_policy"]
        completed = _run_temp_manifest(payload)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("reset_delete_export_policy", completed.stdout)

    def test_secret_like_value_fails(self) -> None:
        payload = _load_example()
        payload["notes"].append("sk-notARealSecretButForbiddenShape")
        completed = _run_temp_manifest(payload)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("secret-like value", completed.stdout)


def _load_example() -> dict:
    return json.loads(EXAMPLE_MANIFEST.read_text(encoding="utf-8"))


def _run_temp_manifest(payload: dict) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "LOCAL_STAGING_MANIFEST.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--manifest", str(path), "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
