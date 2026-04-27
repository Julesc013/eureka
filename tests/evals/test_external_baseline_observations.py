from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_ROOT = REPO_ROOT / "evals" / "search_usefulness" / "external_baselines"
QUERY_PACK = REPO_ROOT / "evals" / "search_usefulness" / "queries" / "search_usefulness_v0.json"
PENDING_MANIFEST = BASELINE_ROOT / "observations" / "pending_observations.json"
SYSTEM_IDS = {
    "google_web_search",
    "internet_archive_metadata_search",
    "internet_archive_full_text_search",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class ExternalBaselineObservationPackTest(unittest.TestCase):
    def test_required_files_parse(self) -> None:
        for relative_path in (
            "README.md",
            "systems.json",
            "observation.schema.json",
            "observation_template.json",
            "instructions/google.md",
            "instructions/internet_archive_metadata.md",
            "instructions/internet_archive_full_text.md",
            "observations/README.md",
            "reports/README.md",
        ):
            self.assertTrue((BASELINE_ROOT / relative_path).exists(), relative_path)

        self.assertEqual(set(item["system_id"] for item in _load(BASELINE_ROOT / "systems.json")["systems"]), SYSTEM_IDS)
        self.assertEqual(
            _load(BASELINE_ROOT / "observation_template.json")["observation_status"],
            "pending_manual_observation",
        )

    def test_systems_are_manual_only(self) -> None:
        systems = _load(BASELINE_ROOT / "systems.json")["systems"]

        for system in systems:
            self.assertEqual(system["observation_mode"], "manual_only")
            self.assertFalse(system["scraping_allowed"])
            self.assertFalse(system["automated_querying_allowed"])
            self.assertFalse(system["live_api_allowed"])

    def test_schema_uses_bounded_score_scale(self) -> None:
        schema = _load(BASELINE_ROOT / "observation.schema.json")
        score_properties = schema["properties"]["usefulness_scores"]["properties"]

        for field in (
            "object_type_fit",
            "smallest_actionable_unit",
            "evidence_quality",
            "compatibility_clarity",
            "actionability",
            "absence_explanation",
            "duplicate_handling",
            "user_cost_reduction",
            "overall",
        ):
            self.assertEqual(score_properties[field]["minimum"], 0)
            self.assertEqual(score_properties[field]["maximum"], 3)

    def test_pending_manifest_covers_all_queries_and_systems(self) -> None:
        query_pack = _load(QUERY_PACK)
        query_ids = sorted(query["id"] for query in query_pack["queries"])
        manifest = _load(PENDING_MANIFEST)

        self.assertEqual(manifest["observation_status"], "pending_manual_observation")
        self.assertEqual(sorted(manifest["query_ids"]), query_ids)
        self.assertEqual(set(manifest["required_system_ids"]), SYSTEM_IDS)
        self.assertEqual(len(manifest["query_ids"]), 64)
        self.assertEqual(len(manifest["query_ids"]) * len(manifest["required_system_ids"]), 192)
        self.assertNotIn("top_results", manifest)

    def test_template_is_not_observed_evidence(self) -> None:
        template = _load(BASELINE_ROOT / "observation_template.json")

        self.assertEqual(template["observation_status"], "pending_manual_observation")
        self.assertEqual(template["top_results"], [])
        self.assertEqual(template["first_useful_result_rank"], None)
        self.assertIn("<manual observation required>", json.dumps(template))

    def test_instructions_prohibit_automation_and_global_truth_claims(self) -> None:
        combined = "\n".join(
            (BASELINE_ROOT / "instructions" / name).read_text(encoding="utf-8").lower()
            for name in (
                "google.md",
                "internet_archive_metadata.md",
                "internet_archive_full_text.md",
            )
        )

        self.assertIn("manual only", combined)
        self.assertIn("do not scrape", combined)
        self.assertIn("do not", combined)
        self.assertIn("automate", combined)
        self.assertIn("not", combined)
        self.assertIn("global", combined)


if __name__ == "__main__":
    unittest.main()
