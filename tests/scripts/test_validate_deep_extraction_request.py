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


class ValidateDeepExtractionRequestTests(DeepExtractionTestMixin, unittest.TestCase):
    def test_validator_passes_and_json_parses(self):
        result = run_cmd("scripts/validate_deep_extraction_request.py", "--all-examples")
        self.assertEqual(result.returncode, 0, result.stderr)
        result_json = run_cmd("scripts/validate_deep_extraction_request.py", "--all-examples", "--json")
        self.assertEqual(result_json.returncode, 0, result_json.stderr)
        payload = json.loads(result_json.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["error_count"], 0)

    def test_hard_booleans_false(self):
        hard_false = [
            "runtime_extraction_implemented",
            "extraction_executed",
            "files_opened",
            "archive_unpacked",
            "payload_executed",
            "installer_executed",
            "package_manager_invoked",
            "emulator_vm_launched",
            "OCR_performed",
            "transcription_performed",
            "live_source_called",
            "external_calls_performed",
            "URL_fetched",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "public_index_mutated",
            "local_index_mutated",
            "master_index_mutated",
            "telemetry_exported",
        ]
        for request_path in (ROOT / "examples/extraction").glob("*/DEEP_EXTRACTION_REQUEST.json"):
            data = json.loads(request_path.read_text(encoding="utf-8"))
            for key in hard_false:
                self.assertIs(data[key], False, f"{request_path}:{key}")

    def test_negative_hard_false_fields_fail(self):
        source = self.load("examples/extraction/minimal_archive_member_listing_v0/DEEP_EXTRACTION_REQUEST.json")
        for field in ("extraction_executed", "files_opened", "archive_unpacked", "payload_executed", "URL_fetched"):
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "request.json"
                bad = copy.deepcopy(source)
                bad[field] = True
                path.write_text(json.dumps(bad), encoding="utf-8")
                result = run_cmd("scripts/validate_deep_extraction_request.py", "--request", str(path))
                self.assertNotEqual(result.returncode, 0, field)

    def test_negative_private_path_fails(self):
        source = self.load("examples/extraction/minimal_archive_member_listing_v0/DEEP_EXTRACTION_REQUEST.json")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "request.json"
            bad = copy.deepcopy(source)
            bad["target_ref"]["target_path_public_safe"] = "../private/secret.txt"
            path.write_text(json.dumps(bad), encoding="utf-8")
            result = run_cmd("scripts/validate_deep_extraction_request.py", "--request", str(path))
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
