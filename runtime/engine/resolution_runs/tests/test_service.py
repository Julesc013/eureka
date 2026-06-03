from __future__ import annotations

import tempfile
from typing import Any
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
    SearchRequest,
)
from runtime.engine.query_planner import DeterministicQueryPlannerService
from runtime.engine.resolve import DeterministicSearchService, ExactMatchResolutionService
from runtime.engine.resolution_runs import (
    LocalResolutionRunService,
    LocalResolutionRunStore,
    ResolutionRunFallbackPolicy,
)
from runtime.source.registry import load_source_registry


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
        self.assertIsNone(run.fallback_summary)

    def test_deterministic_search_results_do_not_call_fallback_provider(self) -> None:
        provider = FakeFallbackProvider()
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(
                temp_dir,
                fallback_provider=provider,
                fallback_policy=ResolutionRunFallbackPolicy(enabled=True),
            )
            run = service.run_deterministic_search(
                DeterministicSearchRunRequest.from_parts("synthetic"),
            )

        self.assertIsNotNone(run.result_summary)
        self.assertIsNone(run.fallback_summary)
        self.assertEqual(provider.calls, [])

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
        self.assertIsNone(run.fallback_summary)

    def test_search_miss_records_governed_fallback_candidate(self) -> None:
        provider = FakeFallbackProvider()
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(
                temp_dir,
                fallback_provider=provider,
                fallback_policy=ResolutionRunFallbackPolicy(enabled=True),
            )
            run = service.run_deterministic_search(
                DeterministicSearchRunRequest.from_parts("missing"),
            )

        fallback = run.fallback_summary or {}
        self.assertEqual(provider.calls, [("missing", 5)])
        self.assertEqual(run.status, "completed")
        self.assertIsNone(run.result_summary)
        self.assertIsNotNone(run.absence_report)
        self.assertEqual(fallback["mode"], "indexless_live_search_fallback")
        self.assertEqual(fallback["status"], "candidate")
        self.assertEqual(fallback["trigger"], "local_lookup_no_results")
        self.assertEqual(fallback["candidate_count"], 1)
        self.assertFalse(fallback["verified"])
        self.assertFalse(fallback["accepted_truth"])
        self.assertFalse(fallback["reviewed_record_created"])
        self.assertFalse(fallback["reviewed_index_mutated"])
        self.assertEqual(fallback["candidates"][0]["status"], "candidate")
        self.assertFalse(fallback["candidates"][0]["verified"])
        self.assertFalse(fallback["source_observation"]["accepted_truth"])
        self.assertIn("indexless_fallback_candidate", [notice.code for notice in run.notices])

    def test_unavailable_local_index_can_record_fallback_candidate(self) -> None:
        provider = FakeFallbackProvider()
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(
                temp_dir,
                search_service=FailingSearchService(),
                fallback_provider=provider,
                fallback_policy=ResolutionRunFallbackPolicy(enabled=True),
            )
            run = service.run_deterministic_search(
                DeterministicSearchRunRequest.from_parts("missing"),
            )

        fallback = run.fallback_summary or {}
        self.assertEqual(run.status, "completed")
        self.assertEqual(fallback["status"], "candidate")
        self.assertEqual(fallback["trigger"], "local_lookup_unavailable")
        self.assertEqual(provider.calls, [("missing", 5)])
        self.assertIn("local_lookup_unavailable", [notice.code for notice in run.notices])

    def test_fallback_disabled_is_policy_blocked_and_does_not_call_provider(self) -> None:
        provider = FakeFallbackProvider()
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(
                temp_dir,
                fallback_provider=provider,
                fallback_policy=ResolutionRunFallbackPolicy(enabled=False),
            )
            run = service.run_deterministic_search(
                DeterministicSearchRunRequest.from_parts("missing"),
            )

        fallback = run.fallback_summary or {}
        self.assertEqual(provider.calls, [])
        self.assertEqual(fallback["status"], "policy_blocked")
        self.assertIn("fallback_disabled", fallback["reason_codes"])

    def test_source_family_disabled_blocks_fallback_without_calling_provider(self) -> None:
        provider = FakeFallbackProvider()
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(
                temp_dir,
                fallback_provider=provider,
                fallback_policy=ResolutionRunFallbackPolicy(
                    enabled=True,
                    disabled_source_families=("internet_archive",),
                ),
            )
            run = service.run_deterministic_search(
                DeterministicSearchRunRequest.from_parts("missing"),
            )

        fallback = run.fallback_summary or {}
        self.assertEqual(provider.calls, [])
        self.assertEqual(fallback["status"], "policy_blocked")
        self.assertIn("source_family_disabled", fallback["reason_codes"])

    def test_source_allowlist_denial_blocks_fallback_without_calling_provider(self) -> None:
        provider = FakeFallbackProvider()
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(
                temp_dir,
                fallback_provider=provider,
                fallback_policy=ResolutionRunFallbackPolicy(
                    enabled=True,
                    allowed_source_families=("software_heritage",),
                ),
            )
            run = service.run_deterministic_search(
                DeterministicSearchRunRequest.from_parts("missing"),
            )

        fallback = run.fallback_summary or {}
        self.assertEqual(provider.calls, [])
        self.assertEqual(fallback["status"], "policy_blocked")
        self.assertIn("source_family_not_allowlisted", fallback["reason_codes"])

    def test_budget_exceeded_degrades_without_calling_provider(self) -> None:
        provider = FakeFallbackProvider()
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(
                temp_dir,
                fallback_provider=provider,
                fallback_policy=ResolutionRunFallbackPolicy(enabled=True, max_requests=0),
            )
            run = service.run_deterministic_search(
                DeterministicSearchRunRequest.from_parts("missing"),
            )

        fallback = run.fallback_summary or {}
        self.assertEqual(provider.calls, [])
        self.assertEqual(fallback["status"], "unavailable")
        self.assertEqual(fallback["failure_reason"], "fallback_budget_exceeded")

    def test_source_timeout_degrades_without_truth_promotion(self) -> None:
        provider = FakeFallbackProvider(error=TimeoutError("metadata timeout"))
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(
                temp_dir,
                fallback_provider=provider,
                fallback_policy=ResolutionRunFallbackPolicy(enabled=True),
            )
            run = service.run_deterministic_search(
                DeterministicSearchRunRequest.from_parts("missing"),
            )

        fallback = run.fallback_summary or {}
        self.assertEqual(provider.calls, [("missing", 5)])
        self.assertEqual(fallback["status"], "unavailable")
        self.assertEqual(fallback["failure_reason"], "source_timeout")
        self.assertFalse(fallback["verified"])
        self.assertFalse(fallback["accepted_truth"])
        self.assertFalse(fallback["reviewed_index_mutated"])

    def test_successful_fallback_without_candidates_records_need(self) -> None:
        provider = FakeFallbackProvider(
            result={
                "schema_version": "archive_org_metadata_candidate_search.v0",
                "status": "succeeded",
                "query": "missing",
                "source_id": "internet_archive_metadata",
                "source_family": "internet_archive",
                "source_label": "Internet Archive metadata search",
                "candidate_count": 0,
                "candidates": [],
                "total_http_requests": 1,
                "live_call_performed": True,
                "metadata_request_performed": True,
                "accepted_truth": False,
                "review_required": True,
                "warnings": [],
                "limitations": ["archive_org_metadata_only", "candidate_not_reviewed_truth"],
            }
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(
                temp_dir,
                fallback_provider=provider,
                fallback_policy=ResolutionRunFallbackPolicy(enabled=True),
            )
            run = service.run_deterministic_search(
                DeterministicSearchRunRequest.from_parts("missing"),
            )

        fallback = run.fallback_summary or {}
        self.assertEqual(fallback["status"], "need")
        self.assertEqual(fallback["candidate_count"], 0)
        self.assertEqual(fallback["need_count"], 1)
        self.assertEqual(fallback["needs"][0]["status"], "need")

    def test_planned_search_run_records_resolution_task(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(temp_dir)
            run = service.run_planned_search(
                PlannedSearchRunRequest.from_parts("latest Firefox before XP support ended"),
            )

        self.assertEqual(run.run_kind, "planned_search")
        self.assertIsNotNone(run.resolution_task)
        self.assertEqual(
            run.resolution_task.task_kind if run.resolution_task else "",
            "find_latest_compatible_release",
        )
        self.assertEqual(run.resolution_task.constraints["product_hint"] if run.resolution_task else "", "Firefox")
        self.assertIsNone(run.result_summary)
        self.assertIsNotNone(run.absence_report)

    def _build_service(
        self,
        root: str,
        *,
        search_service=None,
        fallback_provider=None,
        fallback_policy: ResolutionRunFallbackPolicy | None = None,
    ) -> LocalResolutionRunService:
        return LocalResolutionRunService(
            catalog=self._catalog,
            source_registry=self._source_registry,
            resolution_service=self._resolution_service,
            search_service=search_service or self._search_service,
            absence_service=self._absence_service,
            run_store=LocalResolutionRunStore(root),
            query_planner=DeterministicQueryPlannerService(),
            fallback_provider=fallback_provider,
            fallback_policy=fallback_policy or ResolutionRunFallbackPolicy(),
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


class FakeFallbackProvider:
    source_id = "internet_archive_metadata"
    source_family = "internet_archive"

    def __init__(self, *, result: dict[str, Any] | None = None, error: Exception | None = None) -> None:
        self._result = result
        self._error = error
        self.calls: list[tuple[str, int]] = []

    def search_metadata_candidates(self, query: str, limit: int) -> dict[str, Any]:
        self.calls.append((query, limit))
        if self._error is not None:
            raise self._error
        if self._result is not None:
            return dict(self._result)
        return {
            "schema_version": "archive_org_metadata_candidate_search.v0",
            "status": "succeeded",
            "query": query,
            "source_id": self.source_id,
            "source_family": self.source_family,
            "source_label": "Internet Archive metadata search",
            "candidate_count": 1,
            "candidates": [
                {
                    "candidate_id": "ia-meta-candidate:test",
                    "candidate_title": "Archive.org metadata candidate",
                    "candidate_summary": "Metadata-only candidate; review required before use.",
                    "source_id": self.source_id,
                    "source_family": self.source_family,
                    "source_locator": {
                        "url": "https://archive.org/details/test",
                    },
                    "limitations": ["archive_org_metadata_only", "candidate_not_reviewed_truth"],
                    "warnings": ["Candidate requires review."],
                }
            ],
            "total_http_requests": 1,
            "live_call_performed": True,
            "metadata_request_performed": True,
            "raw_response_committed": False,
            "download_performed": False,
            "upload_performed": False,
            "extraction_executed": False,
            "accepted_truth": False,
            "review_required": True,
            "warnings": ["Archive.org metadata candidate requires review."],
            "limitations": ["archive_org_metadata_only", "candidate_not_reviewed_truth"],
        }


class FailingSearchService:
    def search(self, request: SearchRequest):
        raise RuntimeError("local index unavailable")


if __name__ == "__main__":
    unittest.main()
