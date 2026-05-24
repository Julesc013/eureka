from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from runtime.source.action.action_kernel import (
    CREATED_AT,
    build_source_action_boundary_report,
    build_source_action_scorecard,
    register_source_action_adapter,
    reset_source_action_registry_for_tests,
    run_source_action,
    stable_id,
)


REQUIRED_SOURCE_WAVE_FAMILIES = (
    "internet_archive_metadata_v2",
    "wayback_cdx_metadata",
    "github_releases_metadata",
    "software_heritage_metadata",
    "package_registry_metadata",
    "open_library_metadata",
    "wikidata_metadata",
    "manual_source_pack",
)

OPTIONAL_DESCRIPTOR_ONLY_FAMILIES = (
    "pypi_metadata",
    "npm_metadata",
    "crates_io_metadata",
    "nuget_metadata",
    "maven_metadata",
)


@dataclass(frozen=True)
class SourceWaveFamily:
    source_family: str
    display_name: str
    adapter_id: str
    capabilities: tuple[str, ...]
    example_path: str
    future_live_task: str
    best_for_domains: tuple[str, ...]
    known_failure_modes: tuple[str, ...]


SOURCE_WAVE_FAMILIES: dict[str, SourceWaveFamily] = {
    "internet_archive_metadata_v2": SourceWaveFamily(
        source_family="internet_archive_metadata_v2",
        display_name="Internet Archive Metadata v2",
        adapter_id="internet_archive_metadata_v2_adapter",
        capabilities=("metadata_search", "item_metadata_read", "file_manifest_metadata"),
        example_path="examples/sources/internet_archive_metadata",
        future_live_task="SOURCE-WAVE-IA-METADATA-V2-LIVE-GATE",
        best_for_domains=("archived software metadata", "item manifests", "collection metadata"),
        known_failure_modes=("ambiguous item identity", "sparse metadata", "collection noise"),
    ),
    "wayback_cdx_metadata": SourceWaveFamily(
        source_family="wayback_cdx_metadata",
        display_name="Wayback CDX Metadata",
        adapter_id="wayback_cdx_metadata_adapter",
        capabilities=("capture_availability_lookup",),
        example_path="examples/sources/wayback_cdx",
        future_live_task="SOURCE-WAVE-WAYBACK-CDX-LIVE-GATE",
        best_for_domains=("archived URL availability", "support-page traces"),
        known_failure_modes=("URL canonicalization drift", "capture gaps", "robots exclusions"),
    ),
    "github_releases_metadata": SourceWaveFamily(
        source_family="github_releases_metadata",
        display_name="GitHub Releases Metadata",
        adapter_id="github_releases_metadata_adapter",
        capabilities=("release_metadata_read",),
        example_path="examples/sources/github_releases",
        future_live_task="SOURCE-WAVE-GITHUB-RELEASES-LIVE-GATE",
        best_for_domains=("release identity", "asset metadata", "version lineage"),
        known_failure_modes=("renamed repositories", "deleted assets", "rate limits"),
    ),
    "software_heritage_metadata": SourceWaveFamily(
        source_family="software_heritage_metadata",
        display_name="Software Heritage Metadata",
        adapter_id="software_heritage_metadata_adapter",
        capabilities=("origin_metadata_read",),
        example_path="examples/sources/software_heritage",
        future_live_task="SOURCE-WAVE-SWH-LIVE-GATE",
        best_for_domains=("source origin traces", "revision identity", "archive provenance"),
        known_failure_modes=("origin aliases", "missing releases", "snapshot lag"),
    ),
    "package_registry_metadata": SourceWaveFamily(
        source_family="package_registry_metadata",
        display_name="Package Registry Metadata",
        adapter_id="package_registry_metadata_adapter",
        capabilities=("package_metadata_read",),
        example_path="examples/sources/package_registries",
        future_live_task="SOURCE-WAVE-PACKAGE-REGISTRY-LIVE-GATE",
        best_for_domains=("package versions", "ecosystem identifiers", "release metadata"),
        known_failure_modes=("namespace squatting", "registry-specific semantics", "yanked versions"),
    ),
    "open_library_metadata": SourceWaveFamily(
        source_family="open_library_metadata",
        display_name="Open Library Metadata",
        adapter_id="open_library_metadata_adapter",
        capabilities=("bibliographic_metadata_read",),
        example_path="examples/sources/open_library",
        future_live_task="SOURCE-WAVE-OPEN-LIBRARY-LIVE-GATE",
        best_for_domains=("manuals", "books", "bibliographic identity"),
        known_failure_modes=("edition ambiguity", "metadata sparsity", "duplicate works"),
    ),
    "wikidata_metadata": SourceWaveFamily(
        source_family="wikidata_metadata",
        display_name="Wikidata Metadata",
        adapter_id="wikidata_metadata_adapter",
        capabilities=("entity_metadata_read",),
        example_path="examples/sources/wikidata",
        future_live_task="SOURCE-WAVE-WIKIDATA-LIVE-GATE",
        best_for_domains=("entity identity", "external identifiers", "relation hints"),
        known_failure_modes=("entity ambiguity", "stale claims", "weak source statements"),
    ),
    "manual_source_pack": SourceWaveFamily(
        source_family="manual_source_pack",
        display_name="Manual Source Pack",
        adapter_id="manual_source_pack_adapter",
        capabilities=("source_pack_replay", "fixture_replay"),
        example_path="examples/sources/manual_source_pack",
        future_live_task="SOURCE-WAVE-MANUAL-PACK-IMPORT-GATE",
        best_for_domains=("curated source leads", "offline evidence packets", "operator-reviewed packs"),
        known_failure_modes=("pack schema drift", "operator transcription errors", "stale references"),
    ),
}


