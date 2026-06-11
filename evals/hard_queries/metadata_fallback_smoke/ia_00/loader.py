from __future__ import annotations

import json
from pathlib import Path
import tempfile
from typing import Any, Mapping

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
from runtime.engine.interfaces.public import DeterministicSearchRunRequest
from runtime.engine.resolve import DeterministicSearchService, ExactMatchResolutionService
from runtime.engine.resolution_runs import (
    LocalResolutionRunService,
    LocalResolutionRunStore,
    ResolutionRunFallbackPolicy,
)
from runtime.source.observation.archive_org_public_metadata import ArchiveOrgMetadataCandidateProvider
from runtime.source.observation.internet_archive_live_transport import (
    IALiveTransportPolicy,
    IALiveTransportResponse,
)
from runtime.source.registry import load_source_registry
from runtime.surface import SurfaceKernel, SurfaceRequest


REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_PATH = Path(__file__).with_name("ia_metadata_fixtures.json")
EXPECTED_PATH = Path(__file__).with_name("expected_fallback_outputs.json")
BASELINE_PROFILES = ("json_v0", "text_v0", "html_basic_v0", "snapshot_v0")
TASK_ID = "IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00"


def load_fixture_payload(path: Path = FIXTURE_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_expected_outputs(path: Path = EXPECTED_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_smoke_suite() -> dict[str, Any]:
    fixture_payload = load_fixture_payload()
    catalog = _build_demo_normalized_catalog()
    cases: dict[str, Any] = {}
    with tempfile.TemporaryDirectory() as temp_root:
        for case in fixture_payload["cases"]:
            case_id = str(case["case_id"])
            provider = provider_for_case(case_id, fixture_payload)
            policy = policy_for_case(case_id)
            service = _build_service(catalog, temp_root, fallback_provider=provider, fallback_policy=policy)
            run = service.run_deterministic_search(DeterministicSearchRunRequest.from_parts(str(case["query_text"])))
            projections = {
                profile: SurfaceKernel().project(
                    SurfaceRequest(
                        route_id="resolution_run",
                        payload=run,
                        requested_profile=profile,
                        visibility_posture="public",
                        data_version="ia-metadata-smoke-v0",
                    )
                )
                for profile in BASELINE_PROFILES
            }
            fallback = dict(run.fallback_summary or {})
            cases[case_id] = {
                "schema_version": "ia_metadata_fallback_smoke_case_result.v0",
                "case_id": case_id,
                "query_text": case["query_text"],
                "run": run.to_dict(),
                "fallback_summary": fallback,
                "surface_projections": projections,
                "provider_call_count": provider_call_count(provider),
                "truth_boundary": truth_boundary(fallback),
            }
    return {
        "schema_version": "ia_metadata_fallback_smoke_suite.v0",
        "task_id": TASK_ID,
        "profiles": list(BASELINE_PROFILES),
        "cases": cases,
        "live_network_required": False,
        "downloads_performed": False,
        "file_fetching_performed": False,
        "wayback_replay_performed": False,
        "reviewed_artifact_records_created": 0,
        "verified_artifacts_created": 0,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def provider_for_case(case_id: str, fixture_payload: Mapping[str, Any]):
    case = _case_by_id(case_id, fixture_payload)
    mode = str(case["fixture_mode"])
    if mode == "near_miss":
        return FixtureBackedIAMetadataProvider(result=_near_miss_result(case))
    calls: list[str] = []
    provider = ArchiveOrgMetadataCandidateProvider(
        rows=3,
        transport_factory=lambda _policy: FixtureArchiveTransport(case, calls),
    )
    object.__setattr__(provider, "calls", calls)
    return provider


def policy_for_case(case_id: str) -> ResolutionRunFallbackPolicy:
    if case_id == "policy_blocked_disabled":
        return ResolutionRunFallbackPolicy(enabled=False)
    if case_id == "policy_blocked_source_disabled":
        return ResolutionRunFallbackPolicy(enabled=True, disabled_source_families=("internet_archive",))
    if case_id == "policy_blocked_not_allowlisted":
        return ResolutionRunFallbackPolicy(enabled=True, allowed_source_families=("software_heritage",))
    return ResolutionRunFallbackPolicy(enabled=True, allowed_source_families=("internet_archive",), candidate_limit=3)


def provider_call_count(provider: Any) -> int:
    if hasattr(provider, "calls"):
        return len(provider.calls)
    cache = getattr(provider, "_cache", {})
    return 1 if cache else 0


def truth_boundary(fallback: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "accepted_truth": bool(fallback.get("accepted_truth")),
        "verified": bool(fallback.get("verified")),
        "reviewed_record_created": bool(fallback.get("reviewed_record_created")),
        "reviewed_index_mutated": bool(fallback.get("reviewed_index_mutated")),
        "public_index_mutated": bool(fallback.get("public_index_mutated")),
        "master_index_mutated": bool(fallback.get("master_index_mutated")),
        "download_performed": bool((fallback.get("source_observation") or {}).get("download_performed")),
    }


class FixtureArchiveTransport:
    def __init__(self, case: Mapping[str, Any], calls: list[str]) -> None:
        self.case = dict(case)
        self.calls = calls
        self.request_count = 0

    def get_json(self, **kwargs: object) -> IALiveTransportResponse:
        self.request_count += 1
        self.calls.append(str(kwargs.get("url", "")))
        mode = str(self.case["fixture_mode"])
        if mode == "timeout":
            return _response(kwargs, status_code=0, body="", transport_error="timeout")
        if mode == "malformed":
            return _response(kwargs, status_code=200, body="{not-json")
        docs = self.case.get("docs") if isinstance(self.case.get("docs"), list) else []
        if mode == "empty":
            docs = []
        body = json.dumps({"response": {"numFound": len(docs), "docs": docs}}, sort_keys=True)
        return _response(kwargs, status_code=200, body=body)


class FixtureBackedIAMetadataProvider:
    source_id = "internet_archive_metadata"
    source_family = "internet_archive"

    def __init__(self, *, result: Mapping[str, Any]) -> None:
        self._result = dict(result)
        self.calls: list[tuple[str, int]] = []

    def search_metadata_candidates(self, query: str, limit: int) -> dict[str, Any]:
        self.calls.append((query, limit))
        result = dict(self._result)
        result["query"] = query
        result["candidate_count"] = 0
        result["candidates"] = []
        result["total_http_requests"] = 0
        return result


def _response(
    kwargs: Mapping[str, object],
    *,
    status_code: int,
    body: str,
    transport_error: str = "",
) -> IALiveTransportResponse:
    return IALiveTransportResponse(
        url=str(kwargs.get("url", "https://archive.org/advancedsearch.php")),
        endpoint_class=str(kwargs.get("endpoint_class", "archive_org_metadata_search")),
        status_code=status_code,
        elapsed_ms=3,
        response_byte_count=len(body.encode("utf-8")),
        content_sha256="0" * 64,
        safe_headers={"content-type": "application/json"} if status_code else {},
        body_text=body,
        transport_error=transport_error,
    )


def _near_miss_result(case: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "archive_org_metadata_candidate_search.v0",
        "status": "near_miss",
        "source_id": "internet_archive_metadata",
        "source_family": "internet_archive",
        "source_label": "Internet Archive metadata search fixture",
        "failure_reason": "metadata_near_miss",
        "live_call_performed": False,
        "metadata_request_performed": True,
        "accepted_truth": False,
        "review_required": True,
        "limitations": ["archive_org_metadata_only", "candidate_not_reviewed_truth", "no_download"],
        "warnings": [str(case.get("near_miss_reason", "metadata near miss requires review"))],
    }


def _case_by_id(case_id: str, fixture_payload: Mapping[str, Any]) -> Mapping[str, Any]:
    for case in fixture_payload.get("cases", []) or []:
        if isinstance(case, Mapping) and case.get("case_id") == case_id:
            return case
    raise KeyError(case_id)


def _build_service(
    catalog: NormalizedCatalog,
    root: str,
    *,
    fallback_provider,
    fallback_policy: ResolutionRunFallbackPolicy,
) -> LocalResolutionRunService:
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
        fallback_provider=fallback_provider,
        fallback_policy=fallback_policy,
        timestamp_factory=lambda: "2026-06-12T00:00:00+10:00",
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
