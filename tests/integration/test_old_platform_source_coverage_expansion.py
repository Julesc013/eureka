from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.gateway import build_demo_local_index_public_api
from runtime.gateway.public_api import LocalIndexBuildRequest, LocalIndexQueryRequest


class OldPlatformSourceCoverageExpansionIntegrationTestCase(unittest.TestCase):
    def test_expanded_fixture_result_carries_source_member_lane_and_compatibility(self) -> None:
        api = build_demo_local_index_public_api()

        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "old-platform-source-coverage.sqlite3"
            build = api.build_index(LocalIndexBuildRequest.from_parts(str(index_path)))
            query = api.query_index(
                LocalIndexQueryRequest.from_parts(str(index_path), "creative ct1740")
            )

        self.assertEqual(build.status_code, 200)
        self.assertEqual(query.status_code, 200)
        result = next(
            item
            for item in query.body["results"]
            if item.get("member_path") == "drivers/sound/creative_ct1740/windows98/driver.inf"
            and item.get("record_kind") == "synthetic_member"
        )

        self.assertEqual(result["source_id"], "local-bundle-fixtures")
        self.assertEqual(result["primary_lane"], "inside_bundles")
        self.assertLessEqual(result["user_cost_score"], 1)
        self.assertIn("parent_target_ref", result)
        self.assertTrue(
            any(
                evidence.get("platform", {}).get("name") == "Windows 98"
                for evidence in result.get("compatibility_evidence", [])
            )
        )

    def test_documentation_only_browser_fixture_is_findable_without_live_source_claims(self) -> None:
        api = build_demo_local_index_public_api()

        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "old-platform-source-coverage.sqlite3"
            api.build_index(LocalIndexBuildRequest.from_parts(str(index_path)))
            query = api.query_index(
                LocalIndexQueryRequest.from_parts(str(index_path), "mac os 9 browser")
            )

        self.assertEqual(query.status_code, 200)
        result = next(
            item
            for item in query.body["results"]
            if item.get("target_ref") == "internet-archive-recorded:ia-mac-os9-browser-doc-fixture"
            and item.get("record_kind") == "resolved_object"
        )

        self.assertEqual(result["source_id"], "internet-archive-recorded-fixtures")
        self.assertIn("documentation", result["label"].casefold())
        self.assertTrue(
            any(
                evidence.get("platform", {}).get("name") == "Mac OS 9"
                for evidence in result.get("compatibility_evidence", [])
            )
        )
        self.assertNotIn("live", (result.get("usefulness_summary") or "").casefold())


if __name__ == "__main__":
    unittest.main()