class SourceWaveAdapter:
    def __init__(self, family: SourceWaveFamily) -> None:
        self.family = family
        self.adapter_id = family.adapter_id
        self.source_family = family.source_family
        self.supported_action_kinds = family.capabilities
        self.supported_transport_modes = ("fixture", "mock_live")

    def manifest(self) -> dict[str, Any]:
        return build_source_family_manifest(self.family)

    def run_fixture(self, plan: Mapping[str, Any]) -> dict[str, Any]:
        query = str(plan.get("query_context", {}).get("query", "sampleproject"))
        action_kind = str(plan.get("action_kind", self.family.capabilities[0]))
        return {"records": [source_wave_fixture_record(self.family, action_kind, query, "fixture")]}

    def run_mock(self, plan: Mapping[str, Any]) -> dict[str, Any]:
        query = str(plan.get("query_context", {}).get("query", "sampleproject"))
        action_kind = str(plan.get("action_kind", self.family.capabilities[0]))
        return {"records": [source_wave_fixture_record(self.family, action_kind, query, "mock_live")]}

    def normalize(self, transport_result: Mapping[str, Any]) -> dict[str, Any]:
        observations: list[dict[str, Any]] = []
        for record in transport_result.get("records", []):
            observations.append(
                {
                    "observation_id": stable_id("source_wave_observation", record.get("source_record_id")),
                    "source_family": self.source_family,
                    "title": record.get("title"),
                    "summary": record.get("summary"),
                    "source_locator": record.get("source_locator"),
                    "identifiers": record.get("identifiers", {}),
                    "provenance": {
                        "transport_mode": transport_result.get("transport_mode"),
                        "fixture": True,
                        "raw_response_persisted": False,
                    },
                    "confidence": "metadata_fixture",
                }
            )
        return {"observations": observations}


def build_source_family_manifest(family: SourceWaveFamily | str) -> dict[str, Any]:
    payload = SOURCE_WAVE_FAMILIES[family] if isinstance(family, str) else family
    fixture_refs = [f"{payload.example_path}/source_family_descriptor.json"]
    return {
        "schema_version": "source_family_manifest.v0",
        "record_type": "source_family_manifest",
        "created_at": CREATED_AT,
        "source_family": payload.source_family,
        "display_name": payload.display_name,
        "source_family_version": "0.0",
        "manifest_version": "0.0",
        "adapter_id": payload.adapter_id,
        "supported_capabilities": list(payload.capabilities),
        "supported_action_kinds": list(payload.capabilities),
        "supported_transport_modes": ["fixture", "mock_live"],
        "capability_profile_ref": "contracts/source/action/source_capability_profile.v0.json",
        "policy_ref": "control/policies/source_wave_policy.json",
        "fixture_refs": fixture_refs,
        "mock_refs": fixture_refs,
        "live_policy_required": True,
        "default_enabled": False,
        "live_enabled_default": False,
        "public_fanout_allowed": False,
        "public_fanout_allowed_default": False,
        "downloads_allowed": False,
        "extraction_allowed": False,
        "evidence_acceptance_allowed": False,
        "reviewed_record_creation_allowed": False,
        "review_required": True,
        "scorecard_required": True,
        "boundary_report_required": True,
        "future_live_task": payload.future_live_task,
        "source_action_id": stable_id("source_wave_manifest", payload.source_family),
        "projection_profile": "operator_workbench",
        "dry_run": True,
        "live_call_performed": False,
        "accepted_truth": False,
        "limitations": ["metadata_fixture_or_mock_only", "not_truth"],
        "non_claims": source_wave_non_claims(),
    }


def build_optional_descriptor(source_family: str) -> dict[str, Any]:
    display_name = source_family.replace("_", " ").title()
    return {
        "schema_version": "source_family_manifest.v0",
        "record_type": "source_family_manifest",
        "created_at": CREATED_AT,
        "source_family": source_family,
        "display_name": display_name,
        "source_family_version": "0.0",
        "adapter_id": f"{source_family}_descriptor_only",
        "supported_capabilities": ["package_metadata_read"],
        "supported_transport_modes": ["fixture"],
        "fixture_refs": [],
        "mock_refs": [],
        "live_enabled_default": False,
        "public_fanout_allowed_default": False,
        "downloads_allowed": False,
        "extraction_allowed": False,
        "evidence_acceptance_allowed": False,
        "reviewed_record_creation_allowed": False,
        "scorecard_required": True,
        "boundary_report_required": True,
        "future_live_task": "SOURCE-WAVE-OPTIONAL-PACKAGE-SPLIT",
        "limitations": ["descriptor_only_in_source_wave_00"],
        "non_claims": source_wave_non_claims(),
    }


