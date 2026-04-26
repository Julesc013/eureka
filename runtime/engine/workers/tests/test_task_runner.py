from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runtime.connectors.github_releases import GitHubReleasesConnector
from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.core import NormalizedCatalog
from runtime.engine.index import LocalIndexEngineService, LocalIndexSqliteStore
from runtime.engine.interfaces.extract import (
    extract_github_release_source_record,
    extract_synthetic_source_record,
)
from runtime.engine.interfaces.normalize import (
    normalize_extracted_record,
    normalize_github_release_record,
)
from runtime.engine.interfaces.public import LocalTaskReadRequest, LocalTaskRunRequest
from runtime.engine.workers import LocalTaskStore
from runtime.engine.workers.task_runner import LocalTaskRunnerService
from runtime.source_registry import load_source_registry


def _build_catalog() -> NormalizedCatalog:
    synthetic_records = tuple(
        normalize_extracted_record(extract_synthetic_source_record(record))
        for record in SyntheticSoftwareConnector().load_source_records()
    )
    github_records = tuple(
        normalize_github_release_record(extract_github_release_source_record(record))
        for record in GitHubReleasesConnector().load_source_records()
    )
    return NormalizedCatalog(synthetic_records + github_records)


class LocalTaskRunnerServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        catalog = _build_catalog()
        source_registry = load_source_registry()
        self._index_service = LocalIndexEngineService(
            catalog=catalog,
            source_registry=source_registry,
            sqlite_store=LocalIndexSqliteStore(),
        )
        self._source_registry = source_registry

    def test_validate_source_registry_task_completes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(temp_dir)
            task = service.run_task(
                LocalTaskRunRequest.from_parts("validate_source_registry"),
            )

        self.assertEqual(task.status, "completed")
        self.assertEqual(task.task_kind, "validate_source_registry")
        self.assertEqual(task.result_summary["source_count"], 8)
        self.assertEqual(
            task.result_summary["active_fixture_sources"],
            ["local-bundle-fixtures", "synthetic-fixtures"],
        )
        self.assertEqual(
            task.result_summary["active_recorded_fixture_sources"],
            ["github-releases-recorded-fixtures", "internet-archive-recorded-fixtures"],
        )

    def test_build_local_index_task_completes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(temp_dir)
            index_path = str(Path(temp_dir) / "local-index.sqlite3")
            task = service.run_task(
                LocalTaskRunRequest.from_parts(
                    "build_local_index",
                    {"index_path": index_path},
                ),
            )

        self.assertEqual(task.status, "completed")
        self.assertEqual(task.output_references["index"]["index_path"], index_path)
        self.assertGreater(task.result_summary["record_count"], 0)

    def test_query_local_index_task_completes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(temp_dir)
            index_path = str(Path(temp_dir) / "local-index.sqlite3")
            service.run_task(
                LocalTaskRunRequest.from_parts(
                    "build_local_index",
                    {"index_path": index_path},
                ),
            )
            task = service.run_task(
                LocalTaskRunRequest.from_parts(
                    "query_local_index",
                    {"index_path": index_path, "query": "archive"},
                ),
            )

        self.assertEqual(task.status, "completed")
        self.assertEqual(task.result_summary["query"], "archive")
        self.assertGreaterEqual(task.result_summary["result_count"], 1)

    def test_validate_archive_resolution_evals_task_completes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(temp_dir)
            task = service.run_task(
                LocalTaskRunRequest.from_parts("validate_archive_resolution_evals"),
            )

        self.assertEqual(task.status, "completed")
        self.assertGreaterEqual(task.result_summary["task_count"], 1)

    def test_unsupported_task_kind_blocks_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(temp_dir)
            task = service.run_task(
                LocalTaskRunRequest.from_parts("unsupported_task_kind"),
            )

        self.assertEqual(task.status, "blocked")
        self.assertEqual(task.error_summary["code"], "unsupported_task_kind")

    def test_missing_local_index_blocks_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(temp_dir)
            task = service.run_task(
                LocalTaskRunRequest.from_parts(
                    "query-local-index",
                    {
                        "index_path": str(Path(temp_dir) / "missing.sqlite3"),
                        "query": "archive",
                    },
                ),
            )

        self.assertEqual(task.status, "blocked")
        self.assertEqual(task.error_summary["code"], "local_index_not_found")

    def test_persisted_task_can_be_read_back(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(temp_dir)
            created = service.run_task(LocalTaskRunRequest.from_parts("validate_source_registry"))
            loaded = service.get_task(LocalTaskReadRequest.from_parts(created.task_id))

        self.assertEqual(loaded.task_id, created.task_id)
        self.assertEqual(loaded.status, "completed")

    def _build_service(self, root: str) -> LocalTaskRunnerService:
        return LocalTaskRunnerService(
            task_store=LocalTaskStore(root),
            source_registry=self._source_registry,
            local_index_service=self._index_service,
            timestamp_factory=lambda: "2026-04-24T00:00:00+00:00",
        )


if __name__ == "__main__":
    unittest.main()
