from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.connectors.web import FetchRequest, HTTPTransportResult, SafeHTTPFetcher
from runtime.connectors.web.dns_guard import DNSGuard
from runtime.connectors.web.robots import AllowAllRobotsClient
from runtime.index.preview import SQLitePreviewIndexStore
from runtime.index.preview.recovery import (
    create_backup,
    list_backups,
    migration_preflight,
    rebuild_probe,
    restore_backup,
    verify_backup,
)
from runtime.local.portable_instance import build_portable_paths


class PreviewIndexRecoveryTests(unittest.TestCase):
    def test_backup_verify_restore_and_rebuild_probe(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            target = root / "target"
            paths = build_portable_paths(source)
            paths.config_dir.mkdir(parents=True, exist_ok=True)
            (paths.config_dir / "instance.json").write_text('{"instance_id":"test"}\n', encoding="utf-8")
            fetched = _fetcher().fetch(FetchRequest("https://example.test/manual", query="Sound Blaster", run_id="run-1"))
            store = SQLitePreviewIndexStore(paths.preview_sqlite)
            try:
                store.upsert_observations([fetched.observation])
                stats = store.stats()
            finally:
                store.close()

            backup = create_backup(
                instance_root=source,
                backup_root=paths.backup_root,
                sqlite_path=paths.preview_sqlite,
                run_root=paths.run_bundles,
                foundry_root=source / "run" / "foundry" / "runs",
                config_dir=paths.config_dir,
                generation_root=paths.preview_index,
            )
            listed = list_backups(paths.backup_root)
            verified = verify_backup(backup["backup_path"])
            restored = restore_backup(backup["backup_path"], target)
            restored_store = SQLitePreviewIndexStore(target / "db" / "preview" / "preview.sqlite")
            try:
                restored_search = restored_store.search("Sound Blaster", limit=5)
            finally:
                restored_store.close()
            preflight = migration_preflight(paths.preview_sqlite)
            rebuild = rebuild_probe(paths.preview_sqlite)

        self.assertEqual(1, stats["document_count"])
        self.assertEqual("pass", backup["status"])
        self.assertEqual(1, listed["backup_count"])
        self.assertEqual("pass", verified["status"])
        self.assertEqual("pass", restored["status"])
        self.assertEqual(1, restored_search["result_count"])
        self.assertEqual("pass", preflight["status"])
        self.assertEqual("pass", rebuild["status"])
        self.assertTrue(rebuild["rebuild_possible"])
        self.assertFalse(backup["provider_result_payload_included"])

    def test_corrupt_backup_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = build_portable_paths(root / "source")
            paths.config_dir.mkdir(parents=True, exist_ok=True)
            (paths.config_dir / "instance.json").write_text('{"instance_id":"test"}\n', encoding="utf-8")
            store = SQLitePreviewIndexStore(paths.preview_sqlite)
            store.close()
            backup = create_backup(
                instance_root=paths.root,
                backup_root=paths.backup_root,
                sqlite_path=paths.preview_sqlite,
                run_root=paths.run_bundles,
                foundry_root=paths.root / "run" / "foundry" / "runs",
                config_dir=paths.config_dir,
                generation_root=paths.preview_index,
            )
            sqlite_copy = Path(backup["backup_path"]) / "db" / "preview" / "preview.sqlite"
            sqlite_copy.write_bytes(b"not sqlite")
            verified = verify_backup(backup["backup_path"])

        self.assertEqual("fail", verified["status"])
        self.assertTrue(verified["errors"])


def _fetcher() -> SafeHTTPFetcher:
    def transport(_url: str, _headers: object, _timeout: int, _max_bytes: int) -> HTTPTransportResult:
        return HTTPTransportResult(200, {"Content-Type": "text/html; charset=utf-8"}, b"<html><title>Manual</title><body>Sound Blaster CT1740 manual text</body></html>")

    return SafeHTTPFetcher(
        dns_guard=DNSGuard(resolver=lambda _host: ("93.184.216.34",)),
        robots_client=AllowAllRobotsClient(),
        transport=transport,
        clock=lambda: "2026-06-21T00:00:00Z",
    )


if __name__ == "__main__":
    unittest.main()
