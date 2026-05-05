import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DryRunResultMergeGroupTests(unittest.TestCase):
    def test_dry_run_outputs_valid_group_without_runtime_or_mutation(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_result_merge_group.py",
                "--left-title",
                "Example App 1.0",
                "--right-title",
                "ExampleApp v1.0",
                "--relation-type",
                "near_duplicate_result",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        group = json.loads(completed.stdout)
        self.assertEqual(group["status"], "dry_run_validated")
        self.assertEqual(group["group_relation"]["relation_type"], "near_duplicate_result")
        self.assertFalse(group["runtime_result_merge_implemented"])
        self.assertFalse(group["records_merged"])
        self.assertFalse(group["destructive_merge_performed"])
        self.assertFalse(group["public_search_ranking_changed"])
        self.assertFalse(group["live_source_called"])
        self.assertFalse(group["external_calls_performed"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "RESULT_MERGE_GROUP.json"
            path.write_text(json.dumps(group), encoding="utf-8")
            validated = subprocess.run(
                [sys.executable, "scripts/validate_result_merge_group.py", "--group", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
        self.assertEqual(json.loads(validated.stdout)["status"], "valid")


if __name__ == "__main__":
    unittest.main()
