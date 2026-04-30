from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "search-usefulness-source-expansion-v2"
REPORT = AUDIT_DIR / "source_expansion_v2_report.json"


class SearchUsefulnessSourceExpansionV2AuditTestCase(unittest.TestCase):
    def test_audit_pack_records_fixture_only_delta(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "implemented_fixture_only")
        self.assertEqual(payload["mode"], "local_index_only")
        self.assertEqual(payload["baseline_counts"]["source_gap"], 26)
        self.assertEqual(payload["final_counts"]["source_gap"], 10)
        self.assertEqual(payload["delta"]["partial"], 18)
        self.assertEqual(len(payload["selected_query_targets"]), 15)
        self.assertEqual(payload["archive_resolution_eval_status_counts"], {"satisfied": 6})

    def test_external_baselines_and_forbidden_behaviors_remain_disabled(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))

        external = payload["external_baseline_status"]
        self.assertFalse(external["automated_external_calls_performed"])
        self.assertFalse(external["external_observations_added"])
        self.assertEqual(external["pending_manual_observation_counts"]["google"], 64)

        for flag, value in payload["forbidden_behaviors_preserved"].items():
            with self.subTest(flag=flag):
                self.assertFalse(value)

    def test_required_audit_files_exist(self) -> None:
        required = {
            "README.md",
            "BASELINE_AUDIT_COUNTS.md",
            "SELECTED_QUERY_TARGETS.md",
            "SOURCE_FAMILY_SELECTION.md",
            "FIXTURE_INVENTORY.md",
            "NORMALIZATION_AND_INDEXING_NOTES.md",
            "QUERY_IMPACT_MATRIX.md",
            "FINAL_AUDIT_COUNTS.md",
            "REMAINING_GAPS.md",
            "RISKS_AND_LIMITATIONS.md",
            "NEXT_SOURCE_WORK.md",
            "source_expansion_v2_report.json",
        }

        self.assertEqual(
            required,
            {path.name for path in AUDIT_DIR.iterdir() if path.is_file()},
        )


if __name__ == "__main__":
    unittest.main()
