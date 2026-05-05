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


class DryRunDeepExtractionRequestTests(DeepExtractionTestMixin, unittest.TestCase):
    def test_dry_run_outputs_request_json_only(self):
        result = run_cmd("scripts/dry_run_deep_extraction_request.py", "--label", "Example archive", "--container-kind", "zip_archive", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["extraction_request_kind"], "deep_extraction_request")
        self.assertIs(payload["extraction_executed"], False)
        self.assertIs(payload["files_opened"], False)
        self.assertIs(payload["archive_unpacked"], False)
        self.assertIs(payload["payload_executed"], False)
        self.assertIs(payload["URL_fetched"], False)

    def test_dry_run_output_validates_without_writing_files(self):
        before = {path.name for path in (ROOT / "examples/extraction").iterdir()}
        result = run_cmd("scripts/dry_run_deep_extraction_request.py", "--label", "Example archive", "--container-kind", "zip_archive", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        after = {path.name for path in (ROOT / "examples/extraction").iterdir()}
        self.assertEqual(before, after)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "request.json"
            path.write_text(result.stdout, encoding="utf-8")
            validation = run_cmd("scripts/validate_deep_extraction_request.py", "--request", str(path))
            self.assertEqual(validation.returncode, 0, validation.stderr)


if __name__ == "__main__":
    unittest.main()
