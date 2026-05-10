from __future__ import annotations

import copy
import unittest

from runtime.connectors.h6_web_archive_news_event.dead_link_trace import build_h6_dead_link_trace_candidates
from runtime.connectors.h6_web_archive_news_event.news_event_mention import build_h6_news_event_mention_candidates
from runtime.connectors.h6_web_archive_news_event.normalizer_common import detect_h6_truth_boundary_violations


class H6NewsEventDeadLinkMappingTests(unittest.TestCase):
    def test_event_and_dead_link_boundaries(self) -> None:
        event = build_h6_news_event_mention_candidates({"source_id": "gdelt_news_event", "article_or_record_id": "a", "headline_or_title": "h"})[0]
        self.assertFalse(event["truth_boundary"]["news_event_mention_candidate_is_event_truth"])
        self.assertFalse(event["truth_boundary"]["article_metadata_proves_claim_accuracy"])
        self.assertFalse(event["truth_boundary"]["transcript_metadata_proves_full_context"])
        dead = build_h6_dead_link_trace_candidates({"source_id": "generic_web_archive", "dead_url_candidate": "fixture://dead"})[0]
        self.assertFalse(dead["truth_boundary"]["dead_link_trace_grants_acquisition_permission"])
        self.assertFalse(dead["truth_boundary"]["mirror_candidate_proves_authenticity"])
        self.assertFalse(dead["truth_boundary"]["checksum_candidate_proves_malware_safety"])

    def test_event_truth_claim_is_rejected(self) -> None:
        candidate = build_h6_news_event_mention_candidates({"source_id": "x", "headline_or_title": "h"})[0]
        mutated = copy.deepcopy(candidate)
        mutated["truth_boundary"]["news_event_mention_candidate_is_event_truth"] = True
        self.assertTrue(detect_h6_truth_boundary_violations(mutated))


if __name__ == "__main__":
    unittest.main()
