from __future__ import annotations

from typing import Any

from runtime.source.action import build_source_wave_adapter, get_source_family_manifest


SOURCE_FAMILY = "open_library_metadata"


def build_adapter():
    return build_source_wave_adapter(SOURCE_FAMILY)


def build_registration() -> dict[str, Any]:
    return get_source_family_manifest(SOURCE_FAMILY)
