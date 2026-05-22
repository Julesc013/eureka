from __future__ import annotations

import copy
import unittest

from archive.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.media_transcript_metadata import build_h6_media_transcript_metadata_candidates
from archive.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.normalizer_common import detect_h6_truth_boundary_violations
from archive.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.public_document_trace import build_h6_public_document_trace_candidates


class H6PublicDocumentTraceMappingTests(unittest.TestCase):
    def test_public_document_and_media_boundaries(self) -> None:
        document = build_h6_public_document_trace_candidates({"source_id": "restricted_public_document_manifest", "document_record_id": "d", "sensitivity_class": "restricted"})[0]
        self.assertFalse(document["truth_boundary"]["public_document_trace_is_public_truth"])
        self.assertFalse(document["direct_fetch_allowed_current"])
        self.assertTrue(document["manifest_only_allowed"])
        self.assertFalse(document["truth_boundary"]["sensitive_source_access_approved"])
        media = build_h6_media_transcript_metadata_candidates({"source_id": "cspan_video_library", "media_or_program_id": "m", "transcript_or_caption_ref": "fixture://caption"})[0]
        self.assertFalse(media["download_allowed_current"])
        self.assertFalse(media["payload_available_current"])
        self.assertFalse(media["truth_boundary"]["transcript_metadata_proves_full_context"])
        self.assertFalse(media["truth_boundary"]["media_metadata_proves_event_truth"])

    def test_public_document_truth_claim_is_rejected(self) -> None:
        candidate = build_h6_public_document_trace_candidates({"source_id": "x", "document_record_id": "d"})[0]
        mutated = copy.deepcopy(candidate)
        mutated["truth_boundary"]["public_document_trace_is_public_truth"] = True
        self.assertTrue(detect_h6_truth_boundary_violations(mutated))


if __name__ == "__main__":
    unittest.main()
