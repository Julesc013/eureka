from __future__ import annotations

from pathlib import Path
import unittest

from evals.hard_queries.reviewed_seed_corpus.batch_02 import (
    load_next_validation_pivot,
    load_public_alpha_gate,
    load_validation_summary,
    validate_next_validation_pivot,
)


class ReviewedCorpusBatchTwoValidationPivotTests(unittest.TestCase):
    def test_next_validation_pivot_points_to_source_snapshot_closeout(self) -> None:
        pivot = load_next_validation_pivot()

        self.assertEqual(validate_next_validation_pivot(pivot), ())
        self.assertEqual(pivot["next_primary_task"], "SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01")
        self.assertTrue(pivot["root_structure_frozen"])
        self.assertTrue(pivot["public_alpha_blocked"])
        self.assertTrue(pivot["dev_to_main_blocked"])
        self.assertTrue(pivot["source_snapshot_closeout_needed"])
        self.assertFalse(pivot["public_launch_recommended"])

    def test_validation_summary_declares_external_full_discovery_needed(self) -> None:
        summary = load_validation_summary()

        self.assertEqual(summary["task_id"], "REVIEWED-CORPUS-SEED-BATCH-02")
        self.assertFalse(summary["full_discovery_inside_ai"])
        self.assertTrue(summary["external_full_discovery_needed"])
        self.assertEqual(summary["next_primary_task"], "SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01")
        self.assertEqual(summary["public_alpha_corpus_gate"], "FAIL_INSUFFICIENT_REVIEWED_CORPUS")
        self.assertTrue(summary["validation_commands"])

    def test_docs_handoff_matches_gate_and_pivot(self) -> None:
        gate = load_public_alpha_gate()
        repo_root = Path(__file__).resolve().parents[2]
        handoff = (
            repo_root
            / "docs/planning/public_live_preimplementation/implementation/reviewed_corpus_seed_batch_02/SOURCE_SNAPSHOT_CLOSEOUT_HANDOFF.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(gate["next_primary_task"], "SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01")
        self.assertIn("SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01", handoff)
        self.assertIn("Full unittest discovery must not run inside the AI session", handoff)


if __name__ == "__main__":
    unittest.main()
