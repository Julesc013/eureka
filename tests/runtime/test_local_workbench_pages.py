from __future__ import annotations

import unittest

from runtime.local_workbench import (
    build_absence_page_view,
    build_home_page_view,
    build_object_page_view,
    build_search_page_view,
    build_source_page_view,
    build_status_page_view,
    render_absence_page,
    render_home_page,
    render_object_page,
    render_search_page,
    render_source_page,
    render_status_page,
    validate_local_workbench_page,
)


def sample_status() -> dict:
    return {
        "status": "pass",
        "runtime": {
            "instance_id": "local-test",
            "instance_schema_version": "1",
            "migration_needed": False,
            "server_enabled": False,
            "lan_enabled": False,
            "deployment_performed": False,
            "stores": {
                "public_index": {
                    "opened": True,
                    "integrity_status": "pass",
                    "schema_version": "public_index_store.v0",
                }
            },
            "warnings": [],
        },
        "public_index": {"record_count": 1},
        "warnings": [],
        "limitations": ["local reviewed index only"],
    }


def sample_record() -> dict:
    return {
        "record_id": "pir_0123456789abcdef",
        "source_id": "source.example.metadata",
        "source_cache_entry_id": "sce_test",
        "evidence_id": "evc_test",
        "review_item_id": "rvi_test",
        "review_decision_id": "rvd_test",
        "title": "demo-project",
        "description": "Synthetic metadata for local review",
        "normalized_fields": {"name": "demo-project", "summary": "Synthetic metadata"},
    }


class LocalWorkbenchPageTests(unittest.TestCase):
    def assert_valid_page(self, html: str) -> None:
        validate_local_workbench_page(html)
        self.assertIn('<html lang="en">', html)
        self.assertIn("<title>", html)
        self.assertIn("<nav", html)
        self.assertIn("Local appliance prototype", html)
        self.assertNotIn("<script", html.lower())
        self.assertNotIn("method=\"post\"", html.lower())
        self.assertNotIn("http://", html.lower())
        self.assertNotIn("https://", html.lower())

    def test_home_page_renders(self) -> None:
        html = render_home_page(build_home_page_view(sample_status()))
        self.assert_valid_page(html)
        self.assertIn("Eureka Local Appliance", html)
        self.assertIn("Search reviewed index", html)
        self.assertIn("<label", html)

    def test_search_page_renders_and_escapes_query(self) -> None:
        payload = {"result_count": 1, "results": [sample_record()], "warnings": [], "limitations": []}
        html = render_search_page(build_search_page_view("<needle>", payload))
        self.assert_valid_page(html)
        self.assertIn("&lt;needle&gt;", html)
        self.assertNotIn("<needle>", html)
        self.assertIn("Reviewed result count", html)
        self.assertIn("Reviewed results are from the local reviewed public index only", html)

    def test_object_page_renders_found_and_missing_states(self) -> None:
        found = render_object_page(build_object_page_view("pir_0123456789abcdef", sample_record()))
        missing = render_object_page(build_object_page_view("missing-record", None))
        self.assert_valid_page(found)
        self.assert_valid_page(missing)
        self.assertIn("Evidence and review references", found)
        self.assertIn("Normalized fields", found)
        self.assertIn("Object not found", missing)

    def test_source_page_renders_empty_state(self) -> None:
        html = render_source_page(
            build_source_page_view("source.example.metadata", {"result_count": 0, "records": [], "warnings": [], "limitations": []})
        )
        self.assert_valid_page(html)
        self.assertIn("No local reviewed index records", html)
        self.assertIn("Source coverage shown here is local", html)

    def test_absence_page_states_local_absence_only(self) -> None:
        html = render_absence_page(
            build_absence_page_view(
                "missing",
                {"absence": {"result_count": 0, "checked_sources": []}, "warnings": [], "limitations": []},
            )
        )
        self.assert_valid_page(html)
        self.assertIn("local current-index absence only, not global proof", html)
        self.assertIn("Checked local layers", html)
        self.assertIn("Unchecked and deferred layers", html)

    def test_status_page_renders_flags(self) -> None:
        html = render_status_page(build_status_page_view(sample_status()))
        self.assert_valid_page(html)
        self.assertIn("Instance ID", html)
        self.assertIn("Store status", html)
        self.assertIn("lan_enabled", html)
        self.assertIn("deployment_performed", html)


if __name__ == "__main__":
    unittest.main()
