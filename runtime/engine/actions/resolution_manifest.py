from __future__ import annotations

from typing import Any

from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.normalize import NormalizedResolutionRecord
from runtime.engine.resolve.object_summary import normalized_record_to_object_summary


class ResolutionManifestExportService:
    def __init__(self, catalog: NormalizedCatalog) -> None:
        self._catalog = catalog

    def has_manifest_available(self, target_ref: str) -> bool:
        return self._catalog.find_by_target_ref(target_ref) is not None

    def export_manifest(self, target_ref: str) -> dict[str, Any] | None:
        record = self._catalog.find_by_target_ref(target_ref)
        if record is None:
            return None
        return build_resolution_manifest(record)


def build_resolution_manifest(record: NormalizedResolutionRecord) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "manifest_kind": "eureka.resolution_manifest",
        "manifest_version": "0.1.0-draft",
        "generated_from": {
            "kind": "normalized_resolution_record",
            "source_name": record.source_name,
            "source_locator": record.source_locator,
        },
        "target_ref": record.target_ref,
        "primary_object": normalized_record_to_object_summary(record).to_dict(),
        "source_fixture": {
            "kind": "synthetic_fixture",
            "locator": record.source_locator,
        },
        "notices": [],
    }
    matched_state = _compact_mapping(
        {
            "id": record.state_id,
            "kind": record.state_kind,
        }
    )
    if matched_state:
        manifest["matched_state"] = matched_state

    representation = _compact_mapping(
        {
            "id": record.representation_id,
            "kind": record.representation_kind,
            "access_path": _compact_mapping(
                {
                    "id": record.access_path_id,
                    "kind": record.access_path_kind,
                    "locator": record.access_path_locator,
                }
            ),
        }
    )
    if representation:
        manifest["representations"] = [representation]
    return manifest


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
