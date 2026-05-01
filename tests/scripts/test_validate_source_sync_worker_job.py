import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "source_sync" / "minimal_ia_metadata_sync_job_v0" / "SOURCE_SYNC_WORKER_JOB.json"
MANUAL_EXAMPLE = ROOT / "examples" / "source_sync" / "minimal_manual_source_review_job_v0" / "SOURCE_SYNC_WORKER_JOB.json"
GITHUB_EXAMPLE = ROOT / "examples" / "source_sync" / "minimal_github_releases_sync_job_v0" / "SOURCE_SYNC_WORKER_JOB.json"


class SourceSyncWorkerJobValidatorTests(unittest.TestCase):
    def test_all_examples_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_source_sync_worker_job.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_all_examples_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_source_sync_worker_job.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 4)

    def test_examples_encode_expected_boundaries(self) -> None:
        for path in (EXAMPLE, MANUAL_EXAMPLE, GITHUB_EXAMPLE):
            with self.subTest(path=path):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertFalse(payload["source_target"]["arbitrary_url_allowed"])
                self.assertFalse(payload["source_policy"]["live_source_enabled_now"])
                self.assertFalse(payload["no_execution_guarantees"]["worker_runtime_implemented"])
                self.assertFalse(payload["no_execution_guarantees"]["job_executed"])
                self.assertFalse(payload["no_execution_guarantees"]["live_source_called"])
                self.assertFalse(payload["no_execution_guarantees"]["external_calls_performed"])
                self.assertFalse(payload["no_execution_guarantees"]["credentials_used"])
                self.assertFalse(payload["no_mutation_guarantees"]["source_cache_mutated"])
                self.assertFalse(payload["no_mutation_guarantees"]["evidence_ledger_mutated"])
                self.assertFalse(payload["no_mutation_guarantees"]["candidate_index_mutated"])
                self.assertFalse(payload["no_mutation_guarantees"]["master_index_mutated"])
                self.assertFalse(payload["rights_and_risk"]["rights_clearance_claimed"])
                self.assertFalse(payload["rights_and_risk"]["malware_safety_claimed"])

    def test_live_network_examples_require_required_gates(self) -> None:
        payload = self._example_payload()
        self.assertTrue(payload["job_kind"]["live_network_required_future"])
        required = {gate["gate_type"] for gate in payload["approval_gates"] if gate["required"]}
        for gate in (
            "source_policy_review",
            "rate_limit_review",
            "user_agent_review",
            "circuit_breaker_review",
            "cache_policy_review",
        ):
            self.assertIn(gate, required)

    def test_hard_no_execution_and_no_mutation_flags_fail(self) -> None:
        for section, field in (
            ("no_execution_guarantees", "worker_runtime_implemented"),
            ("no_execution_guarantees", "job_executed"),
            ("no_execution_guarantees", "live_source_called"),
            ("no_execution_guarantees", "external_calls_performed"),
            ("no_execution_guarantees", "credentials_used"),
            ("no_mutation_guarantees", "source_cache_mutated"),
            ("no_mutation_guarantees", "evidence_ledger_mutated"),
            ("no_mutation_guarantees", "candidate_index_mutated"),
            ("no_mutation_guarantees", "master_index_mutated"),
        ):
            with self.subTest(field=field):
                payload = self._example_payload()
                payload[section][field] = True
                report = self._validate_temp(payload)
                self.assertEqual(report["status"], "invalid")
                self.assertTrue(any(field in error for error in report["errors"]))

    def test_live_network_without_approval_fails(self) -> None:
        payload = self._example_payload()
        payload["job_kind"]["approval_required"] = False
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("approval_required" in error for error in report["errors"]))

    def test_live_network_missing_required_gate_fails(self) -> None:
        payload = self._example_payload()
        payload["approval_gates"] = [gate for gate in payload["approval_gates"] if gate["gate_type"] != "rate_limit_review"]
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("rate_limit_review" in error for error in report["errors"]))

    def test_private_path_job_fails(self) -> None:
        payload = self._example_payload()
        payload["limitations"].append("C:\\Users\\Alice\\private.txt")
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("windows_absolute_path" in error for error in report["errors"]))

    def test_secret_marker_job_fails(self) -> None:
        payload = self._example_payload()
        payload["limitations"].append("api_key should not be here")
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("api_key_marker" in error for error in report["errors"]))

    def test_fake_contact_email_fails(self) -> None:
        payload = self._example_payload()
        payload["user_agent_and_terms"]["notes"].append("contact fake@example.invalid")
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("email_address" in error for error in report["errors"]))

    def test_rights_or_malware_claims_fail(self) -> None:
        for field in ("rights_clearance_claimed", "malware_safety_claimed", "downloads_enabled", "installs_enabled", "execution_enabled"):
            with self.subTest(field=field):
                payload = self._example_payload()
                payload["rights_and_risk"][field] = True
                report = self._validate_temp(payload)
                self.assertEqual(report["status"], "invalid")
                self.assertTrue(any(field in error for error in report["errors"]))

    def _example_payload(self) -> dict:
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def _validate_temp(self, payload: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SOURCE_SYNC_WORKER_JOB.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_source_sync_worker_job.py", "--job", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
