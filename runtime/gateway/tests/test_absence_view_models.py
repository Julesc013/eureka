from __future__ import annotations

import unittest

from runtime.gateway import build_demo_absence_public_api
from runtime.gateway.public_api import (
    ExplainResolveMissRequest,
    ExplainSearchMissRequest,
    absence_envelope_to_view_model,
)


class AbsenceViewModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_absence_public_api()

    def test_absence_view_model_maps_resolution_miss(self) -> None:
        response = self.public_api.explain_resolution_miss(
            ExplainResolveMissRequest.from_parts("fixture:software/archivebox@9.9.9"),
        )

        view_model = absence_envelope_to_view_model(response.body)

        self.assertEqual(view_model["request_kind"], "resolve")
        self.assertEqual(view_model["requested_value"], "fixture:software/archivebox@9.9.9")
        self.assertEqual(
            view_model["checked_source_families"],
            [
                "synthetic_fixture",
                "github_releases",
                "internet_archive_recorded",
                "local_bundle_fixtures",
                "article_scan_recorded",
                "wayback_memento_recorded",
                "software_heritage_recorded",
                "package_registry_recorded",
                "manual_document_recorded",
                "review_description_recorded",
                "sourceforge_recorded",
            ],
        )
        self.assertEqual(view_model["near_matches"][0]["subject_key"], "archivebox")
        self.assertEqual(view_model["near_matches"][0]["evidence"][0]["claim_kind"], "label")

    def test_absence_view_model_maps_search_miss_without_near_matches(self) -> None:
        response = self.public_api.explain_search_miss(
            ExplainSearchMissRequest.from_parts("totally missing bounded query"),
        )

        view_model = absence_envelope_to_view_model(response.body)

        self.assertEqual(view_model["request_kind"], "search")
        self.assertEqual(view_model["status"], "explained")
        self.assertEqual(view_model["likely_reason_code"], "query_not_present_in_bounded_corpus")
        self.assertEqual(view_model["near_matches"], [])
