import json
import unittest

from runtime.gateway import build_demo_source_registry_public_api
from runtime.gateway.public_api import SourceCatalogRequest
from tests.hardening.helpers import repo_path


ACTIVE_FIXTURE_SOURCE_IDS = {
    "synthetic-fixtures",
    "github-releases-recorded-fixtures",
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
            if status not in {"placeholder", "future"}:
                continue

            self.assertNotEqual(connector_status, "fixture_backed", source_id)
            self.assertNotEqual(connector_status, "implemented", source_id)
            self.assertFalse(connector.get("entrypoint"), source_id)
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

        self.assertEqual(local_files["status"], "future")
        self.assertEqual(local_files["connector"]["status"], "deferred")
        self.assertIn("private", combined)
        self.assertIn("local", combined)

    def test_public_source_view_does_not_present_placeholders_as_active(self):
        response = build_demo_source_registry_public_api().list_sources(
            SourceCatalogRequest.from_parts()
        )
        for source in response.body["sources"]:
            if source["source_id"] in ACTIVE_FIXTURE_SOURCE_IDS:
                continue
            self.assertIn(source["status"], {"placeholder", "future"})
            self.assertNotIn("Active fixture-backed", source["status_summary"])


if __name__ == "__main__":
    unittest.main()
