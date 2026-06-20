from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path

from runtime.local.synthetic_truth_path import (
    DEFAULT_OUTPUT_ROOT,
    NAMESPACE,
    SyntheticTruthPathError,
    SyntheticTruthPathOptions,
    materialize_synthetic_reviewed_record,
    rollback_synthetic_truth_path,
    run_synthetic_truth_path,
    validate_synthetic_truth_path,
)
from runtime.review.queue import ReviewQueueStore


REPO_ROOT = Path(__file__).resolve().parents[2]


class SyntheticTruthMaterializationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = REPO_ROOT / DEFAULT_OUTPUT_ROOT / "runtime-test"
        if self.root.exists():
            shutil.rmtree(self.root)

    def tearDown(self) -> None:
        if self.root.exists():
            shutil.rmtree(self.root)

    def test_happy_path_materializes_synthetic_record_and_preserves_ledger(self) -> None:
        result = run_synthetic_truth_path(SyntheticTruthPathOptions(out_root=DEFAULT_OUTPUT_ROOT / "runtime-test"))
        scenario_dir = REPO_ROOT / result["scenario_dir"]
        manifest = _json(scenario_dir / "scenario_manifest.json")
        reviewed = _jsonl(scenario_dir / "truth" / "generations" / manifest["truth_generation_after"] / "reviewed_records.jsonl")[0]
        search_before = _json(scenario_dir / "index" / "search_before.json")
        search_after = _json(scenario_dir / "index" / "search_after.json")
        search_rollback = _json(scenario_dir / "index" / "search_rollback.json")

        self.assertEqual(result["status"], "PASS")
        self.assertTrue(reviewed["synthetic"])
        self.assertEqual(reviewed["namespace"], NAMESPACE)
        self.assertEqual(reviewed["truth_scope"], "synthetic_test_only")
        self.assertTrue(reviewed["accepted_truth"])
        self.assertFalse(reviewed["artifact_verified"])
        self.assertEqual(search_before["results"][0]["status"], "candidate")
        self.assertEqual(search_after["results"][0]["status"], "verified")
        self.assertEqual(search_after["results"][0]["truth_scope"], "synthetic_test_only")
        self.assertEqual(search_rollback["results"][0]["status"], "candidate")

        with ReviewQueueStore.open(scenario_dir / "review" / "review_queue.sqlite") as store:
            self.assertEqual(len(store.list_decisions(limit=10)), 1)
            self.assertGreaterEqual(len(store.list_events(limit=20)), 4)

    def test_materializer_rejects_non_synthetic_or_wrong_namespace(self) -> None:
        result = run_synthetic_truth_path(SyntheticTruthPathOptions(out_root=DEFAULT_OUTPUT_ROOT / "runtime-test"))
        scenario_dir = REPO_ROOT / result["scenario_dir"]
        candidate = _json(scenario_dir / "input" / "candidate.json")
        review_item = _json(scenario_dir / "input" / "review_item.json")
        decision = _json(scenario_dir / "review" / "decision_result.json")

        bad_candidate = dict(candidate, synthetic=False)
        with self.assertRaises(SyntheticTruthPathError):
            materialize_synthetic_reviewed_record(
                candidate=bad_candidate,
                review_item=review_item,
                decision_result=decision,
                output_root=scenario_dir / "truth",
            )

        bad_item = dict(review_item, namespace="synthetic:other")
        with self.assertRaises(SyntheticTruthPathError):
            materialize_synthetic_reviewed_record(
                candidate=candidate,
                review_item=bad_item,
                decision_result=decision,
                output_root=scenario_dir / "truth",
            )

    def test_materializer_rejects_missing_confirmation_and_outside_output(self) -> None:
        result = run_synthetic_truth_path(SyntheticTruthPathOptions(out_root=DEFAULT_OUTPUT_ROOT / "runtime-test"))
        scenario_dir = REPO_ROOT / result["scenario_dir"]
        candidate = _json(scenario_dir / "input" / "candidate.json")
        review_item = _json(scenario_dir / "input" / "review_item.json")
        decision = _json(scenario_dir / "review" / "decision_result.json")
        decision["review_event"]["event_payload"]["local_only_confirmed"] = False

        with self.assertRaises(SyntheticTruthPathError):
            materialize_synthetic_reviewed_record(
                candidate=candidate,
                review_item=review_item,
                decision_result=decision,
                output_root=scenario_dir / "truth",
            )

        decision["review_event"]["event_payload"]["local_only_confirmed"] = True
        with self.assertRaises(SyntheticTruthPathError):
            materialize_synthetic_reviewed_record(
                candidate=candidate,
                review_item=review_item,
                decision_result=decision,
                output_root=REPO_ROOT / "control" / "audits",
            )

    def test_boundary_validator_rejects_artifact_verified_and_real_source_family(self) -> None:
        result = run_synthetic_truth_path(SyntheticTruthPathOptions(out_root=DEFAULT_OUTPUT_ROOT / "runtime-test"))
        scenario_dir = REPO_ROOT / result["scenario_dir"]
        candidate_path = scenario_dir / "input" / "candidate.json"
        candidate = _json(candidate_path)
        candidate["artifact_verified"] = True
        candidate_path.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        validation = validate_synthetic_truth_path(scenario_dir, strict=True)
        self.assertEqual(validation["status"], "fail")
        self.assertTrue(any("artifact_verified" in error for error in validation["errors"]))

        observation_path = scenario_dir / "input" / "source_observation.json"
        observation = _json(observation_path)
        observation["source_family"] = "internet_archive"
        observation_path.write_text(json.dumps(observation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        validation = validate_synthetic_truth_path(scenario_dir, strict=True)
        self.assertTrue(any("forbidden real IA" in error for error in validation["errors"]))

    def test_corrupt_baseline_index_cannot_be_activated_for_rollback(self) -> None:
        result = run_synthetic_truth_path(SyntheticTruthPathOptions(out_root=DEFAULT_OUTPUT_ROOT / "runtime-test"))
        scenario_dir = REPO_ROOT / result["scenario_dir"]
        index_path = scenario_dir / "index" / "generations" / "index-generation.baseline.v0" / "index.json"
        index = _json(index_path)
        index["documents"][0]["id"] = ""
        index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        with self.assertRaises(SyntheticTruthPathError):
            rollback_synthetic_truth_path(scenario_dir)


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    unittest.main()
