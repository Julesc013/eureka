import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "source_pages" / "minimal_fixture_source_page_v0" / "SOURCE_PAGE.json"


class SourcePageValidatorTests(unittest.TestCase):
    def test_validator_passes_all_examples(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_source_page.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("example_count: 4", completed.stdout)

    def test_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_source_page.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 4)

    def test_hard_booleans_and_coverage_are_safe(self) -> None:
        page = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        for key in (
            "runtime_source_page_implemented",
            "persistent_source_page_store_implemented",
            "connector_live_enabled",
            "live_source_called",
            "external_calls_performed",
            "source_sync_worker_executed",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "candidate_promotion_performed",
            "public_index_mutated",
            "local_index_mutated",
            "master_index_mutated",
            "downloads_enabled",
            "uploads_enabled",
            "installs_enabled",
            "execution_enabled",
            "arbitrary_url_fetch_enabled",
            "rights_clearance_claimed",
            "malware_safety_claimed",
            "source_trust_claimed",
        ):
            self.assertFalse(page[key])
        self.assertFalse(page["source_status"]["live_enabled"])
        self.assertFalse(page["source_status"]["public_search_live_fanout_allowed"])
        self.assertTrue(page["coverage"]["source_coverage_claim_not_exhaustive"])

    def test_negative_mutations_and_actions_fail(self) -> None:
        for path, value in (
            (("runtime_source_page_implemented",), True),
            (("connector_live_enabled",), True),
            (("live_source_called",), True),
            (("downloads_enabled",), True),
            (("installs_enabled",), True),
            (("execution_enabled",), True),
            (("source_cache_mutated",), True),
            (("evidence_ledger_mutated",), True),
            (("master_index_mutated",), True),
            (("rights_clearance_claimed",), True),
            (("malware_safety_claimed",), True),
            (("source_trust_claimed",), True),
        ):
            with self.subTest(path=path):
                self._assert_invalid(path, value)

    def test_negative_private_path_fails(self) -> None:
        self._assert_invalid(("notes", 0), "C:\\\\Users\\\\Example\\\\source.txt")

    def test_negative_credential_like_value_fails(self) -> None:
        self._assert_invalid(("notes", 0), "api_key=example-value")

    def _assert_invalid(self, key_path: tuple, value) -> None:
        page = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        target = page
        for part in key_path[:-1]:
            target = target[part]
        target[key_path[-1]] = value
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp) / "SOURCE_PAGE.json"
            tmp_path.write_text(json.dumps(page), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_source_page.py", "--page", str(tmp_path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
