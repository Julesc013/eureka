import json
import tempfile
import unittest
from pathlib import Path

from scripts import record_review_queue, summarize_review_queue, validate_local_review_queue_runtime


REPO_ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_REVIEW = REPO_ROOT / "examples/review/queue_entries/candidate_needs_review_v0.json"


class LocalReviewQueueRuntimeScriptTests(unittest.TestCase):
    def test_record_script_writes_no_files_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            before = set(Path(tmp).iterdir())
            code = record_review_queue.main(["--input", str(CANDIDATE_REVIEW), "--check"])
            after = set(Path(tmp).iterdir())
        self.assertEqual(code, 0)
        self.assertEqual(before, after)

    def test_record_script_writes_explicit_report_to_temp_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "review_entry.json"
            summary = Path(tmp) / "review_summary.md"
            code = record_review_queue.main(
                [
                    "--input",
                    str(CANDIDATE_REVIEW),
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
        self.assertEqual(payload["schema_version"], "local_review_queue_entry.v0")
        self.assertEqual(payload["review_subject_type"], "candidate_record")
        self.assertTrue(summary_text.startswith("# Review Queue Entry"))

    def test_record_script_refuses_site_dist_output(self) -> None:
        self.assertFalse(record_review_queue.output_path_allowed(REPO_ROOT / "site/dist/review.json"))

    def test_record_script_refuses_runtime_output(self) -> None:
        self.assertFalse(record_review_queue.output_path_allowed(REPO_ROOT / "runtime/review.json"))

    def test_summarizer_works_on_examples(self) -> None:
        code = summarize_review_queue.main(["--input", str(REPO_ROOT / "examples/review/queue_entries"), "--check"])
        self.assertEqual(code, 0)

    def test_summarizer_writes_explicit_report_to_temp_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "review_snapshot.json"
            summary = Path(tmp) / "review_summary.md"
            code = summarize_review_queue.main(
                [
                    "--input",
                    str(REPO_ROOT / "examples/review/queue_entries"),
                    "--output",
                    str(output),
                    "--summary-output",
                    str(summary),
                    "--check",
                ]
            )
            self.assertEqual(code, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            summary_text = summary.read_text(encoding="utf-8")
        self.assertEqual(payload["summary"]["review_entry_count"], 10)
        self.assertTrue(summary_text.startswith("# Review Queue Summary"))

    def test_validator_passes_current_repo(self) -> None:
        report = validate_local_review_queue_runtime.validate_local_review_queue_runtime(REPO_ROOT)
        self.assertEqual(report["status"], "pass", report["errors"])

    def test_product_boundary_true_claim_fails(self) -> None:
        report = record_review_queue.build_report(CANDIDATE_REVIEW)
        entry = report["entry"]
        entry["product_boundary"]["enabled_telemetry"] = True
        from runtime.local.foundry import review_queue

        self.assertTrue(review_queue.detect_review_product_boundary_violations(entry))

    def test_runtime_does_not_call_network_model_or_provider(self) -> None:
        runtime_source = (REPO_ROOT / "runtime/local/foundry/review_queue.py").read_text(encoding="utf-8")
        scripts = (
            (REPO_ROOT / "scripts/record_review_queue.py").read_text(encoding="utf-8")
            + (REPO_ROOT / "scripts/summarize_review_queue.py").read_text(encoding="utf-8")
        )
        for token in ("requests", "urllib", "socket", "openai", "anthropic", "selenium", "playwright"):
            self.assertNotIn(token, runtime_source)
            self.assertNotIn(token, scripts)

    def test_runtime_does_not_mutate_master_index_or_create_private_roots(self) -> None:
        report = record_review_queue.build_report(CANDIDATE_REVIEW)
        self.assertFalse(report["entry"]["product_boundary"]["mutated_master_index"])
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
