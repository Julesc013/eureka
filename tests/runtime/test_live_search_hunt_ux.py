from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from urllib.parse import quote

from runtime.index.preview import SQLitePreviewIndexStore
from runtime.local.service.request_context import build_request_context
from runtime.local.service.routes import route_request


class LiveSearchHuntUXTests(unittest.TestCase):
    def test_search_page_inspection_and_hunt_progress_are_product_facing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            db_path = Path(temp) / "preview.sqlite"
            store = SQLitePreviewIndexStore(db_path)
            store.upsert_observations([_observation()])
            search_result = store.search("CT1740", limit=1)["results"][0]
            store.close()
            runtime = SimpleNamespace(
                live_search_enabled=True,
                live_search_provider="brave",
                eureka_preview_sqlite_path=db_path,
                e2e_explore_preview_index_path=None,
            )

            search = route_request(runtime, build_request_context("GET", "/search?q=CT1740", None, "127.0.0.1"))
            inspect = route_request(runtime, build_request_context("GET", f"/results/{quote(search_result['document_id'])}", None, "127.0.0.1"))
            hunt = route_request(runtime, build_request_context("GET", "/hunt?q=CT1740&max_fetches=0", None, "127.0.0.1"))

        self.assertEqual(200, search.status_code)
        self.assertIn("Eureka", search.body)
        self.assertIn("Local", search.body)
        self.assertIn("Live", search.body)
        self.assertIn("Indexed", search.body)
        self.assertIn("INDEXED - UNREVIEWED", search.body)
        self.assertIn("Inspect", search.body)
        self.assertNotIn("review packet", search.body.lower())
        self.assertNotIn("architecture", search.body.lower())
        self.assertNotIn("task id", search.body.lower())

        self.assertEqual(200, inspect.status_code)
        self.assertIn("Durable CT1740 observation text", inspect.body)
        self.assertIn("Content hash", inspect.body)
        self.assertIn("Outbound links", inspect.body)

        self.assertEqual(200, hunt.status_code)
        self.assertIn("Hunt progress", hunt.body)
        self.assertIn("Queries", hunt.body)
        self.assertIn("Providers", hunt.body)
        self.assertNotIn("<pre>{", hunt.body)


def _observation() -> dict[str, object]:
    return {
        "schema_version": "source_observation.v0",
        "observation_id": "observation:ux-test",
        "status": "unreviewed",
        "requested_url": "https://example.test/manual",
        "final_url": "https://example.test/manual",
        "canonical_url": "https://example.test/manual",
        "retrieved_at": "2026-06-21T00:00:00Z",
        "http_status": 200,
        "content_type": "text/html; charset=utf-8",
        "mime": "text/html",
        "charset": "utf-8",
        "content_hash": "sha256:ux-test",
        "title": "CT1740 Manual",
        "extracted_title": "CT1740 Manual",
        "extracted_text": "Durable CT1740 observation text for inspection.",
        "outbound_links": [
            {
                "schema_version": "link_edge.v0",
                "source_url": "https://example.test/manual",
                "target_url": "https://example.test/driver",
                "rel": "",
                "anchor_text": "driver",
            }
        ],
        "query": "CT1740",
        "run_id": "hunt-ux",
        "fetch_policy_result": "allowed",
        "fetch_policy_version": "fetch_policy.v0",
        "selected_headers": {"Content-Type": "text/html; charset=utf-8"},
        "redirects": [],
        "source_family": "web",
        "retention_policy": {"provider_result_payload_persisted": False},
        "provider_result_payload_persisted": False,
    }


if __name__ == "__main__":
    unittest.main()
