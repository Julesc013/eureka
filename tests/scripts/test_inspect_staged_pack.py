from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "inspect_staged_pack.py"
EXAMPLE_ROOT = REPO_ROOT / "examples" / "local_staging_manifests" / "minimal_local_staging_manifest_v0"
EXAMPLE_MANIFEST = EXAMPLE_ROOT / "LOCAL_STAGING_MANIFEST.json"
HARD_FALSE_FIELDS = [
    "model_calls_performed",
    "mutation_performed",
    "staging_performed",
    "import_performed",
    "indexing_performed",
    "upload_performed",
    "master_index_mutation_performed",
    "runtime_mutation_performed",
    "network_performed",
    "public_search_mutated",
    "local_index_mutated",
]


class InspectStagedPackScriptTestCase(unittest.TestCase):
    def test_list_examples_succeeds(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--list-examples"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Staged Pack Inspector examples", completed.stdout)
        self.assertIn("minimal_local_staging_manifest_v0", completed.stdout)
        self.assertIn("staging_performed: False", completed.stdout)

    def test_all_examples_human_and_json_succeed(self) -> None:
        human = subprocess.run(
            [sys.executable, str(SCRIPT), "--all-examples"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Staged Pack Inspection", human.stdout)
        self.assertIn("inspection only; no staging/import/index/search/master-index mutation performed", human.stdout)
        self.assertIn("candidate_semantics", human.stdout)

        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--all-examples", "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["summary"], {"total": 1, "passed": 1, "failed": 0, "unavailable": 0})
        self.assertEqual(payload["inspected_manifests"][0]["validation_status"], "passed")
        _assert_no_mutation(self, payload)

    def test_explicit_manifest_and_root_succeed(self) -> None:
        for args in [
            ["--manifest", str(EXAMPLE_MANIFEST)],
            ["--manifest-root", str(EXAMPLE_ROOT)],
        ]:
            with self.subTest(args=args):
                completed = subprocess.run(
                    [sys.executable, str(SCRIPT), *args, "--json"],
                    cwd=REPO_ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                payload = json.loads(completed.stdout)
                self.assertTrue(payload["ok"], payload["errors"])
                self.assertEqual(payload["inspected_manifests"][0]["manifest_id"], "example.local_staging_manifest.minimal_v0")
                _assert_no_mutation(self, payload)

    def test_invalid_manifest_fails_under_strict_validation(self) -> None:
        payload = _load_example()
        payload["public_search_mutated"] = True
        payload["no_mutation_guarantees"]["public_search_mutated"] = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "LOCAL_STAGING_MANIFEST.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--manifest", str(path), "--strict", "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        result = json.loads(completed.stdout)
        self.assertFalse(result["ok"])
        self.assertEqual(result["inspected_manifests"][0]["validation_status"], "failed")
        self.assertIn("public_search_mutated must be false", json.dumps(result))
        _assert_no_mutation(self, result)

    def test_redaction_helper_redacts_private_paths_and_secrets(self) -> None:
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            import inspect_staged_pack
        finally:
            sys.path.pop(0)

        redacted = inspect_staged_pack.redact_sensitive(
            {
                "local_path": r"C:\Users\Example\private\manifest.json",
                "home_path": "/home/example/private/manifest.json",
                "api_key": "sk-exampleSecretValue",
                "notes": ["safe", "-----BEGIN PRIVATE KEY-----"],
            }
        )
        rendered = json.dumps(redacted)
        self.assertIn("<redacted-local-path>", rendered)
        self.assertIn("<redacted-secret", rendered)
        self.assertNotIn("C:\\Users\\Example", rendered)
        self.assertNotIn("/home/example", rendered)
        self.assertNotIn("sk-exampleSecretValue", rendered)

    def test_no_validate_inspection_redacts_private_path_fields(self) -> None:
        payload = _load_example()
        payload["limitations"].append(r"C:\Users\Example\private-staging\manifest.json")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "LOCAL_STAGING_MANIFEST.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--manifest", str(path), "--no-validate", "--json"],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
        rendered = completed.stdout
        self.assertIn("<redacted-local-path>", rendered)
        self.assertNotIn("C:\\Users\\Example", rendered)
        payload = json.loads(rendered)
        self.assertEqual(payload["inspected_manifests"][0]["validation_status"], "skipped")
        _assert_no_mutation(self, payload)


def _load_example() -> dict:
    return json.loads(EXAMPLE_MANIFEST.read_text(encoding="utf-8"))


def _assert_no_mutation(testcase: unittest.TestCase, payload: dict) -> None:
    for field in HARD_FALSE_FIELDS:
        testcase.assertFalse(payload[field], field)


if __name__ == "__main__":
    unittest.main()
