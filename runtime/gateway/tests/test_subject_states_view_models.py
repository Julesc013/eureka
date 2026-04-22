from __future__ import annotations

import unittest

from runtime.gateway import build_demo_subject_states_public_api
from runtime.gateway.public_api import (
    SubjectStatesCatalogRequest,
    subject_states_envelope_to_view_model,
)


class SubjectStatesViewModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_subject_states_public_api()

    def test_subject_states_envelope_maps_to_shared_view_model(self) -> None:
        response = self.public_api.list_subject_states(
            SubjectStatesCatalogRequest.from_parts("archivebox")
        )

        view_model = subject_states_envelope_to_view_model(response.body)

        self.assertEqual(view_model["status"], "listed")
        self.assertEqual(view_model["subject"]["subject_label"], "ArchiveBox")
        self.assertEqual(view_model["states"][0]["normalized_version_or_state"], "0.8.5")
        self.assertEqual(view_model["states"][1]["source"]["label"], "GitHub Releases")
        self.assertEqual(view_model["states"][1]["evidence"][1]["claim_kind"], "version")


if __name__ == "__main__":
    unittest.main()
