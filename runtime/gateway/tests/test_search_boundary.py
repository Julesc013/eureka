from __future__ import annotations

import unittest

from runtime.gateway import build_demo_search_public_api
from runtime.gateway.public_api import SearchCatalogRequest


class SearchPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_search_public_api()

    def test_public_search_boundary_returns_multiple_matches(self) -> None:
        response = self.public_api.search_records(SearchCatalogRequest.from_parts("synthetic"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["query"], "synthetic")
        self.assertEqual(response.body["result_count"], 2)
        self.assertEqual(
            [entry["target_ref"] for entry in response.body["results"]],
            [
                "fixture:software/synthetic-demo-app@1.0.0",
                "fixture:software/synthetic-demo-suite@2.0.0",
            ],
        )

    def test_public_search_boundary_returns_one_match(self) -> None:
        response = self.public_api.search_records(SearchCatalogRequest.from_parts("compatibility"))

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.body["result_count"], 1)
        compatibility_result = next(
            entry
            for entry in response.body["results"]
            if entry["target_ref"] == "fixture:software/compatibility-lab@3.2.1"
        )
        self.assertEqual(
            compatibility_result["object"],
            {
                "id": "obj.compatibility-lab",
                "kind": "software",
                "label": "Compatibility Lab",
            },
        )
        self.assertTrue(compatibility_result["resolved_resource_id"].startswith("resolved:sha256:"))
        self.assertEqual(compatibility_result["source"]["label"], "Synthetic Fixture")
        self.assertEqual(compatibility_result["evidence"][0]["claim_kind"], "label")

    def test_public_search_boundary_surfaces_github_release_source_labels(self) -> None:
        response = self.public_api.search_records(SearchCatalogRequest.from_parts("archive"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["result_count"], 7)
        self.assertEqual(response.body["results"][3]["target_ref"], "github-release:archivebox/archivebox@v0.8.5")
        self.assertEqual(response.body["results"][3]["source"]["family"], "github_releases")
        self.assertEqual(response.body["results"][3]["source"]["label"], "GitHub Releases")
        self.assertEqual(
            response.body["results"][3]["source"]["locator"],
            "https://github.com/archivebox/archivebox/releases/tag/v0.8.5",
        )
        self.assertEqual(response.body["results"][3]["evidence"][1]["claim_kind"], "version")
        self.assertEqual(response.body["results"][3]["evidence"][1]["claim_value"], "v0.8.5")
        self.assertEqual(
            [entry["source"]["family"] for entry in response.body["results"][4:]],
            [
                "internet_archive_recorded",
                "internet_archive_recorded",
                "internet_archive_recorded",
            ],
        )

    def test_public_search_boundary_returns_structured_absence_for_no_matches(self) -> None:
        response = self.public_api.search_records(SearchCatalogRequest.from_parts("missing"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.body,
            {
                "query": "missing",
                "result_count": 0,
                "results": [],
                "absence": {
                    "code": "search_no_matches",
                    "message": "No bounded records matched query 'missing'.",
                },
            },
        )

    def test_public_search_boundary_projects_synthetic_member_context(self) -> None:
        response = self.public_api.search_records(SearchCatalogRequest.from_parts("driver.inf"))

        self.assertEqual(response.status_code, 200)
        member_result = next(
            entry
            for entry in response.body["results"]
            if entry["object"].get("member_path") == "drivers/wifi/thinkpad_t42/windows2000/driver.inf"
        )
        self.assertRegex(member_result["target_ref"], r"^member:sha256:[a-f0-9]{64}$")
        self.assertEqual(member_result["object"]["record_kind"], "synthetic_member")
        self.assertEqual(member_result["object"]["member_kind"], "driver")
        self.assertEqual(
            member_result["object"]["parent_target_ref"],
            "local-bundle-fixture:driver-support-cd@1.0",
        )
        self.assertEqual(member_result["source"]["source_id"], "local-bundle-fixtures")
