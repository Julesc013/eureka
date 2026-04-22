from __future__ import annotations

from dataclasses import asdict
from io import BytesIO
import json
import re
from typing import Any
import zipfile

from runtime.engine.actions import build_resolution_manifest
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.normalize import NormalizedResolutionRecord
from runtime.engine.interfaces.service import ResolutionBundleArtifact
from runtime.engine.resolve import resolved_resource_id_for_record


_FIXED_ZIP_DATETIME = (1980, 1, 1, 0, 0, 0)
RESOLUTION_BUNDLE_MEMBER_ORDER = (
    "README.txt",
    "bundle.json",
    "manifest.json",
    "records/normalized_record.json",
)


class ResolutionBundleExportService:
    def __init__(self, catalog: NormalizedCatalog) -> None:
        self._catalog = catalog

    def has_bundle_available(self, target_ref: str) -> bool:
        return self._catalog.find_by_target_ref(target_ref) is not None

    def export_bundle(self, target_ref: str) -> ResolutionBundleArtifact | None:
        record = self._catalog.find_by_target_ref(target_ref)
        if record is None:
            return None
        return build_resolution_bundle(record)


def build_resolution_bundle(record: NormalizedResolutionRecord) -> ResolutionBundleArtifact:
    entries = (
        ("README.txt", _bundle_readme_bytes(record)),
        ("bundle.json", _json_bytes(_bundle_metadata(record))),
        ("manifest.json", _json_bytes(build_resolution_manifest(record))),
        ("records/normalized_record.json", _json_bytes(_normalized_record_export(record))),
    )
    payload = _build_zip_payload(entries)
    return ResolutionBundleArtifact(
        filename=_bundle_filename(record.target_ref),
        content_type="application/zip",
        payload=payload,
    )


def _bundle_metadata(record: NormalizedResolutionRecord) -> dict[str, Any]:
    return {
        "bundle_kind": "eureka.resolution_bundle",
        "bundle_version": "0.1.0-draft",
        "generated_from": {
            "kind": "normalized_resolution_record",
            "source_name": record.source_name,
            "source_locator": record.source_locator,
        },
        "target_ref": record.target_ref,
        "resolved_resource_id": resolved_resource_id_for_record(record),
        "source": {
            "family": record.source_family,
            "label": record.source_family_label or record.source_family,
            "locator": record.access_path_locator or record.source_locator,
        },
        "created_by_slice": "portable_bundle_export",
        "entries": list(RESOLUTION_BUNDLE_MEMBER_ORDER),
    }


def _normalized_record_export(record: NormalizedResolutionRecord) -> dict[str, Any]:
    values = asdict(record)
    return {
        "record_kind": "normalized_resolution_record",
        "target_ref": values["target_ref"],
        "resolved_resource_id": resolved_resource_id_for_record(record),
        "source": _compact_mapping(
            {
                "family": values["source_family"],
                "label": values["source_family_label"],
                "name": values["source_name"],
                "locator": values["source_locator"],
            }
        ),
        "object": _compact_mapping(
            {
                "id": values["object_id"],
                "kind": values["object_kind"],
                "label": values["object_label"],
            }
        ),
        "state": _compact_mapping(
            {
                "id": values["state_id"],
                "kind": values["state_kind"],
            }
        ),
        "representation": _compact_mapping(
            {
                "id": values["representation_id"],
                "kind": values["representation_kind"],
                "access_path": _compact_mapping(
                    {
                        "id": values["access_path_id"],
                        "kind": values["access_path_kind"],
                        "locator": values["access_path_locator"],
                    }
                ),
            }
        ),
    }


def _bundle_readme_bytes(record: NormalizedResolutionRecord) -> bytes:
    return (
        "Eureka bootstrap resolution bundle\n"
        f"target_ref: {record.target_ref}\n"
        "\n"
        "This ZIP is a local deterministic export artifact from the portable bundle thin slice.\n"
        "It is synthetic, rights-safe, and not a final snapshot, restore, or installer contract.\n"
    ).encode("utf-8")


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return f"{json.dumps(payload, indent=2, sort_keys=True)}\n".encode("utf-8")


def _build_zip_payload(entries: tuple[tuple[str, bytes], ...]) -> bytes:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        for name, data in entries:
            info = zipfile.ZipInfo(name, date_time=_FIXED_ZIP_DATETIME)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return buffer.getvalue()


def _bundle_filename(target_ref: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9.]+", "-", target_ref).strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return f"eureka-resolution-bundle-{normalized}.zip"


def _compact_mapping(values: dict[str, Any]) -> dict[str, Any]:
    compacted: dict[str, Any] = {}
    for key, value in values.items():
        if value is None:
            continue
        if isinstance(value, dict):
            nested = _compact_mapping(value)
            if nested:
                compacted[key] = nested
            continue
        compacted[key] = value
    return compacted
