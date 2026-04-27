from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runtime.gateway import (
    build_demo_decomposition_public_api,
    build_demo_local_index_public_api,
    build_demo_member_access_public_api,
    build_demo_source_registry_public_api,
)
from runtime.gateway.public_api import (
    DecompositionInspectionRequest,
    LocalIndexBuildRequest,
    LocalIndexQueryRequest,
    MemberAccessReadRequest,
    SourceReadRequest,
)
from surfaces.native.cli.main import main as cli_main


class RealSourceCoveragePackIntegrationTestCase(unittest.TestCase):
    def test_public_source_projection_includes_new_active_fixture_sources(self) -> None:
        api = build_demo_source_registry_public_api()

        article = api.get_source(SourceReadRequest.from_parts("article-scan-recorded-fixtures"))
        ia = api.get_source(SourceReadRequest.from_parts("internet-archive-recorded-fixtures"))
        local = api.get_source(SourceReadRequest.from_parts("local-bundle-fixtures"))

        self.assertEqual(article.status_code, 200)
        self.assertEqual(article.body["sources"][0]["status"], "active_recorded_fixture")
        self.assertEqual(article.body["sources"][0]["coverage_depth"], "content_or_member_indexed")
        self.assertFalse(article.body["sources"][0]["capabilities"]["live_supported"])
        self.assertEqual(ia.status_code, 200)
        self.assertEqual(ia.body["sources"][0]["status"], "active_recorded_fixture")
        self.assertFalse(ia.body["sources"][0]["capabilities"]["live_supported"])
        self.assertIn("No live Internet Archive API", json.dumps(ia.body))
        self.assertEqual(local.status_code, 200)
        self.assertEqual(local.body["sources"][0]["status"], "active_fixture")
        self.assertTrue(local.body["sources"][0]["capabilities"]["supports_member_listing"])

    def test_index_and_member_access_flow_for_local_bundle_fixture(self) -> None:
        index_api = build_demo_local_index_public_api()
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "real-source-coverage-pack.sqlite3"
            build = index_api.build_index(LocalIndexBuildRequest.from_parts(str(index_path)))
            query = index_api.query_index(LocalIndexQueryRequest.from_parts(str(index_path), "thinkpad"))

            self.assertEqual(build.status_code, 200)
            self.assertTrue(
                any(
                    result["source_id"] == "local-bundle-fixtures"
                    for result in query.body["results"]
                )
            )

        decomposition = build_demo_decomposition_public_api().decompose_representation(
            DecompositionInspectionRequest.from_parts(
                "local-bundle-fixture:driver-support-cd@1.0",
                "rep.local-bundle.driver-support-cd.zip",
            )
        )
        self.assertEqual(decomposition.body["decomposition_status"], "decomposed")
        self.assertTrue(
            any(
                member["member_path"] == "drivers/wifi/thinkpad_t42/windows2000/driver.inf"
                for member in decomposition.body["members"]
            )
        )

        member = build_demo_member_access_public_api().read_member(
            MemberAccessReadRequest.from_parts(
                "local-bundle-fixture:driver-support-cd@1.0",
                "rep.local-bundle.driver-support-cd.zip",
                "drivers/wifi/thinkpad_t42/windows2000/driver.inf",
            )
        )
        self.assertEqual(member.body["member_access_status"], "read")
        self.assertEqual(member.body["reason_codes"], ["member_readback_succeeded"])
        self.assertNotIn("text_preview", member.body)

    def test_cli_source_detail_mentions_recorded_fixture_scope(self) -> None:
        from io import StringIO

        output = StringIO()
        exit_code = cli_main(["source", "internet-archive-recorded-fixtures"], stdout=output)

        self.assertEqual(exit_code, 0)
        text = output.getvalue()
        self.assertIn("internet-archive-recorded-fixtures", text)
        self.assertIn("active_recorded_fixture", text)
        self.assertIn("recorded_fixture_only", text)


if __name__ == "__main__":
    unittest.main()
