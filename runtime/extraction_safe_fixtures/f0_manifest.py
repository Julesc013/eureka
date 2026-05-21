"""Read-only F0 fixture manifest helpers.

This module is intentionally narrow: it lists committed fixture metadata and ZIP
directory entries, then emits candidate member manifests. It never extracts,
executes, downloads, or writes archive contents.
"""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re
import tempfile
from typing import Any, Mapping, Sequence
from zipfile import ZipFile


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXED_CREATED_AT = "2026-05-22T00:00:00Z"

PROJECTION_PROFILES: tuple[str, ...] = (
    "operator_workbench",
    "public_web",
    "native_desktop_read_only",
)

REQUIRED_FIXTURE_IDS: tuple[str, ...] = (
    "safe_zip_basic",
    "safe_zip_nested_directory",
    "unsafe_zip_path_traversal_manifest_fixture",
    "unsafe_zip_absolute_path_manifest_fixture",
    "large_member_declared_size_manifest_fixture",
    "future_iso_blocked_fixture_descriptor",
    "future_archive_member_query_fixture",
)

BLOCKED_ACTIONS: tuple[str, ...] = (
    "download",
    "upload",
    "filesystem_extract",
    "arbitrary_file_extract",
    "execute",
    "install",
    "emulate",
    "call_model_provider",
    "write_source_cache",
    "write_evidence",
    "write_candidate_index",
    "write_review_queue",
    "mutate_master_index",
    "mutate_operator_instance",
    "deploy",
)

DEFAULT_RESOURCE_LIMITS: dict[str, Any] = {
    "max_fixture_file_size_bytes": 1048576,
    "max_member_count": 100,
    "max_declared_total_size_bytes": 10485760,
    "max_uncompressed_total_size_bytes": 10485760,
    "max_nested_depth": 1,
    "max_filename_length": 240,
    "timeout_seconds": 10,
    "memory_budget_mb": 64,
}

NESTED_CONTAINER_SUFFIXES = (
    ".zip",
    ".tar",
    ".tgz",
    ".tar.gz",
    ".7z",
    ".rar",
    ".iso",
    ".dmg",
    ".cab",
    ".msi",
)


class F0ManifestError(ValueError):
    """Raised when an F0 fixture manifest cannot be safely used."""


def load_f0_fixture_manifest(path: str | Path) -> dict[str, Any]:
    """Load the F0 fixture manifest from disk."""
    return _load_json(_resolve_path(path))


