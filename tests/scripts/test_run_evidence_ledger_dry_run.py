import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RunEvidenceLedgerDryRunCliTests(unittest.TestCase):
    def test_all_examples_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/run_evidence_ledger_dry_run.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "local_dry_run")
        self.assertEqual(payload["candidates_seen"], 7)
        self.assertEqual(payload["candidates_invalid"], 0)
        self.assertFalse(payload["hard_booleans"]["external_calls_performed"])
        self.assertFalse(payload["hard_booleans"]["claim_accepted_as_truth"])

    def test_forbidden_args_rejected(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/run_evidence_ledger_dry_run.py", "--accept-truth"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("forbidden", completed.stderr)

    def test_invalid_example_fails_in_strict_temp_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "EVIDENCE_LEDGER_CANDIDATE.json").write_text('{"candidate_id": "bad"}', encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_evidence_ledger_dry_run.py",
                    "--example-root",
                    str(root),
                    "--strict",
                    "--json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["candidates_invalid"], 1)

    def test_output_path_outside_allowed_destination_rejected(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/run_evidence_ledger_dry_run.py",
                "--all-examples",
                "--output",
                str(ROOT / "runtime" / "_evidence_ledger_dry_run_report.json"),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("output path is not approved", completed.stderr)

    def test_output_path_under_temp_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_evidence_ledger_dry_run.py",
                    "--all-examples",
                    "--json",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertTrue(output.is_file())
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), json.loads(completed.stdout))


if __name__ == "__main__":
    unittest.main()
