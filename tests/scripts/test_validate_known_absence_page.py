import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "known_absence_pages" / "minimal_no_verified_result_v0" / "KNOWN_ABSENCE_PAGE.json"


class KnownAbsencePageValidatorTests(unittest.TestCase):
    def test_all_examples_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_known_absence_page.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_all_examples_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_known_absence_page.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 3)

    def test_private_path_page_fails(self) -> None:
        payload = self._example_payload()
        payload["query_context"]["normalized_query"] = "C:\\Users\\Alice\\private.txt"
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("windows_absolute_path" in error for error in report["errors"]))

    def test_secret_marker_page_fails(self) -> None:
        payload = self._example_payload()
        payload["query_context"]["normalized_query"] = "api_key should not be here"
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("api_key_marker" in error for error in report["errors"]))

    def test_no_global_absence_flags_fail(self) -> None:
        for field in ("global_absence_claimed", "exhaustive_search_claimed", "live_probes_performed", "external_calls_performed"):
            with self.subTest(field=field):
                payload = self._example_payload()
                payload["no_global_absence_guarantees"][field] = True
                report = self._validate_temp(payload)
                self.assertEqual(report["status"], "invalid")
                self.assertTrue(any(field in error for error in report["errors"]))

    def test_absence_summary_global_flags_fail(self) -> None:
        payload = self._example_payload()
        payload["absence_summary"]["global_absence_claimed"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("absence_summary.global_absence_claimed" in error for error in report["errors"]))

        payload = self._example_payload()
        payload["absence_summary"]["exhaustive_search_claimed"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("absence_summary.exhaustive_search_claimed" in error for error in report["errors"]))

    def test_mutation_flags_fail(self) -> None:
        for field in ("master_index_mutated", "source_cache_mutated", "evidence_ledger_mutated", "candidate_index_mutated"):
            with self.subTest(field=field):
                payload = self._example_payload()
                payload["no_mutation_guarantees"][field] = True
                report = self._validate_temp(payload)
                self.assertEqual(report["status"], "invalid")
                self.assertTrue(any(field in error for error in report["errors"]))

    def test_download_install_upload_actions_cannot_be_enabled(self) -> None:
        payload = self._example_payload()
        payload["safe_next_actions"][0]["label"] = "Download installer now"
        payload["safe_next_actions"][0]["enabled_now"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("prohibited action" in error for error in report["errors"]))

    def test_runtime_candidate_flags_false(self) -> None:
        payload = self._example_payload()
        payload["candidate_context"]["candidate_index_runtime_implemented"] = True
        payload["candidate_context"]["candidate_promotion_runtime_implemented"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("candidate_index_runtime_implemented" in error for error in report["errors"]))
        self.assertTrue(any("candidate_promotion_runtime_implemented" in error for error in report["errors"]))

    def test_checked_scope_and_gaps_required(self) -> None:
        payload = self._example_payload()
        payload["checked_scope"]["checked_indexes"] = []
        payload["gap_explanations"] = []
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("checked_indexes" in error for error in report["errors"]))
        self.assertTrue(any("gap_explanations" in error for error in report["errors"]))

    def _example_payload(self) -> dict:
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def _validate_temp(self, payload: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "KNOWN_ABSENCE_PAGE.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_known_absence_page.py", "--page", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
