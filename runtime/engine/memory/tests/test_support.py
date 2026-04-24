from __future__ import annotations

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
    CheckedSourceSummary,
    ObjectSummary,
    ResolutionMemoryRecord,
    ResolutionMemoryResultSummary,
    SourceSummary,
)
from runtime.engine.provenance import EvidenceSummary
from runtime.engine.query_planner import DeterministicQueryPlannerService
from runtime.engine.resolve import DeterministicSearchService, ExactMatchResolutionService
from runtime.engine.resolution_runs import LocalResolutionRunService, LocalResolutionRunStore
from runtime.source_registry import load_source_registry


KNOWN_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"
MISSING_TARGET_REF = "fixture:software/missing-demo-app@0.0.1"


def build_demo_normalized_catalog() -> NormalizedCatalog:
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


def build_demo_run_service(root: str) -> LocalResolutionRunService:
    catalog = build_demo_normalized_catalog()
    resolution_service = ExactMatchResolutionService(catalog)
    search_service = DeterministicSearchService(catalog)
    absence_service = DeterministicAbsenceService(
        catalog,
        resolution_service=resolution_service,
        search_service=search_service,
    )
    return LocalResolutionRunService(
        catalog=catalog,
        source_registry=load_source_registry(),
        resolution_service=resolution_service,
        search_service=search_service,
        absence_service=absence_service,
        run_store=LocalResolutionRunStore(root),
        query_planner=DeterministicQueryPlannerService(),
        timestamp_factory=lambda: "2026-04-25T00:00:00+00:00",
    )


def build_successful_resolution_memory(
    memory_id: str,
    *,
    memory_kind: str = "successful_resolution",
    source_run_id: str = "run-exact-resolution-0001",
    task_kind: str = "exact_resolution",
) -> ResolutionMemoryRecord:
    return ResolutionMemoryRecord(
        memory_id=memory_id,
        memory_kind=memory_kind,
        source_run_id=source_run_id,
        raw_query=None,
        task_kind=task_kind,
        requested_value=KNOWN_TARGET_REF,
        checked_source_ids=("github-releases-recorded-fixtures", "synthetic-fixtures"),
        checked_source_families=("github_releases", "synthetic"),
        checked_sources=(
            CheckedSourceSummary(
                source_id="synthetic-fixtures",
                name="Synthetic Fixtures",
                source_family="synthetic",
                status="active_fixture",
                trust_lane="fixture",
            ),
        ),
        result_summaries=(
            ResolutionMemoryResultSummary(
                target_ref=KNOWN_TARGET_REF,
                object_summary=ObjectSummary(
                    id="obj.synthetic-demo-app",
                    kind="software",
                    label="Synthetic Demo App",
                ),
                resolved_resource_id="obj.synthetic-demo-app",
                source=SourceSummary(
                    family="synthetic_fixture",
                    source_id="synthetic-fixtures",
                    label="Synthetic Fixtures",
                ),
            ),
        ),
        useful_source_ids=("synthetic-fixtures",),
        primary_resolved_resource_id="obj.synthetic-demo-app",
        evidence_summary=(
            EvidenceSummary(
                claim_kind="version",
                claim_value="1.0.0",
                asserted_by_family="synthetic",
                asserted_by_label="Synthetic Fixtures",
                evidence_kind="fixture_record",
                evidence_locator="fixtures/synthetic_software.json",
            ),
        ),
        created_at="2026-04-25T00:00:00+00:00",
        created_by_slice="resolution_memory_v0",
        invalidation_hints={"created_from_run": source_run_id},
    )