def build_source_wave_adapter(source_family: str) -> SourceWaveAdapter:
    return SourceWaveAdapter(SOURCE_WAVE_FAMILIES[source_family])


def register_source_wave_adapters(*, reset: bool = False) -> list[dict[str, Any]]:
    if reset:
        reset_source_action_registry_for_tests()
    registrations = []
    for source_family in REQUIRED_SOURCE_WAVE_FAMILIES:
        registrations.append(register_source_action_adapter(build_source_wave_adapter(source_family)))
    return registrations


def list_registered_source_families() -> list[str]:
    return list(REQUIRED_SOURCE_WAVE_FAMILIES)


def get_source_family_manifest(source_family: str) -> dict[str, Any]:
    return build_source_family_manifest(source_family)


def run_source_family_fixture_action(
    source_family: str,
    action_kind: str,
    query_context: str | Mapping[str, Any],
    *,
    transport: str = "fixture",
) -> dict[str, Any]:
    if source_family not in SOURCE_WAVE_FAMILIES:
        raise KeyError(f"unknown source wave family: {source_family}")
    register_source_wave_adapters(reset=True)
    query = query_context.get("query", "") if isinstance(query_context, Mapping) else query_context
    return run_source_action(
        query=str(query),
        source_family=source_family,
        action_kind=action_kind,
        transport_mode=transport,
        dry_run=True,
    )


def build_source_wave_mapping_plan(source_family: str, fixture_result: Mapping[str, Any]) -> dict[str, Any]:
    del source_family
    return dict(fixture_result.get("candidate_mapping_plan") or {})


def build_source_wave_scorecard(source_family: str) -> dict[str, Any]:
    family = SOURCE_WAVE_FAMILIES[source_family]
    scorecard = build_source_action_scorecard(source_family, [{"fixture": family.source_family}])
    scorecard["dimensions"].update(
        {
            "false_positive_risk": "medium-fixture-unmeasured",
            "rights_risk": "metadata-only-not-assessed",
            "safety_risk": "low-fixture-only",
            "rate_limit_risk": "future-live-gated",
            "best_for_domains": list(family.best_for_domains),
            "known_failure_modes": list(family.known_failure_modes),
            "next_validation_task": family.future_live_task,
        }
    )
    return scorecard


def build_source_wave_boundary_report(source_family: str, action_result: Mapping[str, Any]) -> dict[str, Any]:
    report = build_source_action_boundary_report(action_result)
    report["source_family"] = source_family
    report["source_wave"] = "SOURCE-WAVE-00"
    return report


def smoke_source_wave_families(
    families: Sequence[str] = REQUIRED_SOURCE_WAVE_FAMILIES,
    *,
    transport: str = "fixture",
) -> dict[str, Any]:
    runs = []
    for source_family in families:
        family = SOURCE_WAVE_FAMILIES[source_family]
        runs.append(
            run_source_family_fixture_action(
                source_family,
                family.capabilities[0],
                "sampleproject",
                transport=transport,
            )
        )
    return {
        "schema_version": "source_wave_smoke_result.v0",
        "task": "AIDE-BATCH-SOURCE-WAVE-00",
        "status": "pass" if all(run.get("status") == "completed" for run in runs) else "fail",
        "family_count": len(runs),
        "families": [run.get("source_family") for run in runs],
        "runs": runs,
        "live_source_call_performed": False,
        "source_probe_executed": False,
        "raw_live_source_response_committed": False,
        "source_cache_write_performed": False,
        "evidence_write_performed": False,
        "candidate_index_mutated": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "operator_instance_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def source_wave_fixture_record(
    family: SourceWaveFamily,
    action_kind: str,
    query: str,
    transport_mode: str,
) -> dict[str, Any]:
    normalized_query = " ".join(query.strip().lower().split()) or "sampleproject"
    return {
        "source_record_id": stable_id("source_wave_record", family.source_family, action_kind, normalized_query),
        "source_family": family.source_family,
        "action_kind": action_kind,
        "title": f"{family.display_name} fixture for {normalized_query}",
        "summary": "Deterministic metadata-only source wave fixture. This is a candidate input, not truth.",
        "source_locator": f"fixture://{family.source_family}/{stable_id('locator', action_kind, normalized_query)}",
        "identifiers": {
            "query": normalized_query,
            "capability": action_kind,
            "source_family": family.source_family,
            "fixture_key": stable_id("fixture", family.source_family, action_kind),
        },
        "transport_mode": transport_mode,
        "live_call_performed": False,
        "accepted_truth": False,
        "review_required": True,
    }


def source_wave_non_claims() -> list[str]:
    return [
        "not_truth",
        "not_evidence_acceptance",
        "not_reviewed_record_creation",
        "not_store_mutation",
        "not_public_live_fanout",
        "not_download_or_extraction",
        "not_production_or_public_launch_readiness",
    ]
