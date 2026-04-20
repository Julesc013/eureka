from __future__ import annotations

from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import extract_synthetic_source_record
from runtime.engine.interfaces.normalize import normalize_extracted_record
from runtime.engine.resolve import ExactMatchResolutionService
from runtime.gateway.public_api import InMemoryResolutionJobService, ResolutionJobsPublicApi


def build_demo_resolution_jobs_public_api() -> ResolutionJobsPublicApi:
    connector = SyntheticSoftwareConnector()
    normalized_records = tuple(
        normalize_extracted_record(extract_synthetic_source_record(record))
        for record in connector.load_source_records()
    )
    resolution_service = ExactMatchResolutionService(NormalizedCatalog(normalized_records))
    job_service = InMemoryResolutionJobService(resolution_service)
    return ResolutionJobsPublicApi(job_service)
