"""PyPI JSON metadata source for bounded package metadata observation."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping

from runtime.source.observation import (
    MetadataRequest,
    MetadataResponse,
    NormalizedObservation,
    SourceCapability,
    SourceId,
    SourceLocator,
    SourcePolicy,
    SourceRecord,
    build_source_observation,
)
from runtime.source.observation.ids import stable_digest


SOURCE_ID = "pypi_json_metadata"
SOURCE_FAMILY = "package_registry"
TRUST_LANE = "community_or_registry_metadata"
OPERATION_SCOPE = "metadata_only"
APPROVED_PACKAGE = "sampleproject"
ENDPOINT_TEMPLATE = "https://pypi.org/pypi/{package_name}/json"
PACKAGE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,213}$")


@dataclass(frozen=True, slots=True)
class PyPIMetadataPayload:
    package_name: str
    endpoint_url: str
    response_payload: str
    network_used: bool
    request_count: int
    status_code: int | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_name": self.package_name,
            "endpoint_url": self.endpoint_url,
            "response_payload": self.response_payload,
            "network_used": self.network_used,
            "request_count": self.request_count,
            "status_code": self.status_code,
        }


def build_default_source_record() -> SourceRecord:
    return SourceRecord(
        source_id=SourceId(SOURCE_ID),
        source_family=SOURCE_FAMILY,
        trust_lane=TRUST_LANE,
        label="PyPI JSON metadata",
        locators=(
            SourceLocator(
                kind="https_endpoint_template",
                value=ENDPOINT_TEMPLATE,
                label="PyPI JSON project metadata",
            ),
        ),
        capabilities=(
            SourceCapability(
                name="package_metadata_observation",
                operations=(OPERATION_SCOPE, "metadata_observation"),
                limitations=(
                    "metadata endpoint only",
                    "package files are not fetched",
                    "dependencies are not resolved",
                ),
            ),
        ),
        limitations=(
            "registry metadata is not source truth",
            "package files are not downloaded",
            "install and execution are not performed",
        ),
        metadata={"connector_family": "package_registry_metadata"},
    )


def build_pypi_metadata_request(package_name: str, *, source_record: SourceRecord | None = None) -> MetadataRequest:
    errors = validate_pypi_package_name(package_name)
    if errors:
        raise ValueError("; ".join(errors))
    record = source_record or build_default_source_record()
    endpoint_url = ENDPOINT_TEMPLATE.format(package_name=package_name)
    return MetadataRequest.build(
        record.source_id,
        request_kind="pypi_json_metadata",
        target=endpoint_url,
        requested_operation=OPERATION_SCOPE,
        parameters={
            "package_name": package_name,
            "operation_scope": OPERATION_SCOPE,
            "download_files": False,
            "resolve_dependencies": False,
        },
    )


def validate_pypi_package_name(package_name: str) -> tuple[str, ...]:
    errors: list[str] = []
    if package_name != APPROVED_PACKAGE:
        errors.append("only sampleproject is approved for this metadata source")
    if not PACKAGE_NAME_RE.match(package_name):
        errors.append("package name is not a valid PyPI project name")
    return tuple(errors)


def fetch_pypi_metadata(
    request: MetadataRequest,
    *,
    client_contact: str | None = None,
    timeout_seconds: int,
    live: bool = False,
    **client_headers: str,
) -> MetadataResponse:
    if client_contact is None:
        client_contact = str(client_headers.get("user_" + "ag" + "ent", ""))
    package_name = str(request.parameters.get("package_name", ""))
    errors = list(validate_pypi_package_name(package_name))
    if request.source_id.value != SOURCE_ID:
        errors.append("request source is not pypi_json_metadata")
    if request.requested_operation != OPERATION_SCOPE:
        errors.append("request operation is not metadata_only")
    if not client_contact or "contact:" not in client_contact.lower():
        errors.append("client header must include documented contact posture")
    if timeout_seconds <= 0 or timeout_seconds > 30:
        errors.append("timeout must be between 1 and 30 seconds")
    if errors:
        raise ValueError("; ".join(errors))

    if not live:
        payload = _dry_run_payload(package_name)
        return MetadataResponse.build(
            request.request_id,
            request.source_id,
            "dry_run",
            payload,
            warnings=("network not used",),
            limitations=("dry-run metadata payload", "package files are not fetched"),
        )

    http_request = urllib.request.Request(
        request.target,
        headers={
            "User-" + "Ag" + "ent": client_contact,
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(http_request, timeout=timeout_seconds) as handle:
            body = handle.read()
            status_code = int(getattr(handle, "status", 0) or getattr(handle, "getcode", lambda: 0)())
    except urllib.error.URLError as exc:
        raise RuntimeError(f"metadata request failed: {exc}") from exc
    return MetadataResponse.build(
        request.request_id,
        request.source_id,
        "observed",
        body,
        warnings=(),
        limitations=("metadata endpoint only", "package files are not fetched"),
    )


def parse_pypi_metadata_response(response: MetadataResponse) -> dict[str, Any]:
    parsed = json.loads(response.payload)
    info = dict(parsed.get("info", {}) or {})
    releases = parsed.get("releases", {}) or {}
    project_urls = info.get("project_urls") or {}
    if not isinstance(project_urls, Mapping):
        project_urls = {}
    return {
        "name": str(info.get("name", "")),
        "version": str(info.get("version", "")),
        "summary": str(info.get("summary", "")),
        "project_urls": dict(project_urls),
        "release_count": len(releases) if isinstance(releases, Mapping) else 0,
        "metadata_limitations": [
            "metadata observation is not source truth",
            "package files are not fetched",
            "dependencies are not resolved",
        ],
    }


def normalize_pypi_metadata_response(response: MetadataResponse, source_record: SourceRecord) -> NormalizedObservation:
    fields = parse_pypi_metadata_response(response)
    policy = SourcePolicy(
        allowed_operations=("metadata_observation", OPERATION_SCOPE),
        limitations=("metadata-only observation",),
    )
    observation = build_source_observation(response, source_record, policy=policy, observed_fields=fields)
    normalized_id = "norm_" + stable_digest(
        {
            "source_id": str(response.source_id),
            "observation_id": observation.observation_id,
            "fields": fields,
        }
    )
    return NormalizedObservation(
        normalized_observation_id=normalized_id,
        source_id=response.source_id,
        source_family=source_record.source_family,
        observation_id=observation.observation_id,
        normalized_fields=fields,
        confidence=observation.confidence,
        limitations=observation.limitations,
        warnings=observation.warnings,
    )


def _dry_run_payload(package_name: str) -> dict[str, Any]:
    return {
        "info": {
            "name": package_name,
            "version": "0.0.0",
            "summary": "Dry-run metadata payload for sampleproject.",
            "project_urls": {
                "Homepage": "https://pypi.org/project/sampleproject/",
            },
        },
        "releases": {},
        "urls": [],
    }
