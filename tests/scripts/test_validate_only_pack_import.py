from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL = REPO_ROOT / "scripts" / "validate_only_pack_import.py"
REPORT_VALIDATOR = REPO_ROOT / "scripts" / "validate_pack_import_report.py"
REGISTRY = REPO_ROOT / "control" / "inventory" / "packs" / "example_packs.json"


class ValidateOnlyPackImportScriptTestCase(unittest.TestCase):
    def test_list_examples_succeeds(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TOOL), "--list-examples"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Validate-Only Pack Import examples", completed.stdout)
        self.assertIn("source_pack", completed.stdout)
        self.assertIn("master_index_review_queue", completed.stdout)
        self.assertIn("import_performed: False", completed.stdout)

    def test_all_examples_json_report_validates(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TOOL), "--all-examples", "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["schema_version"], "pack_import_report.v0")
        self.assertEqual(payload["report_status"], "validate_only_passed")
        self.assertEqual(payload["mode"], "validate_only")
        self.assertEqual(payload["validation_summary"], {
            "total": 5,
            "passed": 5,
            "failed": 0,
            "unavailable": 0,
            "unknown_type": 0,
            "skipped": 0,
        })
        _assert_no_mutation(self, payload)
        self.assertTrue(_report_validates(payload))

    def test_include_ai_outputs_adds_ai_output_bundle_without_model_calls(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TOOL), "--all-examples", "--include-ai-outputs", "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["validation_summary"]["total"], 6)
        ai_results = [result for result in payload["pack_results"] if result["pack_type"] == "ai_output_bundle"]
        self.assertEqual(len(ai_results), 1)
        self.assertEqual(ai_results[0]["validation_status"], "passed")
        self.assertEqual(ai_results[0]["validator_id"], "typed_ai_output_validator_v0")
        self.assertIn("no model calls", " ".join(ai_results[0]["limitations"]).lower())
        _assert_no_mutation(self, payload)
        self.assertTrue(_report_validates(payload))

    def test_each_registered_example_validates_as_explicit_pack_root(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        for example in registry["examples"]:
            with self.subTest(example=example["pack_id"]):
                completed = subprocess.run(
                    [sys.executable, str(TOOL), "--pack-root", example["path"], "--json"],
                    cwd=REPO_ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                payload = json.loads(completed.stdout)
                self.assertEqual(payload["report_status"], "validate_only_passed")
                self.assertEqual(payload["validation_summary"]["passed"], 1)
                self.assertEqual(payload["pack_results"][0]["pack_type"], example["pack_type"])
                _assert_no_mutation(self, payload)

    def test_output_writes_only_explicit_report_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_path = tmp_path / "validate-only-report.json"
            before = {path.name for path in tmp_path.iterdir()}
            completed = subprocess.run(
                [sys.executable, str(TOOL), "--all-examples", "--output", str(output_path), "--json"],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            after = {path.name for path in tmp_path.iterdir()}
            self.assertEqual(after - before, {"validate-only-report.json"})
            stdout_payload = json.loads(completed.stdout)
            file_payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(file_payload["report_id"], stdout_payload["report_id"])
            self.assertIn("<explicit-local-path>", file_payload["mutation_summary"]["files_written"])
            _assert_no_mutation(self, file_payload)
            self.assertTrue(_report_file_validates(output_path))

    def test_unknown_pack_root_fails_strict_with_redacted_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "not-a-pack"
            root.mkdir()
            (root / "README.md").write_text("not a pack\n", encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(TOOL), "--pack-root", str(root), "--strict", "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["report_status"], "unsupported_pack_type")
        self.assertEqual(payload["validation_summary"]["unknown_type"], 1)
        self.assertEqual(payload["pack_results"][0]["recommended_next_action"], "unsupported")
        self.assertIn("<explicit-local-path>", json.dumps(payload))
        self.assertNotIn(str(root), json.dumps(payload))
        _assert_no_mutation(self, payload)
        self.assertTrue(_report_validates(payload))

    def test_invalid_pack_root_fails_with_fix_and_revalidate_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "broken-source-pack"
            root.mkdir()
            (root / "SOURCE_PACK.json").write_text("{}\n", encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(TOOL), "--pack-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["report_status"], "validate_only_failed")
        self.assertEqual(payload["next_actions"][0]["action"], "fix_pack_and_revalidate")
        self.assertEqual(payload["pack_results"][0]["validation_status"], "failed")
        _assert_no_mutation(self, payload)
        self.assertTrue(_report_validates(payload))

    def test_missing_output_parent_fails_without_creating_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing_parent = Path(tmp) / "missing"
            output_path = missing_parent / "report.json"
            completed = subprocess.run(
                [sys.executable, str(TOOL), "--all-examples", "--output", str(output_path), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertFalse(missing_parent.exists())
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["import_performed"])
        self.assertFalse(payload["staging_performed"])
        self.assertIn("parent does not exist", payload["error"])

    def test_forbidden_repo_output_root_fails_without_writing(self) -> None:
        output_path = REPO_ROOT / "site" / "dist" / "forbidden-pack-report.json"
        if output_path.exists():
            output_path.unlink()
        completed = subprocess.run(
            [sys.executable, str(TOOL), "--all-examples", "--output", str(output_path), "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertFalse(output_path.exists())
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["import_performed"])
        self.assertFalse(payload["staging_performed"])
        self.assertIn("forbidden repo root", payload["error"])


def _assert_no_mutation(testcase: unittest.TestCase, payload: dict) -> None:
    for field in [
        "import_performed",
        "staging_performed",
        "indexing_performed",
        "upload_performed",
        "master_index_mutation_performed",
        "runtime_mutation_performed",
        "network_performed",
    ]:
        testcase.assertFalse(payload[field], field)
        testcase.assertFalse(payload["mutation_summary"][field], f"mutation_summary.{field}")


def _report_validates(payload: dict) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "report.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return _report_file_validates(path)


def _report_file_validates(path: Path) -> bool:
    completed = subprocess.run(
        [sys.executable, str(REPORT_VALIDATOR), "--report", str(path), "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0 and json.loads(completed.stdout)["ok"]


if __name__ == "__main__":
    unittest.main()
