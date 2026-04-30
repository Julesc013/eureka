from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_pack_import_report.py"
PASSED_EXAMPLE = REPO_ROOT / "examples" / "import_reports" / "validate_only_all_examples.passed.json"
PRIVATE_PATH_EXAMPLE = REPO_ROOT / "examples" / "import_reports" / "validate_only_private_path.failed.json"
UNKNOWN_EXAMPLE = REPO_ROOT / "examples" / "import_reports" / "validate_only_unknown_pack_type.failed.json"


class ValidatePackImportReportScriptTestCase(unittest.TestCase):
    def test_default_and_all_examples_json_pass(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Pack Import Report validation", plain.stdout)
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
        self.assertEqual(payload["summary"], {"total": 3, "passed": 3, "failed": 0})
        self.assertFalse(payload["import_performed"])
        self.assertFalse(payload["staging_performed"])
        self.assertFalse(payload["indexing_performed"])
        self.assertFalse(payload["upload_performed"])
        self.assertFalse(payload["master_index_mutation_performed"])
        self.assertFalse(payload["runtime_mutation_performed"])

    def test_each_example_validates_explicitly(self) -> None:
        for example in [PASSED_EXAMPLE, PRIVATE_PATH_EXAMPLE, UNKNOWN_EXAMPLE]:
            with self.subTest(example=example.name):
                completed = subprocess.run(
                    [sys.executable, str(VALIDATOR), "--report", str(example), "--json"],
                    cwd=REPO_ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                payload = json.loads(completed.stdout)
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["summary"]["passed"], 1)

    def test_example_statuses_are_preserved(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--all-examples", "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        reports = {item["path"]: item for item in json.loads(completed.stdout)["checked_reports"]}
        self.assertEqual(reports["examples/import_reports/validate_only_all_examples.passed.json"]["report_status"], "validate_only_passed")
        self.assertEqual(reports["examples/import_reports/validate_only_private_path.failed.json"]["report_status"], "validate_only_failed")
        self.assertEqual(reports["examples/import_reports/validate_only_unknown_pack_type.failed.json"]["report_status"], "unsupported_pack_type")

    def test_import_performed_true_fails(self) -> None:
        payload = _load_passed_example()
        payload["import_performed"] = True
        completed = _run_temp_report(payload)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("import_performed must be false", completed.stdout)

    def test_master_index_mutation_true_fails(self) -> None:
        payload = _load_passed_example()
        payload["master_index_mutation_performed"] = True
        payload["mutation_summary"]["master_index_mutation_performed"] = True
        completed = _run_temp_report(payload)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("master_index_mutation_performed must be false", completed.stdout)

    def test_unsupported_next_action_fails(self) -> None:
        payload = _load_passed_example()
        payload["next_actions"][0]["action"] = "import_now"
        completed = _run_temp_report(payload)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("next_actions[0].action", completed.stdout)

    def test_secret_like_field_fails(self) -> None:
        payload = _load_passed_example()
        payload["api_key"] = "not-a-real-key"
        completed = _run_temp_report(payload)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("secret-like field", completed.stdout)

    def test_private_absolute_path_fails(self) -> None:
        payload = _load_passed_example()
        payload["input_roots"][0]["root"] = r"C:\Users\Example\private-pack"
        completed = _run_temp_report(payload)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("private absolute paths", completed.stdout)

    def test_success_report_with_failed_pack_result_fails(self) -> None:
        payload = _load_passed_example()
        payload["pack_results"][0]["validation_status"] = "failed"
        payload["validation_summary"]["passed"] = 5
        payload["validation_summary"]["failed"] = 1
        completed = _run_temp_report(payload)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("validate_only_passed requires every pack_result", completed.stdout)

    def test_module_reports_private_path_example_as_valid_redacted_fixture(self) -> None:
        module = _load_validator_module()
        result = module.validate_report_file(PRIVATE_PATH_EXAMPLE)
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["report_status"], "validate_only_failed")


def _load_passed_example() -> dict:
    return json.loads(PASSED_EXAMPLE.read_text(encoding="utf-8"))


def _run_temp_report(payload: dict) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "report.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--report", str(path), "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )


def _load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_pack_import_report", VALIDATOR)
    if spec is None or spec.loader is None:
        raise AssertionError("Unable to load validate_pack_import_report module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    unittest.main()
