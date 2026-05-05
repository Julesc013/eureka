from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True)


class DeepExtractionTestMixin:
    maxDiff = None

    def load(self, rel: str):
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class ValidateExtractionResultSummaryTests(DeepExtractionTestMixin, unittest.TestCase):
    def test_validator_passes_and_json_parses(self):
        result = run_cmd("scripts/validate_extraction_result_summary.py", "--all-examples")
        self.assertEqual(result.returncode, 0, result.stderr)
        result_json = run_cmd("scripts/validate_extraction_result_summary.py", "--all-examples", "--json")
        self.assertEqual(result_json.returncode, 0, result_json.stderr)
        payload = json.loads(result_json.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["error_count"], 0)

    def test_hard_booleans_false_and_member_paths_safe(self):
        hard_false = [
            "extraction_result_from_runtime",
            "extraction_executed",
            "raw_payload_included",
            "raw_text_dump_included",
            "OCR_performed",
            "transcription_performed",
            "payload_executed",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "public_index_mutated",
            "master_index_mutated",
            "accepted_as_truth",
            "rights_clearance_claimed",
            "malware_safety_claimed",
        ]
        for summary_path in (ROOT / "examples/extraction").glob("*/EXTRACTION_RESULT_SUMMARY.json"):
            data = json.loads(summary_path.read_text(encoding="utf-8"))
            for key in hard_false:
                self.assertIs(data[key], False, f"{summary_path}:{key}")
            for member in data["member_summaries"]:
                self.assertFalse(member["member_path_public_safe"].startswith("/"))
                self.assertNotIn("..", member["member_path_public_safe"].split("/"))
                self.assertIs(member["payload_included"], False)
                self.assertIs(member["payload_executed"], False)

    def test_executable_payload_risk_labels_present(self):
        data = self.load("examples/extraction/minimal_executable_payload_risk_v0/EXTRACTION_RESULT_SUMMARY.json")
        labels = {label for member in data["member_summaries"] for label in member.get("risk_labels", [])}
        self.assertIn("executable_reference", labels)
        self.assertIn("malware_review_required", labels)
        self.assertIs(data["malware_safety_claimed"], False)

    def test_negative_summary_fields_fail(self):
        source = self.load("examples/extraction/minimal_archive_member_listing_v0/EXTRACTION_RESULT_SUMMARY.json")
        for field in ("raw_payload_included", "OCR_performed", "source_cache_mutated", "master_index_mutated", "malware_safety_claimed"):
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "summary.json"
                bad = copy.deepcopy(source)
                bad[field] = True
                path.write_text(json.dumps(bad), encoding="utf-8")
                result = run_cmd("scripts/validate_extraction_result_summary.py", "--summary", str(path))
                self.assertNotEqual(result.returncode, 0, field)

    def test_negative_private_member_path_fails(self):
        source = self.load("examples/extraction/minimal_archive_member_listing_v0/EXTRACTION_RESULT_SUMMARY.json")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "summary.json"
            bad = copy.deepcopy(source)
            bad["member_summaries"][0]["member_path_public_safe"] = "C:/Users/example/private.txt"
            path.write_text(json.dumps(bad), encoding="utf-8")
            result = run_cmd("scripts/validate_extraction_result_summary.py", "--summary", str(path))
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