def validate_f0_fixture_manifest(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the committed F0 fixture manifest."""
    errors: list[str] = []
    if record.get("schema_version") != "f0_fixture_manifest.v0":
        errors.append("f0_fixture_manifest: schema_version must be f0_fixture_manifest.v0.")
    if record.get("fixture_status") != "example_only":
        errors.append("f0_fixture_manifest: fixture_status must be example_only.")
    non_claims = _mapping(record.get("non_claims"))
    for flag in (
        "fake_evidence_created",
        "fake_verified_records_created",
        "live_source_call_performed",
        "download_performed",
        "filesystem_extraction_performed",
        "arbitrary_file_extraction_performed",
        "execution_performed",
        "master_index_mutated",
    ):
        if non_claims.get(flag) is not False:
            errors.append(f"f0_fixture_manifest: non_claims.{flag} must be false.")
    fixture_ids = {str(item.get("fixture_id", "")) for item in _list(record.get("fixtures")) if isinstance(item, Mapping)}
    missing = set(REQUIRED_FIXTURE_IDS) - fixture_ids
    if missing:
        errors.append(f"f0_fixture_manifest: missing fixture ids {sorted(missing)}.")
    return {
        "schema_version": "f0_fixture_manifest_validation_report.v0",
        "status": "valid" if not errors else "invalid",
        "fixture_count": len(fixture_ids),
        "fixture_ids": sorted(fixture_ids),
        "errors": errors,
    }


def build_container_descriptor_from_fixture(path_or_descriptor: str | Path | Mapping[str, Any]) -> dict[str, Any]:
    """Build a container descriptor from a safe path or descriptor object."""
    if isinstance(path_or_descriptor, Mapping):
        descriptor = dict(path_or_descriptor)
        descriptor.setdefault("schema_version", "container_descriptor.v0")
        descriptor.setdefault("record_type", "container_descriptor")
        descriptor.setdefault("created_at", FIXED_CREATED_AT)
        descriptor.setdefault("source_context", {"source_kind": "f0_safe_fixture_descriptor"})
        descriptor.setdefault("domain_id", descriptor.get("domain_id", "legacy_software"))
        descriptor.setdefault("review_required", True)
        descriptor.setdefault("accepted_truth", False)
        descriptor.setdefault("limitations", ["descriptor-only example; no extraction performed"])
        descriptor.setdefault("risk_flags", [])
        descriptor.setdefault("rights_flags", [])
        descriptor.setdefault("non_claims", _default_non_claims())
        return descriptor

    path = _resolve_allowed_fixture_path(path_or_descriptor)
    suffix = path.suffix.lower()
    if suffix == ".zip":
        container_kind = "zip_fixture_manifest"
    elif suffix == ".tar":
        container_kind = "tar_fixture_manifest"
    elif path.is_dir():
        container_kind = "directory_manifest_fixture"
    else:
        container_kind = "unknown_binary_container"
    return {
        "schema_version": "container_descriptor.v0",
        "record_type": "container_descriptor",
        "container_id": f"f0_container_{path.stem}",
        "fixture_id": path.stem,
        "container_kind": container_kind,
        "locator": _repo_relative(path),
        "source_context": {"source_kind": "repo_committed_fixture", "path": _repo_relative(path)},
        "domain_id": "legacy_software",
        "review_required": True,
        "accepted_truth": False,
        "limitations": ["fixture-only descriptor; member manifest may be enumerated without extraction"],
        "risk_flags": [],
        "rights_flags": [],
        "non_claims": _default_non_claims(),
        "created_at": FIXED_CREATED_AT,
    }


def enumerate_safe_zip_manifest(zip_path: str | Path, policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Enumerate ZIP directory metadata without extracting members."""
    limits = _limits(policy)
    path = _resolve_allowed_fixture_path(zip_path)
    if path.stat().st_size > int(limits["max_fixture_file_size_bytes"]):
        raise F0ManifestError(f"{_repo_relative(path)} exceeds max_fixture_file_size_bytes")
    members: list[dict[str, Any]] = []
    with ZipFile(path) as archive:
        for index, info in enumerate(archive.infolist()):
            members.append(_member_record_from_path(
                manifest_id=f"f0_member_manifest_{path.stem}",
                member_id=f"f0_member_{path.stem}_{index + 1}",
                path_text=info.filename,
                declared_size=info.file_size,
                is_directory=info.is_dir(),
                compression_method= str(info.compress_type),
                checksum=f"{info.CRC:08x}",
                is_symlink=_zip_info_is_symlink(info),
                policy=policy,
            ))
    return members


def build_member_manifest(container_descriptor: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a manifest-only member manifest for a fixture descriptor."""
    descriptor = dict(container_descriptor)
    container_kind = str(descriptor.get("container_kind", "unknown_binary_container"))
    fixture_id = str(descriptor.get("fixture_id", "unknown_fixture"))
    container_id = str(descriptor.get("container_id", f"f0_container_{fixture_id}"))
    manifest_id = f"f0_member_manifest_{fixture_id}"
    limits = _limits(policy)

    if container_kind == "zip_fixture_manifest":
        members = enumerate_safe_zip_manifest(str(descriptor.get("locator", "")), policy)
    elif "members" in descriptor:
        members = [
            _member_record_from_path(
                manifest_id=manifest_id,
                member_id=str(item.get("member_id", f"f0_member_{fixture_id}_{index + 1}")),
                path_text=str(item.get("path", "")),
                declared_size=int(item.get("declared_size", 0)),
                is_directory=bool(item.get("is_directory", False)),
                compression_method=item.get("compression_method_if_available"),
                checksum=item.get("checksum_if_available"),
                is_symlink=bool(item.get("is_symlink", False)),
                is_device=bool(item.get("is_device", False)),
                policy=policy,
            )
            for index, item in enumerate(_list(descriptor.get("members")))
            if isinstance(item, Mapping)
        ]
    else:
        members = []

    total_declared_size = sum(int(member.get("declared_size", 0)) for member in members)
    max_depth_observed = max([int(member.get("depth", 0)) for member in members] or [0])
    manifest_block_reasons: list[str] = []
    if container_kind not in {"zip_fixture_manifest", "directory_manifest_fixture", "descriptor_manifest_fixture"}:
        manifest_block_reasons.append("container_type_blocked_or_deferred")
    if len(members) > int(limits["max_member_count"]):
        manifest_block_reasons.append("member_count_exceeds_limit")
    if total_declared_size > int(limits["max_declared_total_size_bytes"]):
        manifest_block_reasons.append("declared_total_size_exceeds_limit")
    if max_depth_observed > int(limits["max_nested_depth"]):
        manifest_block_reasons.append("nested_depth_exceeds_limit")

    risk_report_id = f"f0_risk_report_{fixture_id}"
    manifest = {
        "schema_version": "member_manifest.v0",
        "record_type": "member_manifest",
        "manifest_id": manifest_id,
        "container_id": container_id,
        "container_kind": container_kind,
        "fixture_id": fixture_id,
        "member_count": len(members),
        "total_declared_size": total_declared_size,
        "total_uncompressed_size_if_known": total_declared_size,
        "max_depth_observed": max_depth_observed,
        "members": members,
        "risk_report_id": risk_report_id,
        "manifest_only": True,
        "extracted_to_filesystem": False,
        "source_context": descriptor.get("source_context", {"source_kind": "f0_safe_fixture_descriptor"}),
        "domain_id": descriptor.get("domain_id", "legacy_software"),
        "review_required": True,
        "accepted_truth": False,
        "limitations": [
            "fixture-only member manifest",
            "member paths are observations, not evidence or accepted truth",
        ],
        "risk_flags": sorted(set(manifest_block_reasons + [reason for member in members for reason in _string_list(member.get("block_reasons"))])),
        "rights_flags": [],
        "non_claims": _default_non_claims(),
        "created_at": FIXED_CREATED_AT,
    }
    manifest["risk_report"] = build_extraction_risk_report(manifest, policy)
    return manifest


def validate_member_record(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Validate one manifest-only member record."""
    errors: list[str] = []
    member_id = str(record.get("member_id", "member_record"))
    for field in (
        "member_id",
        "manifest_id",
        "path",
        "normalized_path",
        "path_safe",
        "member_kind",
        "declared_size",
        "checksum_if_available",
        "compression_method_if_available",
        "depth",
        "is_directory",
        "is_symlink",
        "is_device",
        "is_absolute_path",
        "contains_parent_traversal",
        "blocked",
        "block_reasons",
    ):
        if field not in record:
            errors.append(f"{member_id}: missing {field}.")
    expected = _path_safety(str(record.get("path", "")), int(record.get("declared_size", 0)), bool(record.get("is_symlink", False)), bool(record.get("is_device", False)), policy)
    if record.get("path_safe") is not expected["path_safe"]:
        errors.append(f"{member_id}: path_safe does not match normalized path checks.")
    if bool(record.get("blocked")) != bool(expected["block_reasons"]):
        errors.append(f"{member_id}: blocked must match block_reasons.")
    return {
        "schema_version": "member_record_validation_report.v0",
        "record_id": member_id,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
    }


def build_extraction_risk_report(manifest: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a risk report for a manifest-only enumeration."""
    del policy
    members = [member for member in _list(manifest.get("members")) if isinstance(member, Mapping)]
    blocked_members = [member for member in members if member.get("blocked") is True]
    reasons = sorted({reason for member in blocked_members for reason in _string_list(member.get("block_reasons"))})
    return {
        "schema_version": "extraction_risk_report.v0",
        "record_type": "extraction_risk_report",
        "risk_report_id": str(manifest.get("risk_report_id", "")),
        "manifest_id": str(manifest.get("manifest_id", "")),
        "blocked_member_count": len(blocked_members),
        "blocked_reasons": reasons,
        "path_traversal_detected": "path_traversal" in reasons,
        "absolute_path_detected": "absolute_path" in reasons,
        "resource_limit_exceeded": any(reason.endswith("_exceeds_limit") for reason in _string_list(manifest.get("risk_flags")) + reasons),
        "archive_bomb_guard_applied": True,
        "extraction_performed": False,
        "execution_performed": False,
        "review_required": True,
        "accepted_truth": False,
        "non_claims": _default_non_claims(),
        "created_at": FIXED_CREATED_AT,
    }


def build_extraction_boundary_report(manifest: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build the F0 boundary report for the current manifest packet."""
    del policy
    return {
        "schema_version": "extraction_boundary_report.v0",
        "record_type": "extraction_boundary_report",
        "manifest_id": str(manifest.get("manifest_id", "")),
        "manifest_only_enumeration": True,
        "fake_evidence_created": False,
        "fake_verified_records_created": False,
        "live_source_call_performed": False,
        "source_probe_executed": False,
        "download_performed": False,
        "upload_performed": False,
        "filesystem_extraction_performed": False,
        "arbitrary_file_extraction_performed": False,
        "execution_performed": False,
        "operator_instance_mutated": False,
        "master_index_mutated": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "created_at": FIXED_CREATED_AT,
    }


def build_extraction_console_view(manifest: Mapping[str, Any], projection_profile: str = "operator_workbench") -> dict[str, Any]:
    """Build a read-only Workbench F0 console projection."""
    if projection_profile not in PROJECTION_PROFILES:
        raise F0ManifestError(f"unsupported projection profile: {projection_profile}")
    operator_detail_visible = projection_profile == "operator_workbench"
    members = [dict(member) for member in _list(manifest.get("members")) if isinstance(member, Mapping)]
    if not operator_detail_visible:
        for member in members:
            member.pop("checksum_if_available", None)
            member.pop("compression_method_if_available", None)
    return {
        "schema_version": "extraction_console_view.v0",
        "record_type": "extraction_console_view",
        "view_id": f"f0:{manifest.get('manifest_id', '')}:{projection_profile}",
        "routes": [
            "/extraction",
            "/extraction/manifests",
            "/extraction/workunits",
            "/extraction/policies",
            "/extraction/blocked",
        ],
        "projection_profile": projection_profile,
        "read_only": True,
        "operator_detail_visible": operator_detail_visible,
        "views": {
            "ExtractionOverviewView": {
                "manifest_id": manifest.get("manifest_id", ""),
                "member_count": manifest.get("member_count", 0),
                "blocked_member_count": len([member for member in members if member.get("blocked") is True]),
                "manifest_only": True,
            },
            "ContainerDescriptorView": {
                "container_id": manifest.get("container_id", ""),
                "container_kind": manifest.get("container_kind", ""),
                "fixture_id": manifest.get("fixture_id", ""),
            },
            "MemberManifestView": {
                "manifest_id": manifest.get("manifest_id", ""),
                "members": members,
            },
            "MemberRecordView": members[0] if members else {},
            "ExtractionRiskReportView": manifest.get("risk_report", build_extraction_risk_report(manifest)),
            "ExtractionWorkUnitSeedView": build_workunit_seed_suggestions(manifest),
            "BlockedContainerView": {
                "blocked_actions": list(BLOCKED_ACTIONS),
                "blocked_container_types": ["iso", "dmg", "cab", "msi", "7z", "rar", "sit", "hqx", "bin/cue", "nested_archives"],
            },
            "ExtractionBoundaryReportView": build_extraction_boundary_report(manifest),
        },
        "blocked_actions": list(BLOCKED_ACTIONS),
        "non_claims": _default_non_claims(),
        "created_at": FIXED_CREATED_AT,
    }


def build_workunit_seed_suggestions(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Build dry-run extraction WorkUnit seed suggestions."""
    manifest_id = str(manifest.get("manifest_id", ""))
    fixture_id = str(manifest.get("fixture_id", ""))
    blocked = bool(_string_list(manifest.get("risk_flags")))
    return {
        "schema_version": "extraction_workunit_seed_set.v0",
        "record_type": "extraction_workunit_seed_set",
        "manifest_id": manifest_id,
        "dry_run": True,
        "creates_runtime_workunit": False,
        "creates_evidence": False,
        "seeds": [
            {
                "schema_version": "extraction_workunit_seed.v0",
                "record_type": "extraction_workunit_seed",
                "workunit_seed_id": f"f0_workunit_seed_review_{fixture_id}",
                "source_record_id": manifest_id,
                "candidate_id": f"f0_member_observation_candidate_{fixture_id}",
                "container_locator": str(manifest.get("container_id", "")),
                "requested_action": "review_member_manifest" if not blocked else "block_unsafe_container",
                "policy_ref": "control/policies/f0_extraction_policy.json",
                "allowed": False,
                "blocked_reasons": ["operator_policy_required", *(_string_list(manifest.get("risk_flags")))],
                "future_task": "F0-FUTURE-SAFE-EXTRACTION",
                "review_required": True,
                "accepted_truth": False,
                "non_claims": _default_non_claims(),
            }
        ],
    }


def _member_record_from_path(
    *,
    manifest_id: str,
    member_id: str,
    path_text: str,
    declared_size: int,
    is_directory: bool,
    compression_method: Any,
    checksum: Any,
    is_symlink: bool,
    policy: Mapping[str, Any] | None,
    is_device: bool = False,
) -> dict[str, Any]:
    safety = _path_safety(path_text, declared_size, is_symlink, is_device, policy)
    suffix = PurePosixPath(safety["normalized_path"]).suffix.lower()
    if is_directory:
        member_kind = "directory"
    elif suffix in NESTED_CONTAINER_SUFFIXES:
        member_kind = "nested_container"
        safety["block_reasons"].append("nested_archive_deferred")
    else:
        member_kind = "file"
    block_reasons = sorted(set(safety["block_reasons"]))
    return {
        "schema_version": "member_record.v0",
        "record_type": "member_record",
        "member_id": member_id,
        "manifest_id": manifest_id,
        "path": path_text,
        "normalized_path": safety["normalized_path"],
        "path_safe": safety["path_safe"] and not block_reasons,
        "member_kind": member_kind,
        "declared_size": declared_size,
        "checksum_if_available": checksum,
        "compression_method_if_available": compression_method,
        "depth": safety["depth"],
        "is_directory": is_directory,
        "is_symlink": is_symlink,
        "is_device": is_device,
        "is_absolute_path": safety["is_absolute_path"],
        "contains_parent_traversal": safety["contains_parent_traversal"],
        "blocked": bool(block_reasons),
        "block_reasons": block_reasons,
        "source_context": {"source_kind": "f0_member_manifest"},
        "review_required": True,
        "accepted_truth": False,
        "limitations": ["manifest-only observation; member contents were not read or extracted"],
        "risk_flags": block_reasons,
        "rights_flags": [],
        "non_claims": _default_non_claims(),
        "created_at": FIXED_CREATED_AT,
    }


def _path_safety(
    path_text: str,
    declared_size: int,
    is_symlink: bool,
    is_device: bool,
    policy: Mapping[str, Any] | None,
) -> dict[str, Any]:
    limits = _limits(policy)
    normalized = path_text.replace("\\", "/")
    is_absolute = normalized.startswith("/") or bool(re.match(r"^[A-Za-z]:/", normalized))
    parts = [part for part in normalized.split("/") if part not in {"", "."}]
    contains_parent = any(part == ".." for part in parts)
    depth = max(len([part for part in parts if part != ".."]) - 1, 0)
    block_reasons: list[str] = []
    if not normalized or "\x00" in normalized:
        block_reasons.append("invalid_path")
    if is_absolute:
        block_reasons.append("absolute_path")
    if contains_parent:
        block_reasons.append("path_traversal")
    if len(path_text) > int(limits["max_filename_length"]):
        block_reasons.append("filename_length_exceeds_limit")
    if depth > int(limits["max_nested_depth"]):
        block_reasons.append("nested_depth_exceeds_limit")
    if declared_size > int(limits["max_declared_total_size_bytes"]):
        block_reasons.append("declared_size_exceeds_limit")
    if is_symlink:
        block_reasons.append("symlink_materialization_forbidden")
    if is_device:
        block_reasons.append("device_file_materialization_forbidden")
    return {
        "normalized_path": "/".join(parts),
        "path_safe": not block_reasons,
        "is_absolute_path": is_absolute,
        "contains_parent_traversal": contains_parent,
        "depth": depth,
        "block_reasons": block_reasons,
    }


def _zip_info_is_symlink(info: Any) -> bool:
    mode = (int(getattr(info, "external_attr", 0)) >> 16) & 0o170000
    return mode == 0o120000


def _limits(policy: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if not isinstance(policy, Mapping):
        return DEFAULT_RESOURCE_LIMITS
    if isinstance(policy.get("resource_limits"), Mapping):
        merged = dict(DEFAULT_RESOURCE_LIMITS)
        merged.update(_mapping(policy.get("resource_limits")))
        return merged
    merged = dict(DEFAULT_RESOURCE_LIMITS)
    for key in DEFAULT_RESOURCE_LIMITS:
        if key in policy:
            merged[key] = policy[key]
    return merged


def _resolve_allowed_fixture_path(path: str | Path) -> Path:
    resolved = _resolve_path(path)
    allowed_roots = [
        REPO_ROOT / "examples/f0",
        REPO_ROOT / "examples/extraction/fixtures",
        Path(tempfile.gettempdir()).resolve(),
    ]
    if not any(resolved == root.resolve() or resolved.is_relative_to(root.resolve()) for root in allowed_roots):
        raise F0ManifestError(f"refusing to read outside F0 fixture roots: {resolved}")
    return resolved


def _resolve_path(path: str | Path) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = REPO_ROOT / resolved
    return resolved.resolve()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _default_non_claims() -> dict[str, bool]:
    return {
        "fake_evidence_created": False,
        "fake_verified_records_created": False,
        "live_source_call_performed": False,
        "source_probe_executed": False,
        "download_performed": False,
        "upload_performed": False,
        "filesystem_extraction_performed": False,
        "arbitrary_file_extraction_performed": False,
        "execution_performed": False,
        "operator_instance_mutated": False,
        "master_index_mutated": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]
