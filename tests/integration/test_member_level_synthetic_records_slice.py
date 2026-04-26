from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.gateway import (
    build_demo_local_index_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from runtime.gateway.public_api import (
    LocalIndexBuildRequest,
    LocalIndexQueryRequest,
    SearchCatalogRequest,
    SubmitResolutionJobRequest,
)


class MemberLevelSyntheticRecordsSliceTestCase(unittest.TestCase):
    def test_member_record_flows_through_search_index_and_exact_resolution(self) -> None:
        search_response = build_demo_search_public_api().search_records(
            SearchCatalogRequest.from_parts("driver.inf"),
        )
        member_search_result = next(
            result
            for result in search_response.body["results"]
            if result["object"].get("member_path") == "drivers/wifi/thinkpad_t42/windows2000/driver.inf"
        )
        member_target_ref = member_search_result["target_ref"]

        index_api = build_demo_local_index_public_api()
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = str(Path(temp_dir) / "local-index.sqlite3")
            index_api.build_index(LocalIndexBuildRequest.from_parts(index_path))
            index_response = index_api.query_index(
                LocalIndexQueryRequest.from_parts(index_path, "driver.inf")
            )

        member_index_result = next(
            result
            for result in index_response.body["results"]
            if result["record_kind"] == "synthetic_member"
            and result.get("target_ref") == member_target_ref
        )
        self.assertEqual(member_index_result["parent_target_ref"], "local-bundle-fixture:driver-support-cd@1.0")
        self.assertEqual(member_index_result["member_kind"], "driver")

        resolution_api = build_demo_resolution_jobs_public_api()
        submit_response = resolution_api.submit_resolution_job(
            SubmitResolutionJobRequest.from_parts(member_target_ref)
        )
        read_response = resolution_api.read_resolution_job(submit_response.body["job_id"])

        self.assertEqual(read_response.body["status"], "completed")
        primary_object = read_response.body["result"]["primary_object"]
        self.assertEqual(primary_object["record_kind"], "synthetic_member")
        self.assertEqual(primary_object["member_path"], "drivers/wifi/thinkpad_t42/windows2000/driver.inf")
        self.assertEqual(primary_object["parent_target_ref"], "local-bundle-fixture:driver-support-cd@1.0")


if __name__ == "__main__":
    unittest.main()
