from __future__ import annotations

import copy
import unittest

from archive.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.normalizer_common import detect_h6_truth_boundary_violations
from archive.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.web_capture_identity import build_h6_web_capture_identity_candidate


class H6WebCaptureIdentityMappingTests(unittest.TestCase):
    def test_capture_identity_remains_candidate(self) -> None:
        candidate = build_h6_web_capture_identity_candidate({
            "source_id": "wayback_cdx_memento",
            "original_url": "fixture://example",
            "capture_url": "fixture://capture",
            "capture_digest": "fixture-digest",
        })
        self.assertFalse(candidate["truth_boundary"]["web_capture_identity_candidate_is_accepted_capture_truth"])
        self.assertFalse(candidate["truth_boundary"]["capture_presence_proves_completeness"])
        self.assertFalse(candidate["truth_boundary"]["capture_digest_proves_authenticity"])
        self.assertFalse(candidate["truth_boundary"]["archived_content_proves_rights_clearance"])

    def test_capture_truth_claim_is_rejected(self) -> None:
        candidate = build_h6_web_capture_identity_candidate({"source_id": "x", "original_url": "fixture://x"})
        mutated = copy.deepcopy(candidate)
        mutated["truth_boundary"]["capture_digest_proves_authenticity"] = True
        self.assertTrue(detect_h6_truth_boundary_violations(mutated))


if __name__ == "__main__":
    unittest.main()
