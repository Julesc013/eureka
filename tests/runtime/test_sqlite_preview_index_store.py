from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.connectors.web import FetchRequest, HTTPTransportResult, SafeHTTPFetcher
from runtime.connectors.web.dns_guard import DNSGuard
from runtime.connectors.web.robots import AllowAllRobotsClient
from runtime.index.preview import SQLitePreviewIndexStore, load_preview_manifest, validate_preview_index
from runtime.local.portable_instance import _search_portable_index, build_portable_paths


class SQLitePreviewIndexStoreTests(unittest.TestCase):
    def test_restart_search_export_and_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            portable_paths = build_portable_paths(root)
            db_path = portable_paths.preview_sqlite
            fetcher = _fetcher_for(
                {
                    "https://example.test/manual": b"<html><head><title>CT1740 Manual</title></head><body>Sound Blaster CT1740 jumper settings</body></html>",
                    "https://example.test/driver": b"<html><head><title>CT1740 Driver</title></head><body>Creative driver package for Sound Blaster</body></html>",
                }
            )
            first = fetcher.fetch(FetchRequest("https://example.test/manual", query="Sound Blaster CT1740", run_id="hunt-1"))
            self.assertEqual("fetched", first.status)
            store = SQLitePreviewIndexStore(db_path)
            upsert = store.upsert_observations([first.observation])
            first_export = store.export_generation(root / "export")
            store.close()

            reopened = SQLitePreviewIndexStore(db_path)
            search = reopened.search("CT1740 jumper", limit=5)
            reopened.close()
            portable_search = _search_portable_index(portable_paths, "CT1740 jumper", index="local", limit=5)
            reopened = SQLitePreviewIndexStore(portable_paths.preview_sqlite)
            second = fetcher.fetch(FetchRequest("https://example.test/driver", query="Sound Blaster driver", run_id="hunt-1"))
            reopened.upsert_observations([second.observation])
            second_export = reopened.export_generation(root / "export")
            rollback = reopened.rollback(root / "export", first_export["generation_id"])
            stats = reopened.stats()
            first_validation = validate_preview_index(first_export["current_path"])
            second_validation = validate_preview_index(second_export["current_path"])
            current = load_preview_manifest(Path(first_export["current_path"]))
            reopened.close()

        self.assertEqual("pass", upsert["status"])
        self.assertEqual(1, search["result_count"])
        self.assertEqual(1, portable_search["result_count"])
        self.assertEqual("sqlite_preview", portable_search["index"])
        self.assertEqual("INDEXED - UNREVIEWED", search["results"][0]["state"])
        self.assertIn(first.observation.observation_id, search["results"][0]["observation_refs"])
        self.assertEqual("pass", first_validation["status"])
        self.assertEqual("pass", second_validation["status"])
        self.assertNotEqual(first_export["generation_id"], second_export["generation_id"])
        self.assertEqual(first_export["generation_id"], rollback["to_generation"])
        self.assertEqual(first_export["generation_id"], current["generation_id"])
        self.assertEqual(2, stats["observation_count"])
        self.assertFalse(search["reviewed_master_mutation"])
        self.assertFalse(search["public_index_mutation"])


def _fetcher_for(pages: dict[str, bytes]) -> SafeHTTPFetcher:
    def transport(url: str, _headers: object, _timeout: int, _max_bytes: int) -> HTTPTransportResult:
        return HTTPTransportResult(200, {"Content-Type": "text/html; charset=utf-8"}, pages[url])

    return SafeHTTPFetcher(
        dns_guard=DNSGuard(resolver=lambda _host: ("93.184.216.34",)),
        robots_client=AllowAllRobotsClient(),
        transport=transport,
        clock=lambda: "2026-06-21T00:00:00Z",
    )


if __name__ == "__main__":
    unittest.main()
