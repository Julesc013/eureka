from __future__ import annotations

import tempfile
import unittest

from runtime.connectors.github_releases import GitHubReleasesConnector
from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.absence import DeterministicAbsenceService
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import (
    extract_github_release_source_record,
    extract_synthetic_source_record,
)
from runtime.engine.interfaces.normalize import (
    normalize_extracted_record,
    normalize_github_release_record,
)
from runtime.engine.interfaces.public import (
    DeterministicSearchRunRequest,
    ExactResolutionRunRequest,
    PlannedSearchRunRequest,
)
from runtime.engine.query_planner import DeterministicQueryPlannerService
from runtime.engine.resolve import DeterministicSearchService, ExactMatchResolutionService
from runtime.engine.resolution_runs import LocalResolutionRunService, LocalResolutionRunStore
from runtime.source_registry import load_source_registry


KNOWN_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"
MISSING_TARGET_REF = "fixture:software/missing-demo-app@0.0.1"


class LocalResolutionRunServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        catalog = _build_demo_normalized_catalog()
        self._catalog = catalog
        self._source_registry = load_source_registry()
        self._resolution_service = ExactMatchResolutionService(catalog)
        self._search_service = DeterministicSearchService(catalog)
        self._absence_service = DeterministicAbsenceService(
            catalog,
            resolution_service=self._resolution_service,
            search_service=self._search_service,
        )

    def test_exact_resolution_run_records_result_and_checked_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(temp_dir)
            run = service.run_exact_resolution(
                ExactResolutionRunRequest.from_parts(KNOWN_TARGET_REF),
            )

        self.assertEqual(run.run_kind, "exact_resolution")
        self.assertEqual(run.status, "completed")
        self.assertEqual(run.checked_source_ids, ("github-releases-recorded-fixtures", "synthetic-fixtures"))
        self.assertEqual(
            run.checked_source_families,
            ("github_releases", "synthetic"),
        )
        self.assertIsNotNone(run.result_summary)
        self.assertEqual(run.result_summary.result_count if run.result_summary else 0, 1)
        self.assertIsNone(run.absence_report)
        self.assertEqual(run.checked_sources[0].source_id, "github-releases-recorded-fixtures")

    def test_exact_resolution_run_records_absence_for_missing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(temp_dir)
            run = service.run_exact_resolution(
                ExactResolutionRunRequest.from_parts(MISSING_TARGET_REF),
            )

        self.assertEqual(run.status, "completed")
        self.assertIsNone(run.result_summary)
        self.assertIsNotNone(run.absence_report)
        self.assertEqual(run.absence_report.request_kind if run.absence_report else "", "resolve")
        self.assertEqual(run.absence_report.requested_value if run.absence_report else "", MISSING_TARGET_REF)

    def test_deterministic_search_run_records_results(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(temp_dir)
            run = service.run_deterministic_search(
                DeterministicSearchRunRequest.from_parts("synthetic"),
            )

        self.assertEqual(run.run_kind, "deterministic_search")
        self.assertEqual(run.status, "completed")
        self.assertIsNotNone(run.result_summary)
        self.assertEqual(run.result_summary.result_count if run.result_summary else 0, 2)
        self.assertIsNone(run.absence_report)

    def test_deterministic_search_run_records_absence_without_placeholder_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(temp_dir)
            run = service.run_deterministic_search(
                DeterministicSearchRunRequest.from_parts("missing"),
            )

        self.assertEqual(run.status, "completed")
        self.assertIsNone(run.result_summary)
        self.assertIsNotNone(run.absence_report)
        self.assertNotIn("internet-archive-placeholder", run.checked_source_ids)
        self.assertNotIn("wayback-memento-placeholder", run.checked_source_ids)
        self.assertNotIn("software-heritage-placeholder", run.checked_source_ids)

    def test_planned_search_run_records_resolution_task(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(temp_dir)
            run = service.run_planned_search(
                PlannedSearchRunRequest.from_parts("latest Firefox before XP support ended"),
            )

        self.assertEqual(run.run_kind, "planned_search")
        self.assertIsNotNone(run.resolution_task)
        self.assertEqual(run.resolution_task.task_kind if run.resolution_task else "", "find_software_release")
        self.assertEqual(run.resolution_task.constraints["product_hint"] if run.resolution_task else "", "Firefox")
        self.assertIsNone(run.result_summary)
        self.assertIsNotNone(run.absence_report)

    def _build_service(self, root: str) -> LocalResolutionRunService:
        return LocalResolutionRunService(
            catalog=self._catalog,
            source_registry=self._source_registry,
            resolution_service=self._resolution_service,
            search_service=self._search_service,
            absence_service=self._absence_service,
            run_store=LocalResolutionRunStore(root),
            query_planner=DeterministicQueryPlannerService(),
            timestamp_factory=lambda: "2026-04-24T00:00:00+00:00",
        )


def _build_demo_normalized_catalog() -> NormalizedCatalog:
    synthetic_connector = SyntheticSoftwareConnector()
    github_connector = GitHubReleasesConnector()
    synthetic_records = tuple(
        normalize_extracted_record(extract_synthetic_source_record(record))
        for record in synthetic_connector.load_source_records()
    )
    github_records = tuple(
        normalize_github_release_record(extract_github_release_source_record(record))
        for record in github_connector.load_source_records()
    )
    return NormalizedCatalog(synthetic_records + github_records)


if __name__ == "__main__":
    unittest.main()
