import json
import tempfile
import unittest
from pathlib import Path

from scripts import run_candidate_promotion_dry_run, validate_candidate_promotion_dry_run


REPO_ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = REPO_ROOT / "examples/index/candidates/search_need_candidate_v0.json"
REVIEW = REPO_ROOT / "examples/review/queue_entries/candidate_needs_review_v0.json"
READY_INPUT = REPO_ROOT / "examples/review/candidate_promotion_dry_runs/ready_for_promotion_dry_run_v0.json"


class CandidatePromotionDryRunScriptTests(unittest.TestCase):
    def test_script_writes_no_files_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            before = set(Path(tmp).iterdir())
            code = run_candidate_promotion_dry_run.main(["--candidate", str(CANDIDATE), "--review", str(REVIEW), "--check"])
            after = set(Path(tmp).iterdir())
        self.assertEqual(code, 0)
        self.assertEqual(before, after)

    def test_script_writes_explicit_report_to_temp_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "promotion.json"
            summary = Path(tmp) / "promotion.md"
            code = run_candidate_promotion_dry_run.main(
                [
                    "--input",
                    str(READY_INPUT),
                    "--output",
                    str(output),
                    "--summary-output",
                    str(summary),
                    "--check",
                    "--json",
                ]
            )
            self.assertEqual(code, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            summary_text = summary.read_text(encoding="utf-8")
        self.assertEqual(payload["schema_version"], "candidate_promotion_dry_run.v0")
        self.assertEqual(payload["promotion_readiness"], "ready_for_future_reviewed_record_proposal")
        self.assertTrue(summary_text.startswith("# Candidate Promotion Dry-Run Summary"))

    def test_script_refuses_site_dist_output(self) -> None:
        self.assertFalse(run_candidate_promotion_dry_run.output_path_allowed(REPO_ROOT / "site/dist/promotion.json"))

    def test_script_refuses_runtime_output(self) -> None:
        self.assertFalse(run_candidate_promotion_dry_run.output_path_allowed(REPO_ROOT / "runtime/promotion.json"))

    def test_script_refuses_public_and_master_index_output_roots(self) -> None:
        self.assertFalse(run_candidate_promotion_dry_run.output_path_allowed(REPO_ROOT / "public_index/promotion.json"))
        self.assertFalse(run_candidate_promotion_dry_run.output_path_allowed(REPO_ROOT / "master_index/promotion.json"))

    def test_validator_passes_current_repo(self) -> None:
        report = validate_candidate_promotion_dry_run.validate_candidate_promotion_dry_run(REPO_ROOT)
        self.assertEqual(report["status"], "pass", report["errors"])

    def test_product_boundary_true_claim_fails(self) -> None:
        report = run_candidate_promotion_dry_run.build_report(input_path=READY_INPUT)
        record = report["record"]
        record["product_boundary"]["enabled_network_access"] = True
        from runtime.local.foundry import candidate_promotion_dry_run as promotion

        self.assertTrue(promotion.detect_promotion_product_boundary_violations(record))

    def test_runtime_does_not_call_network_model_or_provider(self) -> None:
        runtime_source = (REPO_ROOT / "runtime/local/foundry/candidate_promotion_dry_run.py").read_text(encoding="utf-8")
        script_source = (REPO_ROOT / "scripts/run_candidate_promotion_dry_run.py").read_text(encoding="utf-8")
        for token in ("requests", "urllib", "socket", "openai", "anthropic", "selenium", "playwright"):
            self.assertNotIn(token, runtime_source)
            self.assertNotIn(token, script_source)

    def test_runtime_does_not_mutate_master_index_or_create_private_roots(self) -> None:
        report = run_candidate_promotion_dry_run.build_report(input_path=READY_INPUT)
        self.assertFalse(report["record"]["product_boundary"]["mutated_master_index"])
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
