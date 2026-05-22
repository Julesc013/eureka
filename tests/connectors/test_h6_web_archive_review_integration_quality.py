"""Tests for H6 web archive/news/event review integration quality helpers."""

from __future__ import annotations

from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.quality_delta import build_h6_quality_delta, detect_h6_quality_overclaim
from archive.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.review_integration import (
    build_h6_review_integration_result,
    detect_h6_review_product_boundary_violations,
    detect_h6_review_truth_boundary_violations,
    load_h6_web_archive_outputs,
)
from archive.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.wave_postmortem import build_h6_connector_wave_postmortem, build_h6_next_phase_recommendation

ROOT = Path(__file__).resolve().parents[2]


class H6ReviewIntegrationQualityTests(unittest.TestCase):
    def _review(self, include_live: bool = False):
        paths = sorted((ROOT / "examples/connectors/h6_web_archive_news_event/replay_results").glob("*.json"))
        if include_live:
            paths += sorted((ROOT / "examples/connectors/h6_web_archive_news_event/live_probe_results").glob("*.json"))
        outputs = load_h6_web_archive_outputs(paths)
        return build_h6_review_integration_result({"outputs": outputs, "input_refs": [str(p) for p in paths]})

    def test_review_integration_builds_seeds_from_fixture_outputs(self):
        review = self._review()
        self.assertEqual(13, len(review["sources"]))
        self.assertEqual(13, len(review["web_capture_identity_review_seeds"]))
        self.assertEqual(13, len(review["archived_url_time_state_review_seeds"]))
        self.assertEqual(13, len(review["news_event_mention_review_seeds"]))
        self.assertEqual(13, len(review["dead_link_trace_review_seeds"]))
        self.assertEqual(13, len(review["public_document_trace_review_seeds"]))
        self.assertEqual(13, len(review["media_transcript_metadata_review_seeds"]))
        self.assertEqual(13, len(review["source_cache_review_seeds"]))
        self.assertEqual(13, len(review["evidence_candidate_review_seeds"]))
        self.assertFalse(review["accepts_web_capture_truth"])
        self.assertFalse(review["enables_warc_wacz_fetch"])

    def test_review_integration_builds_seeds_from_mocked_live_probe_outputs(self):
        review = self._review(include_live=True)
        self.assertEqual(13, len(review["blocked_sources"]))
        self.assertFalse(review["product_boundary"]["enabled_scraping_crawling"])
        self.assertFalse(review["truth_boundary"]["web_capture_seed_accepts_capture_truth"])

    def test_review_seeds_and_previews_do_not_accept_truth(self):
        review = self._review(include_live=True)
        self.assertEqual([], detect_h6_review_truth_boundary_violations(review))
        self.assertEqual([], detect_h6_review_product_boundary_violations(review))
        self.assertFalse(review["web_capture_identity_review_seeds"][0]["accepted_web_capture_truth"])
        self.assertFalse(review["archived_url_time_state_review_seeds"][0]["accepted_archived_time_state_truth"])
        self.assertFalse(review["news_event_mention_review_seeds"][0]["accepted_event_truth"])
        self.assertFalse(review["dead_link_trace_review_seeds"][0]["dead_link_seed_grants_acquisition_permission"])
        self.assertFalse(review["public_document_trace_review_seeds"][0]["public_document_fetch_permission"])
        self.assertFalse(review["media_transcript_metadata_review_seeds"][0]["media_transcript_seed_accepts_full_context_truth"])
        self.assertFalse(review["source_cache_review_seeds"][0]["accepted_source_truth"])
        self.assertFalse(review["evidence_candidate_review_seeds"][0]["accepted_evidence_truth"])
        self.assertFalse(review["candidate_promotion_previews"][0]["candidate_promotion_preview_promotes_candidate"])
        self.assertFalse(review["source_pack_update_previews"][0]["source_pack_preview_is_imported_or_submitted"])

    def test_quality_delta_and_postmortem_boundaries(self):
        review = self._review(include_live=True)
        delta = build_h6_quality_delta({"review_integration_result": review})
        self.assertEqual(13, delta["source_count"])
        self.assertEqual(13, delta["blocked_sources_count"])
        self.assertEqual([], detect_h6_quality_overclaim(delta))
        postmortem = build_h6_connector_wave_postmortem(review, delta)
        self.assertFalse(postmortem["auto_approves_future_connectors"])
        recommendation = build_h6_next_phase_recommendation(postmortem)
        self.assertEqual("READY_FOR_H7_BUNDLE_01", recommendation["recommendation_status"])

    def test_forbidden_claims_are_rejected(self):
        review = self._review()
        review["public_index_mutated"] = True
        self.assertTrue(detect_h6_review_truth_boundary_violations(review))
        review["public_index_mutated"] = False
        review["product_boundary"]["enabled_fetching"] = True
        self.assertTrue(detect_h6_review_product_boundary_violations(review))
        delta = build_h6_quality_delta({"review_integration_result": self._review()})
        delta["truth_boundary"]["event_truth_verified"] = True
        self.assertTrue(detect_h6_quality_overclaim(delta))


if __name__ == "__main__":
    unittest.main()
