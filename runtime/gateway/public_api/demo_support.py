from __future__ import annotations

from runtime.connectors.github_releases import GitHubReleasesConnector
from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.acquisition.service import DeterministicAcquisitionService
from runtime.engine.decomposition.service import DeterministicDecompositionService
from runtime.engine.evals import build_archive_resolution_eval_runner_from_corpus
from runtime.engine.index import LocalIndexEngineService, LocalIndexSqliteStore
from runtime.engine.members.service import DeterministicMemberAccessService
from runtime.engine.memory import (
    LocalResolutionMemoryService,
    LocalResolutionMemoryStore,
    ResolutionMemoryBuilder,
)
from runtime.engine.action_routing.service import DeterministicActionPlanService
from runtime.engine.actions import ResolutionManifestExportService
from runtime.engine.absence import DeterministicAbsenceService
from runtime.engine.compatibility.service import DeterministicCompatibilityService
from runtime.engine.compare import DeterministicComparisonService
from runtime.engine.core import NormalizedCatalog
from runtime.engine.handoff.service import DeterministicRepresentationSelectionService
from runtime.engine.interfaces.extract import (
    extract_github_release_source_record,
    extract_synthetic_source_record,
)
from runtime.engine.interfaces.normalize import (
    normalize_extracted_record,
    normalize_github_release_record,
)
from runtime.engine.query_planner import DeterministicQueryPlannerService
from runtime.engine.resolution_runs import LocalResolutionRunService, LocalResolutionRunStore
from runtime.engine.workers import LocalTaskRunnerService, LocalTaskStore
from runtime.engine.representations.service import DeterministicRepresentationsService
from runtime.engine.resolve import DeterministicSearchService, ExactMatchResolutionService
from runtime.engine.states import DeterministicSubjectStatesService
from runtime.engine.snapshots import ResolutionBundleExportService, ResolutionBundleInspectionEngineService
from runtime.engine.store import LocalExportStore, ResolutionExportStoreEngineService
from runtime.source_registry import load_source_registry
from runtime.gateway.public_api.action_plan_boundary import ActionPlanPublicApi
from runtime.gateway.public_api.archive_resolution_evals_boundary import (
    ArchiveResolutionEvalsPublicApi,
)
from runtime.gateway.public_api.acquisition_boundary import AcquisitionPublicApi
from runtime.gateway.public_api.decomposition_boundary import DecompositionPublicApi
from runtime.gateway.public_api.member_access_boundary import MemberAccessPublicApi
from runtime.gateway.public_api.absence_boundary import AbsencePublicApi
from runtime.gateway.public_api.comparison_boundary import ComparisonPublicApi
from runtime.gateway.public_api.compatibility_boundary import CompatibilityPublicApi
from runtime.gateway.public_api.resolution_actions import ResolutionActionsPublicApi
from runtime.gateway.public_api.resolution_boundary import ResolutionJobsPublicApi
from runtime.gateway.public_api.resolution_bundle_inspection import ResolutionBundleInspectionPublicApi
from runtime.gateway.public_api.resolution_jobs import InMemoryResolutionJobService
from runtime.gateway.public_api.query_planner_boundary import QueryPlannerPublicApi
from runtime.gateway.public_api.local_index_boundary import LocalIndexPublicApi
from runtime.gateway.public_api.local_tasks_boundary import LocalTasksPublicApi
from runtime.gateway.public_api.resolution_memory_boundary import ResolutionMemoryPublicApi
from runtime.gateway.public_api.resolution_runs_boundary import ResolutionRunsPublicApi
from runtime.gateway.public_api.representations_boundary import RepresentationsPublicApi
from runtime.gateway.public_api.representation_selection_boundary import (
    RepresentationSelectionPublicApi,
)
from runtime.gateway.public_api.search_boundary import SearchPublicApi
from runtime.gateway.public_api.source_registry_boundary import SourceRegistryPublicApi
from runtime.gateway.public_api.stored_exports import StoredExportsPublicApi
from runtime.gateway.public_api.subject_states_boundary import SubjectStatesPublicApi


def build_demo_resolution_jobs_public_api() -> ResolutionJobsPublicApi:
    catalog = _build_demo_normalized_catalog()
    resolution_service = ExactMatchResolutionService(catalog)
    job_service = InMemoryResolutionJobService(resolution_service)
    return ResolutionJobsPublicApi(job_service)


