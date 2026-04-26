from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.connectors.local_bundle_fixtures import LocalBundleFixturesConnector
from runtime.engine.core import NormalizedCatalog
from runtime.engine.index import LocalIndexSqliteStore, build_index_records
from runtime.engine.interfaces.extract import extract_local_bundle_source_record
from runtime.engine.interfaces.normalize import normalize_local_bundle_record
from runtime.engine.interfaces.public import ResolutionRequest
from runtime.engine.resolve import ExactMatchResolutionService
from runtime.engine.synthetic_records import synthesize_member_normalized_records
from runtime.source_registry import load_source_registry


def _catalog_with_synthetic_members() -> NormalizedCatalog:
    parent_records = tuple(
        normalize_local_bundle_record(extract_local_bundle_source_record(record))
        for record in LocalBundleFixturesConnector().load_source_records()
    )
    member_records = synthesize_member_normalized_records(parent_records)
    return NormalizedCatalog(parent_records + member_records)


class MemberLevelSyntheticRecordsIndexTestCase(unittest.TestCase):
    def test_index_includes_first_class_synthetic_member_records(self) -> None:
        records = build_index_records(_catalog_with_synthetic_members(), load_source_registry())
        driver_record = next(
            record
            for record in records
            if record.record_kind == "synthetic_member"
            and record.member_path == "drivers/wifi/thinkpad_t42/windows2000/driver.inf"
        )

        self.assertRegex(driver_record.target_ref or "", r"^member:sha256:[a-f0-9]{64}$")
        self.assertEqual(driver_record.parent_target_ref, "local-bundle-fixture:driver-support-cd@1.0")
        self.assertEqual(driver_record.parent_representation_id, "rep.local-bundle.driver-support-cd.zip")
        self.assertEqual(driver_record.source_id, "local-bundle-fixtures")
        self.assertEqual(driver_record.member_kind, "driver")
        self.assertEqual(driver_record.media_type, "text/plain")
        self.assertIn("preview_member", driver_record.action_hints)
        self.assertEqual(driver_record.primary_lane, "inside_bundles")
        self.assertIn("best_direct_answer", driver_record.result_lanes)
        self.assertEqual(driver_record.user_cost_score, 1)
        self.assertIn("member_has_path", driver_record.user_cost_reasons)

    def test_index_queries_find_synthetic_members(self) -> None:
        records = build_index_records(_catalog_with_synthetic_members(), load_source_registry())
        store = LocalIndexSqliteStore()

        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "local-index.sqlite3"
            store.build(index_path, records)
            _, thinkpad_results, _ = store.query(index_path, "thinkpad")
            _, driver_results, _ = store.query(index_path, "driver.inf")
            _, seven_zip_results, _ = store.query(index_path, "7z920")
            _, ftp_results, _ = store.query(index_path, "ftp blue")

        self.assertTrue(
            any(result.record_kind == "synthetic_member" for result in thinkpad_results)
        )
        self.assertTrue(
            any(
                result.record_kind == "synthetic_member"
                and result.member_path == "drivers/wifi/thinkpad_t42/windows2000/driver.inf"
                for result in driver_results
            )
        )
        self.assertTrue(
            any(
                result.record_kind == "synthetic_member"
                and result.member_path == "utilities/7z920.exe.txt"
                for result in seven_zip_results
            )
        )
        self.assertTrue(
            any(
                result.record_kind == "synthetic_member"
                and result.member_path == "utilities/ftp-blue-client/readme.txt"
                for result in ftp_results
            )
        )
        driver_member = next(
            result
            for result in thinkpad_results
            if result.record_kind == "synthetic_member"
            and result.member_path == "drivers/wifi/thinkpad_t42/windows2000/driver.inf"
        )
        parent_bundle = next(
            result
            for result in thinkpad_results
            if result.record_kind == "resolved_object"
            and result.target_ref == "local-bundle-fixture:driver-support-cd@1.0"
        )
        self.assertLess(driver_member.user_cost_score or 9, parent_bundle.user_cost_score or 9)
        self.assertEqual(driver_member.primary_lane, "inside_bundles")
        self.assertIn("parent_bundle_context_only", parent_bundle.user_cost_reasons)

    def test_exact_resolution_supports_synthetic_member_target_refs(self) -> None:
        catalog = _catalog_with_synthetic_members()
        member = next(
            record
            for record in catalog.records
            if record.member_path == "drivers/wifi/thinkpad_t42/windows2000/driver.inf"
        )
        outcome = ExactMatchResolutionService(catalog).resolve(
            ResolutionRequest.from_parts(member.target_ref)
        )

        self.assertEqual(outcome.status, "completed")
        self.assertIsNotNone(outcome.result)
        assert outcome.result is not None
        self.assertEqual(outcome.result.primary_object.member_path, member.member_path)
        self.assertEqual(
            outcome.result.primary_object.parent_target_ref,
            "local-bundle-fixture:driver-support-cd@1.0",
        )
        self.assertEqual(outcome.result.primary_object.primary_lane, "inside_bundles")
        self.assertEqual(outcome.result.primary_object.user_cost_score, 1)
        self.assertTrue(
            any(item.claim_kind == "member_path" for item in outcome.result.evidence)
        )


if __name__ == "__main__":
    unittest.main()
