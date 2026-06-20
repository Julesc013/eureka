from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path

from runtime.local.synthetic_truth_path import DEFAULT_OUTPUT_ROOT, SyntheticTruthPathOptions, run_synthetic_truth_path, validate_synthetic_truth_path


REPO_ROOT = Path(__file__).resolve().parents[2]


class SyntheticTruthPathE2ETests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = REPO_ROOT / DEFAULT_OUTPUT_ROOT / "e2e-test"
        if self.base.exists():
            shutil.rmtree(self.base)

    def tearDown(self) -> None:
        if self.base.exists():
            shutil.rmtree(self.base)

    def test_complete_scenario_proves_search_change_rollback_and_snapshot(self) -> None:
        result = run_synthetic_truth_path(SyntheticTruthPathOptions(out_root=DEFAULT_OUTPUT_ROOT / "e2e-test"))
        scenario_dir = REPO_ROOT / result["scenario_dir"]
        manifest = _json(scenario_dir / "scenario_manifest.json")
        validation = validate_synthetic_truth_path(scenario_dir, strict=True)
        snapshot = _json(scenario_dir / "snapshot" / "snapshot_verification.json")

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(validation["status"], "pass")
        self.assertEqual(manifest["baseline_search_result"], "candidate")
        self.assertEqual(manifest["reviewed_search_result"], "verified")
        self.assertEqual(manifest["rollback_search_result"], "candidate")
        self.assertTrue(manifest["accepted_synthetic_truth_created"])
        self.assertFalse(manifest["production_truth_created"])
        self.assertFalse(manifest["artifact_verified"])
        self.assertEqual(snapshot["verification_status"], "verified_local")
        self.assertEqual(manifest["snapshot_verification_status"], "verified_local")
        self.assertTrue(manifest["deterministic_rebuild_verified"]["stable_reviewed_record_id"])
        self.assertFalse(manifest["deterministic_rebuild_verified"]["ledger_uuid_fields_deterministic"])

    def test_two_clean_runs_keep_stable_semantic_ids_and_hashes(self) -> None:
        left = run_synthetic_truth_path(SyntheticTruthPathOptions(out_root=DEFAULT_OUTPUT_ROOT / "e2e-test" / "left"))
        right = run_synthetic_truth_path(SyntheticTruthPathOptions(out_root=DEFAULT_OUTPUT_ROOT / "e2e-test" / "right"))
        left_manifest = _json(REPO_ROOT / left["scenario_manifest"])
        right_manifest = _json(REPO_ROOT / right["scenario_manifest"])

        self.assertEqual(left_manifest["candidate_id"], right_manifest["candidate_id"])
        self.assertEqual(left_manifest["review_item_id"], right_manifest["review_item_id"])
        self.assertEqual(left_manifest["reviewed_record_id"], right_manifest["reviewed_record_id"])
        self.assertEqual(left_manifest["index_generation_after"], right_manifest["index_generation_after"])
        self.assertEqual(left_manifest["snapshot_manifest_id"], right_manifest["snapshot_manifest_id"])


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
