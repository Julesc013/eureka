"""Tier 1 member listing for fixture archives."""

from __future__ import annotations

from pathlib import Path
import stat
import tarfile
import zipfile
from typing import Any, Mapping

from runtime.extraction.container_detect import detect_container_type
from runtime.extraction.guards import check_path_safety, manifest_like, product_boundary, stable_id, truth_boundary


def extract_tier1_member_listing(path: str | Path, policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    fixture = Path(path)
    container_type = detect_container_type(fixture, policy)
    if container_type == "zip":
        return _zip_members(fixture, policy)
    if container_type == "tar":
        return _tar_members(fixture, policy)
    raise ValueError(f"unsupported container type for member listing: {container_type}")


def _zip_members(path: Path, policy: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    members: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            mode = (info.external_attr >> 16) & 0o170000
            is_symlink = mode == stat.S_IFLNK
            member_kind = "directory" if info.is_dir() else "file"
            if is_symlink:
                member_kind = "symlink"
            members.append(
                _member_record(
                    raw_path=info.filename,
                    member_kind=member_kind,
                    size_compressed=info.compress_size,
                    size_uncompressed=info.file_size,
                    policy=policy,
                    extra_block_reasons=["symlink"] if is_symlink else [],
                )
            )
    return members


def _tar_members(path: Path, policy: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    members: list[dict[str, Any]] = []
    with tarfile.open(path) as archive:
        for info in archive.getmembers():
            if info.isdir():
                kind = "directory"
            elif info.isfile():
                kind = "file"
            elif info.issym() or info.islnk():
                kind = "symlink"
            else:
                kind = "special"
            block_reasons: list[str] = []
            if kind == "symlink":
                block_reasons.append("symlink")
            if kind == "special":
                block_reasons.append("special_file")
            members.append(
                _member_record(
                    raw_path=info.name,
                    member_kind=kind,
                    size_compressed=info.size,
                    size_uncompressed=info.size,
                    policy=policy,
                    extra_block_reasons=block_reasons,
                )
            )
    return members


def _member_record(
    *,
    raw_path: str,
    member_kind: str,
    size_compressed: int | None,
    size_uncompressed: int | None,
    policy: Mapping[str, Any] | None,
    extra_block_reasons: list[str],
) -> dict[str, Any]:
    path_check = check_path_safety(raw_path, policy)
    reasons = sorted(set(path_check["block_reasons"] + extra_block_reasons))
    normalized = path_check["normalized_member_path"]
    suffix = Path(normalized).suffix.casefold() if normalized else ""
    manifest = manifest_like(raw_path, policy)
    return {
        "schema_version": "extraction_member.v0",
        "member_id": stable_id("extraction.member", {"path": raw_path, "size": size_uncompressed}),
        "member_path": raw_path,
        "normalized_member_path": normalized,
        "member_kind": "manifest" if manifest and member_kind == "file" else member_kind,
        "size_compressed": size_compressed,
        "size_uncompressed": size_uncompressed,
        "detected_extension": suffix,
        "manifest_like": manifest,
        "blocked": bool(reasons),
        "block_reason": ";".join(reasons),
        "path_safe": not path_check["block_reasons"],
        "preview_allowed": not reasons and member_kind == "file",
        "extracted_payload_stored": False,
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
    }
