from __future__ import annotations

import unittest

from runtime.gateway import build_demo_source_registry_public_api
from runtime.gateway.public_api import SourceCatalogRequest, SourceReadRequest


class SourceRegistryPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_source_registry_public_api()

    def test_list_sources_returns_seed_records(self) -> None:
        response = self.public_api.list_sources(SourceCatalogRequest.from_parts())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["status"], "listed")
        self.assertEqual(response.body["source_count"], 9)
        self.assertEqual(response.body["sources"][0]["source_id"], "article-scan-recorded-fixtures")
        self.assertEqual(response.body["sources"][0]["connector"]["status"], "fixture_backed")

    def test_list_sources_filters_by_status_role_and_surface(self) -> None:
        active_response = self.public_api.list_sources(
            SourceCatalogRequest.from_parts(status="active_fixture")
        )
        self.assertEqual(
            {entry["source_id"] for entry in active_response.body["sources"]},
            {"local-bundle-fixtures", "synthetic-fixtures"},
        )

        recorded_response = self.public_api.list_sources(
            SourceCatalogRequest.from_parts(status="active_recorded_fixture")
        )
        self.assertEqual(
            [entry["source_id"] for entry in recorded_response.body["sources"]],
            [
                "article-scan-recorded-fixtures",
                "github-releases-recorded-fixtures",
                "internet-archive-recorded-fixtures",
            ],
        )

        preservation_response = self.public_api.list_sources(
            SourceCatalogRequest.from_parts(role="preservation_anchor")
        )
        self.assertEqual(
            {entry["source_id"] for entry in preservation_response.body["sources"]},
            {
                "internet-archive-placeholder",
                "software-heritage-placeholder",
                "wayback-memento-placeholder",
            },
        )

        replay_response = self.public_api.list_sources(
            SourceCatalogRequest.from_parts(surface="replay")
        )
        self.assertEqual(
            [entry["source_id"] for entry in replay_response.body["sources"]],
            ["wayback-memento-placeholder"],
        )

    def test_get_source_returns_one_known_record(self) -> None:
        response = self.public_api.get_source(
            SourceReadRequest.from_parts("github-releases-recorded-fixtures")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["status"], "available")
        self.assertEqual(response.body["selected_source_id"], "github-releases-recorded-fixtures")
        self.assertEqual(response.body["source_count"], 1)
        self.assertEqual(response.body["sources"][0]["source_family"], "github_releases")

    def test_get_source_returns_structured_not_found(self) -> None:
        response = self.public_api.get_source(SourceReadRequest.from_parts("missing-source"))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["status"], "blocked")
        self.assertEqual(response.body["selected_source_id"], "missing-source")
        self.assertEqual(response.body["notices"][0]["code"], "source_id_not_found")

    def test_placeholder_sources_do_not_claim_connector_implementation(self) -> None:
        response = self.public_api.get_source(
            SourceReadRequest.from_parts("internet-archive-placeholder")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["sources"][0]["status"], "placeholder")
        self.assertEqual(response.body["sources"][0]["connector"]["status"], "unimplemented")


if __name__ == "__main__":
    unittest.main()
