from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_ROOT = REPO_ROOT / "evals" / "search_usefulness" / "external_baselines"
BATCH_ROOT = BASELINE_ROOT / "batches" / "batch_0"
QUERY_PACK = REPO_ROOT / "evals" / "search_usefulness" / "queries" / "search_usefulness_v0.json"
SYSTEMS_PATH = BASELINE_ROOT / "systems.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class ManualObservationBatchZeroTest(unittest.TestCase):
    def test_batch_zero_required_files_exist(self) -> None:
        for relative_path in (
            "README.md",
            "batch_manifest.json",
            "observation_instructions.md",
            "observation_checklist.md",
            "observation_template.batch_0.json",
            "observations/README.md",
            "observations/pending_batch_0_observations.json",
            "reports/README.md",
        ):
            self.assertTrue((BATCH_ROOT / relative_path).exists(), relative_path)

    def test_manifest_selects_existing_queries_and_systems(self) -> None:
        manifest = _load(BATCH_ROOT / "batch_manifest.json")
        query_ids = {query["id"] for query in _load(QUERY_PACK)["queries"]}
        system_ids = {system["system_id"] for system in _load(SYSTEMS_PATH)["systems"]}

        self.assertEqual(manifest["batch_id"], "batch_0")
        self.assertEqual(manifest["status"], "pending_manual_observation")
        self.assertGreaterEqual(len(manifest["selected_query_ids"]), 10)
        self.assertLessEqual(len(manifest["selected_query_ids"]), 15)
        self.assertTrue(set(manifest["selected_query_ids"]).issubset(query_ids))
        self.assertEqual(
            set(manifest["selected_system_ids"]),
            {
                "google_web_search",
                "internet_archive_metadata_search",
                "internet_archive_full_text_search",
            },
        )
        self.assertTrue(set(manifest["selected_system_ids"]).issubset(system_ids))
        self.assertEqual(
            manifest["expected_observation_count"],
            len(manifest["selected_query_ids"]) * len(manifest["selected_system_ids"]),
        )

    def test_pending_batch_observations_are_pending_only(self) -> None:
        manifest = _load(BATCH_ROOT / "batch_manifest.json")
        payload = _load(BATCH_ROOT / "observations" / "pending_batch_0_observations.json")
        observations = payload["observations"]

        self.assertEqual(payload["observation_status"], "pending_manual_observation")
        self.assertEqual(len(observations), manifest["expected_observation_count"])
        self.assertEqual({record["query_id"] for record in observations}, set(manifest["selected_query_ids"]))
        self.assertEqual({record["system_id"] for record in observations}, set(manifest["selected_system_ids"]))

        seen_slots = set()
        for record in observations:
            with self.subTest(observation_id=record["observation_id"]):
                slot = (record["query_id"], record["system_id"])
                self.assertNotIn(slot, seen_slots)
                seen_slots.add(slot)
                self.assertEqual(record["observation_status"], "pending_manual_observation")
                self.assertEqual(record["top_results"], [])
                self.assertIsNone(record["first_useful_result_rank"])
                self.assertIsNone(record["usefulness_scores"])
                self.assertIsNone(record["operator"])
                self.assertIsNone(record["observed_at"])
                self.assertIsNone(record["exact_query_submitted"])

    def test_batch_template_is_not_observed(self) -> None:
        template = _load(BATCH_ROOT / "observation_template.batch_0.json")
        serialized = json.dumps(template, sort_keys=True)

        self.assertEqual(template["observation_status"], "pending_manual_observation")
        self.assertTrue(template["top_results"])
        self.assertTrue(template["top_results"][0]["title"].startswith("<"))
        self.assertTrue(template["top_results"][0]["url_or_locator"].startswith("<"))
        self.assertIsNone(template["first_useful_result_rank"])
        self.assertIn("<operator>", serialized)
        self.assertIn("<manual observation date>", serialized)
        self.assertIn("<paste manually observed title>", serialized)
        self.assertNotEqual(template["observation_status"], "observed")

    def test_batch_docs_prohibit_scraping_fabrication_and_global_truth(self) -> None:
        combined = "\n".join(
            (BATCH_ROOT / name).read_text(encoding="utf-8").lower()
            for name in (
                "README.md",
                "observation_instructions.md",
                "observation_checklist.md",
            )
        )

        self.assertIn("do not scrape", combined)
        self.assertIn("do not automate", combined)
        self.assertIn("no fabricated", combined)
        self.assertIn("global", combined)
        self.assertIn("pending_manual_observation", combined)


if __name__ == "__main__":
    unittest.main()
