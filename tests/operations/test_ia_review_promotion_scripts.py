import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class IAReviewPromotionScriptTests(unittest.TestCase):
    def run_cmd(self, args):
        return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)

    def test_review_queue_cli_dry_run_passes_without_mutation(self):
        completed = self.run_cmd(
            [
                sys.executable,
                "scripts/eureka_ia_review_queue.py",
                "--instance",
                "../instances/default",
                "--from-candidate-index",
                "--decision",
                "approve_for_reviewed_index_dry_run",
                "--dry-run",
                "--json",
            ]
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["review_report"]["review_queue_mutated"])
        self.assertTrue(payload["review_report"]["all_review_items_require_review"])

    def test_review_queue_apply_requires_operator_token(self):
        completed = self.run_cmd(
            [
                sys.executable,
                "scripts/eureka_ia_review_queue.py",
                "--instance",
                "../instances/default",
                "--from-candidate-index",
                "--apply",
                "--json",
            ]
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("--operator-token is required", completed.stderr)

    def test_review_queue_apply_requires_explicit_apply(self):
        completed = self.run_cmd(
            [
                sys.executable,
                "scripts/eureka_ia_review_queue.py",
                "--instance",
                "../instances/default",
                "--from-candidate-index",
                "--json",
            ]
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["review_report"]["review_queue_mutated"])

    def test_apply_and_promotion_write_to_temp_instance_preview_only(self):
        with tempfile.TemporaryDirectory(prefix="eureka-ia06-test-") as tmp:
            instance = Path(tmp) / "instance"
            review_report = Path(tmp) / "review.json"
            self.assertEqual(0, self.run_cmd([sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"]).returncode)
            self.assertEqual(
                0,
                self.run_cmd(
                    [
                        sys.executable,
                        "scripts/eureka_set_operator_token.py",
                        "--instance",
                        str(instance),
                        "--token",
                        "local-dev-token",
                        "--json",
                    ]
                ).returncode,
            )
            self.assertEqual(
                0,
                self.run_cmd(
                    [
                        sys.executable,
                        "scripts/eureka_ia_candidate_index_write.py",
                        "--instance",
                        str(instance),
                        "--operator-token",
                        "local-dev-token",
                        "--from-evidence-ledger",
                        "--apply",
                        "--json",
                    ]
                ).returncode,
            )
            completed = self.run_cmd(
                [
                    sys.executable,
                    "scripts/eureka_ia_review_queue.py",
                    "--instance",
                    str(instance),
                    "--operator-token",
                    "local-dev-token",
                    "--from-candidate-index",
                    "--decision",
                    "approve_for_reviewed_index_dry_run",
                    "--apply",
                    "--json",
                    "--output",
                    str(review_report),
                ]
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["review_report"]["review_queue_mutated"])
            promotion = self.run_cmd(
                [
                    sys.executable,
                    "scripts/eureka_ia_promotion_dry_run.py",
                    "--instance",
                    str(instance),
                    "--operator-token",
                    "local-dev-token",
                    "--from-review-decisions",
                    "--from-review-report",
                    str(review_report),
                    "--json",
                ]
            )
            self.assertEqual(0, promotion.returncode, promotion.stderr)
            promotion_payload = json.loads(promotion.stdout)
            self.assertTrue(promotion_payload["promotion_report"]["promotion_previews_created"])
            self.assertFalse(promotion_payload["promotion_report"]["reviewed_index_mutated"])
            self.assertFalse(promotion_payload["promotion_report"]["master_index_mutated"])

    def test_validator_passes(self):
        completed = self.run_cmd([sys.executable, "scripts/validate_ia_review_promotion_dry_run.py"])
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
