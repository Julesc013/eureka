from __future__ import annotations

from copy import deepcopy
import unittest

from evals.hard_queries.seed_corpus import (
    BASELINE_PROFILES,
    load_seed_corpus,
    project_seed_item,
    seed_items,
)


FORBIDDEN_PUBLIC_ACTIONS = (
    "review_candidate",
    "promote",
    "reject",
    "supersede",
    "request_more_evidence",
    "rebuild_index",
    "freeze_review",
    "download",
    "install",
    "launch_emulator",
    "run_extraction",
    "submit_direct_evidence",
    "crawl_source",
    "arbitrary_live_lookup",
)


class SurfaceSeedCorpusProjectionTests(unittest.TestCase):
    def test_seed_items_project_status_across_baseline_renderers(self) -> None:
        for item in seed_items(load_seed_corpus()):
            for profile in BASELINE_PROFILES:
                with self.subTest(seed_item_id=item["seed_item_id"], profile=profile):
                    result = project_seed_item(item, profile)
                    output = result["renderer_result"]["renderer_output"]

                    self.assertEqual(result["view_model"]["canonical_status"], item["status"])
                    self.assertIn(item["status"], repr(output))
                    self.assertFalse(result["view_model"]["payload"]["fallback_summary"]["verified"])
                    self.assertFalse(result["view_model"]["payload"]["fallback_summary"]["accepted_truth"])
                    self.assertNotEqual(result["view_model"]["canonical_status"], "verified")

    def test_public_projection_strips_operator_actions(self) -> None:
        for item in seed_items(load_seed_corpus()):
            rendered = [project_seed_item(item, profile) for profile in BASELINE_PROFILES]
            combined_output = repr([result["renderer_result"]["renderer_output"] for result in rendered])
            combined_view_model = repr([result["view_model"] for result in rendered])

            for action in FORBIDDEN_PUBLIC_ACTIONS:
                self.assertNotIn(action, combined_output, f"{item['seed_item_id']} rendered {action}")
                self.assertNotIn(action, combined_view_model, f"{item['seed_item_id']} view leaked {action}")
            for result in rendered:
                action_ids = {action["action_id"] for action in result["view_model"]["actions"]}
                self.assertTrue(action_ids.issubset({"view", "inspect_evidence", "compare", "cite", "export_manifest"}))

    def test_policy_blocked_and_unavailable_states_stay_visible(self) -> None:
        items_by_status = {item["status"]: item for item in seed_items(load_seed_corpus())}
        policy_text = project_seed_item(items_by_status["policy_blocked"], "text_v0")["renderer_result"]["renderer_output"]["content"]
        unavailable_text = project_seed_item(items_by_status["unavailable"], "text_v0")["renderer_result"]["renderer_output"]["content"]

        self.assertIn("Status: policy_blocked", policy_text)
        self.assertIn("reviewed_support_window_evidence_missing", policy_text)
        self.assertIn("Status: unavailable", unavailable_text)
        self.assertIn("publication_title_missing", unavailable_text)

    def test_html_renderer_escapes_seed_corpus_text(self) -> None:
        near_miss = next(item for item in seed_items(load_seed_corpus()) if item["status"] == "near_miss")
        html = project_seed_item(near_miss, "html_basic_v0")["renderer_result"]["renderer_output"]["content"]

        self.assertIn("&lt;client&gt;", html)
        self.assertIn("&quot;Blue&quot;", html)
        self.assertNotIn("<client>", html)
        self.assertNotIn('"Blue"', html)

    def test_snapshot_projection_is_deterministic(self) -> None:
        item = seed_items(load_seed_corpus())[0]

        first = project_seed_item(item, "snapshot_v0")["renderer_result"]["renderer_output"]
        second = project_seed_item(item, "snapshot_v0")["renderer_result"]["renderer_output"]

        self.assertEqual(first, second)
        self.assertEqual(first["content"]["canonical_status"], "candidate")

    def test_unknown_status_degrades_honestly(self) -> None:
        item = deepcopy(seed_items(load_seed_corpus())[-1])
        item["status"] = "not_a_known_seed_status"

        for profile in BASELINE_PROFILES:
            with self.subTest(profile=profile):
                result = project_seed_item(item, profile)

                self.assertEqual(result["view_model"]["canonical_status"], "unknown")
                self.assertIn("unknown", repr(result["renderer_result"]["renderer_output"]))

    def test_projection_does_not_call_sources_or_mutate_indexes(self) -> None:
        for item in seed_items(load_seed_corpus()):
            for profile in BASELINE_PROFILES:
                with self.subTest(seed_item_id=item["seed_item_id"], profile=profile):
                    result = project_seed_item(item, profile)
                    renderer = result["renderer_result"]

                    self.assertFalse(result["surface_kernel_called_source_provider"])
                    self.assertFalse(result["surface_kernel_mutated_reviewed_index"])
                    self.assertFalse(result["surface_kernel_mutated_public_index"])
                    self.assertFalse(result["surface_kernel_mutated_master_index"])
                    self.assertFalse(renderer["renderer_called_source_provider"])
                    self.assertFalse(renderer["renderer_created_verified_state"])
                    self.assertFalse(renderer["renderer_mutated_reviewed_index"])
                    self.assertFalse(renderer["renderer_mutated_public_index"])
                    self.assertFalse(renderer["renderer_mutated_master_index"])


if __name__ == "__main__":
    unittest.main()
