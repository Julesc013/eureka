from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "search-usefulness-delta-v2"
REPORT = AUDIT_DIR / "delta_report.json"


class SearchUsefulnessDeltaV2AuditTestCase(unittest.TestCase):
    def test_audit_pack_records_counts_and_delta(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "implemented_audit_only")
        self.assertEqual(payload["baseline_counts"]["partial"], 22)
        self.assertEqual(payload["current_counts"]["partial"], 40)
        self.assertEqual(payload["status_deltas"]["partial"], 18)
        self.assertEqual(payload["status_deltas"]["source_gap"], -16)
        self.assertEqual(payload["next_recommended_milestone"], "Source Pack Contract v0")

    def test_query_movements_and_source_family_impact_are_present(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))

        movements = payload["query_movements"]
        self.assertEqual(len(movements), 15)
        self.assertTrue(all(item["current_status"] == "partial" for item in movements))
        self.assertIn(
            "wayback_memento_recorded",
            {item["source_family"] for item in movements},
        )
        self.assertEqual(len(payload["source_family_impacts"]), 6)

    def test_external_baselines_remain_pending_manual(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        external = payload["external_baseline_status"]

        self.assertFalse(external["automated_external_calls_performed"])
        self.assertFalse(external["external_observations_added"])
        self.assertEqual(external["global_slot_counts"]["observed"], 0)
        self.assertEqual(external["global_slot_counts"]["pending_manual_observation"], 192)
        self.assertEqual(external["batch_0"]["observed_observation_count"], 0)

    def test_hard_eval_and_public_search_status_are_recorded(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))

        self.assertEqual(payload["hard_eval_status"]["archive_resolution_eval_status_counts"], {"satisfied": 6})
        self.assertFalse(payload["hard_eval_status"]["regressions_found"])
        self.assertEqual(payload["public_search_status"]["smoke_status"], "passed")
        self.assertEqual(payload["public_search_status"]["mode"], "local_index_only")
        self.assertFalse(payload["public_search_status"]["live_probes_enabled"])

    def test_no_unsupported_superiority_or_production_claims(self) -> None:
        joined = "\n".join(path.read_text(encoding="utf-8").casefold() for path in AUDIT_DIR.iterdir() if path.is_file())

        self.assertNotIn("beats google", joined)
        self.assertNotIn("production search relevance", joined)
        self.assertNotIn("production-ready", joined)


if __name__ == "__main__":
    unittest.main()
