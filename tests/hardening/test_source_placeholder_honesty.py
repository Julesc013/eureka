import json
import unittest

from runtime.gateway import build_demo_source_registry_public_api
from runtime.gateway.public_api import SourceCatalogRequest
from tests.hardening.helpers import repo_path


ACTIVE_FIXTURE_SOURCE_IDS = {
    "article-scan-recorded-fixtures",
    "synthetic-fixtures",
    "github-releases-recorded-fixtures",
    "internet-archive-recorded-fixtures",
    "local-bundle-fixtures",
}


def _source_records():
    records = []
    for path in sorted(repo_path("control/inventory/sources").glob("*.source.json")):
        records.append(json.loads(path.read_text(encoding="utf-8")))
    return records


class SourcePlaceholderHonestyTest(unittest.TestCase):
    def test_placeholder_and_future_sources_do_not_claim_connector_implementation(self):
        for record in _source_records():
            status = record.get("status")
            source_id = record["source_id"]
            connector = record.get("connector", {})
            connector_status = connector.get("status")
            if status not in {"placeholder", "future", "local_private_future"}:
                continue

            self.assertNotEqual(connector_status, "fixture_backed", source_id)
            self.assertNotEqual(connector_status, "implemented", source_id)
            self.assertFalse(connector.get("entrypoint"), source_id)
            self.assertEqual(record["coverage"]["coverage_depth"], "source_known", source_id)
            self.assertFalse(record["capabilities"]["live_supported"], source_id)
            self.assertFalse(record["capabilities"]["recorded_fixture_backed"], source_id)
            combined = json.dumps(record, sort_keys=True).lower()
            self.assertRegex(combined, r"placeholder|future|deferred|unimplemented", source_id)

    def test_active_fixture_sources_have_existing_fixture_connector_entrypoints(self):
        records = {record["source_id"]: record for record in _source_records()}
        self.assertTrue(ACTIVE_FIXTURE_SOURCE_IDS.issubset(records))

        for source_id in ACTIVE_FIXTURE_SOURCE_IDS:
            connector = records[source_id]["connector"]
            self.assertEqual(connector.get("status"), "fixture_backed", source_id)
            entrypoint = connector.get("entrypoint")
            self.assertTrue(entrypoint, source_id)
            module_path = repo_path(entrypoint.replace(".", "/") + ".py")
            package_path = repo_path(entrypoint.replace(".", "/")) / "__init__.py"
            self.assertTrue(module_path.exists() or package_path.exists(), source_id)

    def test_local_files_source_stays_private_local_and_deferred(self):
        records = {record["source_id"]: record for record in _source_records()}
        local_files = records["local-files-placeholder"]
        combined = json.dumps(local_files, sort_keys=True).lower()

        self.assertEqual(local_files["status"], "local_private_future")
        self.assertEqual(local_files["connector"]["status"], "deferred")
        self.assertEqual(local_files["coverage"]["coverage_depth"], "source_known")
        self.assertEqual(local_files["coverage"]["connector_mode"], "local_private_future")
        self.assertTrue(local_files["capabilities"]["local_private"])
        self.assertFalse(local_files["capabilities"]["supports_action_paths"])
        self.assertIn("private", combined)
        self.assertIn("local", combined)

    def test_new_recorded_sources_are_distinct_from_placeholders(self):
        records = {record["source_id"]: record for record in _source_records()}

        self.assertEqual(records["internet-archive-placeholder"]["status"], "placeholder")
        self.assertEqual(records["internet-archive-placeholder"]["coverage"]["coverage_depth"], "source_known")
        self.assertEqual(records["internet-archive-recorded-fixtures"]["status"], "active_recorded_fixture")
        self.assertEqual(
            records["internet-archive-recorded-fixtures"]["coverage"]["connector_mode"],
            "recorded_fixture_only",
        )
        self.assertFalse(records["internet-archive-recorded-fixtures"]["capabilities"]["live_supported"])
        self.assertIn(
            "No live Internet Archive API",
            json.dumps(records["internet-archive-recorded-fixtures"], sort_keys=True),
        )

        self.assertEqual(records["article-scan-recorded-fixtures"]["status"], "active_recorded_fixture")
        self.assertEqual(
            records["article-scan-recorded-fixtures"]["coverage"]["coverage_depth"],
            "content_or_member_indexed",
        )
        self.assertFalse(records["article-scan-recorded-fixtures"]["capabilities"]["live_supported"])
        self.assertIn(
            "No real magazine scans",
            json.dumps(records["article-scan-recorded-fixtures"], sort_keys=True),
        )

        self.assertEqual(records["local-files-placeholder"]["status"], "local_private_future")
        self.assertEqual(records["local-bundle-fixtures"]["status"], "active_fixture")
        self.assertFalse(records["local-bundle-fixtures"]["capabilities"]["local_private"])
        self.assertTrue(records["local-bundle-fixtures"]["capabilities"]["fixture_backed"])
        self.assertIn(
            "No arbitrary user filesystem ingestion",
            json.dumps(records["local-bundle-fixtures"], sort_keys=True),
        )

    def test_public_source_view_does_not_present_placeholders_as_active(self):
        response = build_demo_source_registry_public_api().list_sources(
            SourceCatalogRequest.from_parts()
        )
        for source in response.body["sources"]:
            if source["source_id"] in ACTIVE_FIXTURE_SOURCE_IDS:
                continue
            self.assertIn(source["status"], {"placeholder", "future", "local_private_future"})
            self.assertEqual(source["coverage_depth"], "source_known")
            self.assertFalse(source["capabilities"]["live_supported"])
            self.assertNotIn("Active fixture-backed", source["status_summary"])


if __name__ == "__main__":
    unittest.main()
