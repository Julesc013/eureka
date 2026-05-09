"""Container type detection for fixture archives."""

from __future__ import annotations

from pathlib import Path
import tarfile
import zipfile
from typing import Any, Mapping


def detect_container_type(path: str | Path, policy: Mapping[str, Any] | None = None) -> str:
    candidate = Path(path)
    suffixes = "".join(candidate.suffixes).casefold()
    if zipfile.is_zipfile(candidate):
        return "zip"
    if tarfile.is_tarfile(candidate):
        return "tar"
    if suffixes.endswith(".zip"):
        return "zip"
    if suffixes.endswith((".tar", ".tar.gz", ".tgz")):
        return "tar"
    return "unsupported"


def ensure_supported_container(container_type: str, policy: Mapping[str, Any] | None = None) -> None:
    allowed = set((policy or {}).get("allowed_container_types", ["zip", "tar"]))
    if container_type not in allowed:
        raise ValueError(f"unsupported container type: {container_type}")
