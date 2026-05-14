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


def rich_status() -> dict:
    return {
        "status": "pass",
        "runtime": {
            "instance_id": "local-test",
            "instance_schema_version": "1",
            "instance_root": "D:/safe/local-instance",
            "store_count": 4,
            "migration_needed": False,
            "read_only": True,
            "server_enabled": False,
            "lan_enabled": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
            "stores": {
                "source_cache": {
                    "relative_path": "db/source_cache.sqlite",
                    "opened": True,
                    "integrity_status": "pass",
                    "schema_version": "source_cache_store.v0",
                },
                "evidence_ledger": {
                    "relative_path": "db/evidence_ledger.sqlite",
                    "opened": True,
                    "integrity_status": "pass",
                    "schema_version": "evidence_ledger_store.v0",
                },
                "review_queue": {
                    "relative_path": "db/review_queue.sqlite",
                    "opened": True,
                    "integrity_status": "pass",
                    "schema_version": "review_queue_store.v0",
                },
                "public_index": {
                    "relative_path": "db/public_index.sqlite",
                    "opened": True,
                    "integrity_status": "pass",
                    "schema_version": "public_index_store.v0",
                },
            },
        },
        "public_index": {
            "record_count": 1,
            "rebuild_count": 0,
            "source_ref_count": 1,
            "evidence_ref_count": 1,
            "review_ref_count": 1,
            "source_counts": {"source.example.metadata": 1},
        },
        "warnings": ["sample warning"],
        "limitations": ["local reviewed index only"],
    }


def rich_record() -> dict:
    return {
        "record_id": "pir_0123456789abcdef",
        "source_id": "source.example.metadata",
        "source_cache_entry_id": "sce_test",
        "evidence_id": "evc_test",
        "review_item_id": "rvi_test",
        "review_decision_id": "rvd_test",
        "title": "demo-project",
        "description": "Synthetic metadata for local review",
        "normalized_fields": {"name": "demo-project", "summary": "<escaped summary>"},
        "searchable_text": "demo-project synthetic metadata searchable excerpt",
        "source_family": "package_registry",
        "trust_lane": "synthetic_reviewed",
        "warnings": ["record warning"],
        "limitations": ["record limitation"],
    }


class LocalWorkbenchPageHardeningTests(unittest.TestCase):
    def assert_hardened_page(self, html: str) -> None:
        validate_local_workbench_page(html)
        self.assertIn("Local appliance prototype", html)
        lowered = html.lower()
        self.assertNotIn("production ready", lowered)
        self.assertNotIn("public launch ready", lowered)
        self.assertNotIn("globally complete", lowered)
        self.assertNotIn("exhaustive coverage", lowered)
        self.assertNotIn("<script", lowered)
        self.assertNotIn("method=\"post\"", lowered)
        self.assertNotIn("href=\"http://", lowered)
        self.assertNotIn("src=\"http://", lowered)

    def test_status_page_shows_store_status_and_disabled_flags(self) -> None:
        html = render_status_page(build_status_page_view(rich_status()))
        self.assert_hardened_page(html)
        for marker in ("Store status", "source_cache", "evidence_ledger", "review_queue", "public_index"):
            self.assertIn(marker, html)
        for marker in ("server_enabled", "lan_enabled", "deployment_performed", "production_readiness_claimed"):
            self.assertIn(marker, html)

    def test_search_page_shows_local_index_limitation_and_provenance(self) -> None:
        payload = {"result_count": 1, "results": [rich_record()], "warnings": [], "limitations": []}
        html = render_search_page(build_search_page_view("demo", payload))
        self.assert_hardened_page(html)
        self.assertIn("Reviewed results are from the local reviewed public index only", html)
        for marker in ("source_cache_entry_id", "evidence_id", "review_item_id", "review_decision_id"):
            self.assertIn(marker, html)
        self.assertIn("package_registry", html)
        self.assertIn("synthetic_reviewed", html)

    def test_object_page_shows_normalized_fields_provenance_and_escapes(self) -> None:
        html = render_object_page(build_object_page_view("pir_0123456789abcdef", rich_record()))
        self.assert_hardened_page(html)
        self.assertIn("Normalized fields", html)
        self.assertIn("&lt;escaped summary&gt;", html)
        self.assertNotIn("<escaped summary>", html)
        self.assertIn("searchable_text_excerpt", html)
        self.assertIn("source_cache_entry_id", html)
        self.assertIn("evidence_id", html)

    def test_source_page_states_local_scope_only(self) -> None:
        html = render_source_page(
            build_source_page_view(
                "source.example.metadata",
                {"result_count": 1, "records": [rich_record()], "warnings": [], "limitations": []},
            )
        )
        self.assert_hardened_page(html)
        self.assertIn("Source coverage shown here is local to the reviewed index", html)
        self.assertIn("source_record_count_in_local_reviewed_index", html)

    def test_absence_page_shows_checked_unchecked_layers_and_non_proof(self) -> None:
        html = render_absence_page(
            build_absence_page_view(
                "missing",
                {"absence": {"result_count": 0, "checked_sources": ["source.example.metadata"]}, "warnings": [], "limitations": []},
            )
        )
        self.assert_hardened_page(html)
        self.assertIn("reviewed_public_index", html)
        for marker in ("source probes", "WorkUnits", "extraction", "Search Hunt Sessions", "broader connectors", "AI/semantic search"):
            self.assertIn(marker, html)
        self.assertIn("Absence is not proof the artifact does not exist", html)

    def test_home_page_shows_unavailable_capabilities(self) -> None:
        html = render_home_page(build_home_page_view(rich_status()))
        self.assert_hardened_page(html)
        self.assertIn("Unavailable capabilities", html)
        self.assertIn("Durable queue records exist; execution remains disabled", html)
        self.assertIn("Only localhost is enabled", html)


if __name__ == "__main__":
    unittest.main()
