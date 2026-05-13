from __future__ import annotations

import copy
import unittest

from control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.archived_url_time_state import build_h6_archived_url_time_state_candidate
from control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.normalizer_common import detect_h6_truth_boundary_violations


class H6ArchivedUrlTimeStateMappingTests(unittest.TestCase):
    def test_time_state_remains_candidate(self) -> None:
        candidate = build_h6_archived_url_time_state_candidate({
            "source_id": "wayback_cdx_memento",
            "original_url": "fixture://example",
            "nearest_capture": "2024-01-02T00:00:00Z",
        })
        self.assertFalse(candidate["truth_boundary"]["archived_time_state_candidate_is_historical_truth"])
        self.assertFalse(candidate["truth_boundary"]["nearest_capture_proves_exact_state"])
        self.assertFalse(candidate["truth_boundary"]["missing_capture_proves_absence"])
        self.assertFalse(candidate["truth_boundary"]["archived_download_page_grants_download_permission"])

    def test_time_state_truth_claim_is_rejected(self) -> None:
        candidate = build_h6_archived_url_time_state_candidate({"source_id": "x", "original_url": "fixture://x"})
        mutated = copy.deepcopy(candidate)
        mutated["truth_boundary"]["nearest_capture_proves_exact_state"] = True
        self.assertTrue(detect_h6_truth_boundary_violations(mutated))


if __name__ == "__main__":
    unittest.main()
