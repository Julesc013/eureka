from __future__ import annotations

import json
from pathlib import Path
import unittest

from tools.validators.validate_test_run_summary import validate_summary_path


REPO_ROOT = Path(__file__).resolve().parents[2]


class CiFullDiscoveryHarnessPolicyTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        required = [
            "contracts/testing/full_unittest_summary.v0.json",
            "contracts/testing/failure_family.v0.json",
            "contracts/testing/external_full_discovery_handoff.v0.json",
            "contracts/testing/test_run_artifact_manifest.v0.json",
            "scripts/run_full_unittest_discovery.py",
            "scripts/summarize_unittest_log.py",
            "scripts/validate_test_run_summary.py",
            "scripts/run_failed_tests.py",
            ".github/workflows/quick-lanes.yml",
            ".github/workflows/full-discovery.yml",
            ".github/workflows/promotion-gate.yml",
            "docs/operations/FULL_DISCOVERY_CI_RUNBOOK.md",
            "docs/operations/AI_TEST_TOKEN_DISCIPLINE.md",
            ".aide/policies/long_test_token_discipline.md",
            ".aide/policies/test_execution_policy.md",
            "control/inventory/ci_full_discovery_harness_result.json",
            "control/audits/ci-full-discovery-harness-00-v0/generated/sample_full_unittest_summary.json",
        ]
        missing = [path for path in required if not (REPO_ROOT / path).is_file()]
        self.assertEqual([], missing)

    def test_policy_names_waiting_status_and_external_handoff(self) -> None:
        text = "\n".join(
            (REPO_ROOT / path).read_text(encoding="utf-8")
            for path in [
                "AGENTS.md",
                "docs/operations/AI_TEST_TOKEN_DISCIPLINE.md",
                ".aide/policies/long_test_token_discipline.md",
                ".aide/queue/SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01/task.yaml",
            ]
        )
        self.assertIn("WAITING_FOR_EXTERNAL_FULL_DISCOVERY", text)
        self.assertIn("full_unittest_summary.json", text)
        self.assertIn("external_full_discovery_handoff", text)

    def test_workflows_upload_artifacts_without_secrets(self) -> None:
        for rel in [
            ".github/workflows/quick-lanes.yml",
            ".github/workflows/full-discovery.yml",
            ".github/workflows/promotion-gate.yml",
        ]:
            text = (REPO_ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("actions/upload-artifact", text)
            self.assertIn("contents: read", text)
            self.assertNotIn("secrets.", text)

    def test_sample_summary_validates(self) -> None:
        result = validate_summary_path(
            REPO_ROOT
            / "control/audits/ci-full-discovery-harness-00-v0/generated/sample_full_unittest_summary.json"
        )
        self.assertEqual(result["status"], "pass", result["errors"])

    def test_result_records_boundaries(self) -> None:
        payload = json.loads((REPO_ROOT / "control/inventory/ci_full_discovery_harness_result.json").read_text(encoding="utf-8"))
        self.assertFalse(payload["full_discovery_run_inside_ai"])
        self.assertFalse(payload["raw_logs_committed"])
        self.assertFalse(payload["production_readiness_claimed"])
        self.assertFalse(payload["public_launch_readiness_claimed"])


if __name__ == "__main__":
    unittest.main()