def build_demo_action_plan_public_api() -> ActionPlanPublicApi:
    catalog = _build_demo_normalized_catalog()
    resolution_service = ExactMatchResolutionService(catalog)
    compatibility_service = DeterministicCompatibilityService(
        catalog,
        resolution_service=resolution_service,
    )
    action_plan_service = DeterministicActionPlanService(
        catalog,
        resolution_service=resolution_service,
        compatibility_service=compatibility_service,
    )
    return ActionPlanPublicApi(action_plan_service)


def build_demo_search_public_api() -> SearchPublicApi:
    catalog = _build_demo_normalized_catalog()
    search_service = DeterministicSearchService(catalog)
    return SearchPublicApi(search_service)


def build_demo_local_index_public_api() -> LocalIndexPublicApi:
    catalog = _build_demo_normalized_catalog()
    source_registry = load_source_registry()
    index_service = LocalIndexEngineService(
        catalog=catalog,
        source_registry=source_registry,
        sqlite_store=LocalIndexSqliteStore(),
    )
    return LocalIndexPublicApi(index_service)


def build_demo_archive_resolution_evals_public_api() -> ArchiveResolutionEvalsPublicApi:
    catalog = _build_demo_normalized_catalog()
    source_registry = load_source_registry()
    eval_runner = build_archive_resolution_eval_runner_from_corpus(
        catalog,
        source_registry,
    )
    return ArchiveResolutionEvalsPublicApi(eval_runner)


def build_demo_local_tasks_public_api(task_store_root: str) -> LocalTasksPublicApi:
    catalog = _build_demo_normalized_catalog()
    source_registry = load_source_registry()
    index_service = LocalIndexEngineService(
        catalog=catalog,
        source_registry=source_registry,
        sqlite_store=LocalIndexSqliteStore(),
    )
    task_service = LocalTaskRunnerService(
        task_store=LocalTaskStore(task_store_root),
        source_registry=source_registry,
        local_index_service=index_service,
    )
    return LocalTasksPublicApi(task_service)


def build_demo_resolution_memory_public_api(
    memory_store_root: str,
    *,
    run_store_root: str | None = None,
) -> ResolutionMemoryPublicApi:
    memory_service = LocalResolutionMemoryService(
        memory_store=LocalResolutionMemoryStore(memory_store_root),
        memory_builder=ResolutionMemoryBuilder(),
        run_service=(
            _build_demo_resolution_run_service(run_store_root)
            if run_store_root is not None
            else None
        ),
    )
    return ResolutionMemoryPublicApi(memory_service)


def build_demo_source_registry_public_api() -> SourceRegistryPublicApi:
    return SourceRegistryPublicApi(load_source_registry())


def build_demo_query_planner_public_api() -> QueryPlannerPublicApi:
    return QueryPlannerPublicApi(DeterministicQueryPlannerService())


def build_demo_resolution_runs_public_api(run_store_root: str) -> ResolutionRunsPublicApi:
    return ResolutionRunsPublicApi(_build_demo_resolution_run_service(run_store_root))


def build_demo_absence_public_api() -> AbsencePublicApi:
    catalog = _build_demo_normalized_catalog()
    resolution_service = ExactMatchResolutionService(catalog)
    search_service = DeterministicSearchService(catalog)
    absence_service = DeterministicAbsenceService(
        catalog,
        resolution_service=resolution_service,
        search_service=search_service,
    )
    return AbsencePublicApi(absence_service)


def build_demo_comparison_public_api() -> ComparisonPublicApi:
    catalog = _build_demo_normalized_catalog()
    resolution_service = ExactMatchResolutionService(catalog)
    comparison_service = DeterministicComparisonService(
        catalog,
        resolution_service=resolution_service,
    )
    return ComparisonPublicApi(comparison_service)


def build_demo_subject_states_public_api() -> SubjectStatesPublicApi:
    catalog = _build_demo_normalized_catalog()
    subject_states_service = DeterministicSubjectStatesService(catalog)
    return SubjectStatesPublicApi(subject_states_service)


def build_demo_compatibility_public_api() -> CompatibilityPublicApi:
    catalog = _build_demo_normalized_catalog()
    resolution_service = ExactMatchResolutionService(catalog)
    compatibility_service = DeterministicCompatibilityService(
        catalog,
        resolution_service=resolution_service,
    )
    return CompatibilityPublicApi(compatibility_service)


