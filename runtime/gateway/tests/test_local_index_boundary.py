from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.gateway import build_demo_local_index_public_api
from runtime.gateway.public_api import (
    LocalIndexBuildRequest,
    LocalIndexQueryRequest,
    LocalIndexStatusRequest,
)


class LocalIndexPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_local_index_public_api()

    def test_build_query_and_status_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = str(Path(temp_dir) / "local-index.sqlite3")
            build_response = self.public_api.build_index(
                LocalIndexBuildRequest.from_parts(index_path),
            )
            status_response = self.public_api.get_index_status(
                LocalIndexStatusRequest.from_parts(index_path),
            )
            query_response = self.public_api.query_index(
                LocalIndexQueryRequest.from_parts(index_path, "synthetic"),
            )

        self.assertEqual(build_response.status_code, 200)
        self.assertEqual(build_response.body["status"], "built")
        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(status_response.body["status"], "available")
        self.assertEqual(query_response.status_code, 200)
        self.assertEqual(query_response.body["status"], "queried")
        self.assertGreater(query_response.body["result_count"], 0)

    def test_missing_index_and_empty_query_return_structured_errors(self) -> None:
        missing_response = self.public_api.get_index_status(
            LocalIndexStatusRequest.from_parts("missing-index.sqlite3"),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = str(Path(temp_dir) / "local-index.sqlite3")
            self.public_api.build_index(LocalIndexBuildRequest.from_parts(index_path))
            empty_query_response = self.public_api.query_index(
                LocalIndexQueryRequest(index_path=index_path, query=""),
            )

        self.assertEqual(missing_response.status_code, 404)
        self.assertEqual(missing_response.body["notices"][0]["code"], "local_index_not_found")
        self.assertEqual(empty_query_response.status_code, 400)
        self.assertEqual(empty_query_response.body["notices"][0]["code"], "invalid_local_index_query")

    def test_query_projects_synthetic_member_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = str(Path(temp_dir) / "local-index.sqlite3")
            self.public_api.build_index(LocalIndexBuildRequest.from_parts(index_path))
            response = self.public_api.query_index(
                LocalIndexQueryRequest.from_parts(index_path, "driver.inf"),
            )

        member = next(
            result
            for result in response.body["results"]
            if result["record_kind"] == "synthetic_member"
            and result.get("member_path") == "drivers/wifi/thinkpad_t42/windows2000/driver.inf"
        )
        self.assertEqual(member["parent_target_ref"], "local-bundle-fixture:driver-support-cd@1.0")
        self.assertEqual(member["parent_representation_id"], "rep.local-bundle.driver-support-cd.zip")
        self.assertEqual(member["member_kind"], "driver")
        self.assertEqual(member["media_type"], "text/plain")
        self.assertRegex(member["content_hash"], r"^sha256:[a-f0-9]{64}$")
        self.assertIn("preview_member", member["action_hints"])
        self.assertEqual(member["primary_lane"], "inside_bundles")
        self.assertEqual(member["user_cost_score"], 1)
        self.assertIn("member_has_preview_or_readback_action", member["user_cost_reasons"])


if __name__ == "__main__":
    unittest.main()
