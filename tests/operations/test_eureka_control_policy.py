from __future__ import annotations

from pathlib import Path
import unittest

from scripts.validate_eureka_control_policy import (
    DOC_FILES,
    POLICY_FILES,
    validate_commit_message,
    validate_control_policy,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class EurekaControlPolicyTest(unittest.TestCase):
    def test_required_policy_files_exist(self) -> None:
        for path in POLICY_FILES.values():
            self.assertTrue((REPO_ROOT / path).is_file(), path)

    def test_required_docs_exist(self) -> None:
        for path in DOC_FILES:
            self.assertTrue((REPO_ROOT / path).is_file(), path)

    def test_validator_passes_on_current_repo(self) -> None:
        report = validate_control_policy(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_valid_structured_sample_commit_passes(self) -> None:
        message = (REPO_ROOT / "examples/commit_messages/valid_structured_commit.txt").read_text(encoding="utf-8")

        self.assertEqual(validate_commit_message(message), [])

    def test_missing_why_fails(self) -> None:
        message = (REPO_ROOT / "examples/commit_messages/invalid_missing_why.txt").read_text(encoding="utf-8")

        self.assertIn("missing required heading ## Why", validate_commit_message(message))

    def test_missing_validation_fails(self) -> None:
        message = (REPO_ROOT / "examples/commit_messages/valid_structured_commit.txt").read_text(encoding="utf-8")
        message = message.replace("## Validation", "## Checks")

        self.assertIn("missing required heading ## Validation", validate_commit_message(message))

    def test_missing_required_trailer_fails(self) -> None:
        message = (REPO_ROOT / "examples/commit_messages/valid_structured_commit.txt").read_text(encoding="utf-8")
        message = message.replace("AIDE-Task: EUREKA-CTRL-01\n", "")

        self.assertIn("missing required trailer AIDE-Task", validate_commit_message(message))

    def test_invalid_subject_line_fails(self) -> None:
        message = (REPO_ROOT / "examples/commit_messages/valid_structured_commit.txt").read_text(encoding="utf-8")
        message = message.replace("docs(control): add recovery policy preview", "Update docs")

        self.assertIn("invalid subject line", validate_commit_message(message))

    def test_workunit_policy_contains_duplicate_out_of_order_partial_handling(self) -> None:
        text = (REPO_ROOT / ".aide/policies/workunit-recovery-policy.yaml").read_text(encoding="utf-8")

        self.assertIn("duplicate", text)
        self.assertIn("out_of_order_task", text)
        self.assertIn("if_partial", text)

    def test_documentation_policy_contains_stale_claim_and_no_bloat_checks(self) -> None:
        text = (REPO_ROOT / ".aide/policies/documentation-quality-policy.yaml").read_text(encoding="utf-8")

        self.assertIn("avoid copying full chat history", text)
        self.assertIn("hosted backend active", text)

    def test_source_comment_policy_contains_why_first_language(self) -> None:
        text = (REPO_ROOT / ".aide/policies/source-comment-policy.yaml").read_text(encoding="utf-8").lower()

        self.assertIn("why", text)
        self.assertIn("failure modes", text)
        self.assertIn("hard_fail_existing_code", text)


if __name__ == "__main__":
    unittest.main()