def build_demo_representations_public_api() -> RepresentationsPublicApi:
    catalog = _build_demo_normalized_catalog()
    resolution_service = ExactMatchResolutionService(catalog)
    representations_service = DeterministicRepresentationsService(
        catalog,
        resolution_service=resolution_service,
    )
    return RepresentationsPublicApi(representations_service)


def build_demo_acquisition_public_api() -> AcquisitionPublicApi:
    catalog = _build_demo_normalized_catalog()
    resolution_service = ExactMatchResolutionService(catalog)
    acquisition_service = DeterministicAcquisitionService(
        catalog,
        resolution_service=resolution_service,
    )
    return AcquisitionPublicApi(acquisition_service)


def build_demo_decomposition_public_api() -> DecompositionPublicApi:
    catalog = _build_demo_normalized_catalog()
    resolution_service = ExactMatchResolutionService(catalog)
    acquisition_service = DeterministicAcquisitionService(
        catalog,
        resolution_service=resolution_service,
    )
    decomposition_service = DeterministicDecompositionService(acquisition_service)
    return DecompositionPublicApi(decomposition_service)


def build_demo_member_access_public_api() -> MemberAccessPublicApi:
    catalog = _build_demo_normalized_catalog()
    resolution_service = ExactMatchResolutionService(catalog)
    acquisition_service = DeterministicAcquisitionService(
        catalog,
        resolution_service=resolution_service,
    )
    decomposition_service = DeterministicDecompositionService(acquisition_service)
    member_access_service = DeterministicMemberAccessService(
        acquisition_service,
        decomposition_service,
    )
    return MemberAccessPublicApi(member_access_service)


def build_demo_representation_selection_public_api() -> RepresentationSelectionPublicApi:
    catalog = _build_demo_normalized_catalog()
    resolution_service = ExactMatchResolutionService(catalog)
    representations_service = DeterministicRepresentationsService(
        catalog,
        resolution_service=resolution_service,
    )
    compatibility_service = DeterministicCompatibilityService(
        catalog,
        resolution_service=resolution_service,
    )
    handoff_service = DeterministicRepresentationSelectionService(
        catalog,
        resolution_service=resolution_service,
        representations_service=representations_service,
        compatibility_service=compatibility_service,
    )
    return RepresentationSelectionPublicApi(handoff_service)


def build_demo_resolution_actions_public_api() -> ResolutionActionsPublicApi:
    catalog = _build_demo_normalized_catalog()
    manifest_service = ResolutionManifestExportService(catalog)
    bundle_service = ResolutionBundleExportService(catalog)
    return ResolutionActionsPublicApi(
        manifest_service=manifest_service,
        bundle_service=bundle_service,
    )


def build_demo_resolution_bundle_inspection_public_api() -> ResolutionBundleInspectionPublicApi:
    inspection_service = ResolutionBundleInspectionEngineService()
    return ResolutionBundleInspectionPublicApi(inspection_service)


def build_demo_stored_exports_public_api(store_root: str) -> StoredExportsPublicApi:
    catalog = _build_demo_normalized_catalog()
    manifest_service = ResolutionManifestExportService(catalog)
    bundle_service = ResolutionBundleExportService(catalog)
    store_service = ResolutionExportStoreEngineService(
        manifest_service=manifest_service,
        bundle_service=bundle_service,
        store=LocalExportStore(store_root),
    )
    return StoredExportsPublicApi(store_service)


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


def _build_demo_resolution_run_service(run_store_root: str) -> LocalResolutionRunService:
    catalog = _build_demo_normalized_catalog()
    source_registry = load_source_registry()
    resolution_service = ExactMatchResolutionService(catalog)
    search_service = DeterministicSearchService(catalog)
    absence_service = DeterministicAbsenceService(
        catalog,
        resolution_service=resolution_service,
        search_service=search_service,
    )
    return LocalResolutionRunService(
        catalog=catalog,
        source_registry=source_registry,
        resolution_service=resolution_service,
        search_service=search_service,
        absence_service=absence_service,
        run_store=LocalResolutionRunStore(run_store_root),
        query_planner=DeterministicQueryPlannerService(),
    )
