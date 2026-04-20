from __future__ import annotations

from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.actions import ResolutionManifestExportService
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import extract_synthetic_source_record
from runtime.engine.interfaces.normalize import normalize_extracted_record
from runtime.engine.resolve import DeterministicSearchService, ExactMatchResolutionService
from runtime.engine.snapshots import ResolutionBundleExportService
from runtime.gateway.public_api import (
    InMemoryResolutionJobService,
    ResolutionActionsPublicApi,
    ResolutionJobsPublicApi,
    SearchPublicApi,
)


def build_demo_resolution_jobs_public_api() -> ResolutionJobsPublicApi:
    catalog = _build_demo_normalized_catalog()
    resolution_service = ExactMatchResolutionService(catalog)
    job_service = InMemoryResolutionJobService(resolution_service)
    return ResolutionJobsPublicApi(job_service)


def build_demo_search_public_api() -> SearchPublicApi:
    catalog = _build_demo_normalized_catalog()
    search_service = DeterministicSearchService(catalog)
    return SearchPublicApi(search_service)


def build_demo_resolution_actions_public_api() -> ResolutionActionsPublicApi:
    catalog = _build_demo_normalized_catalog()
    manifest_service = ResolutionManifestExportService(catalog)
    bundle_service = ResolutionBundleExportService(catalog)
    return ResolutionActionsPublicApi(
        manifest_service=manifest_service,
        bundle_service=bundle_service,
    )


def _build_demo_normalized_catalog() -> NormalizedCatalog:
    connector = SyntheticSoftwareConnector()
    normalized_records = tuple(
        normalize_extracted_record(extract_synthetic_source_record(record))
        for record in connector.load_source_records()
    )
    return NormalizedCatalog(normalized_records)
