from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def project_snapshot_files(snapshot_build_result: Mapping[str, Any], output_dir: str | Path | None = None) -> dict[str, Any]:
    base = Path(output_dir or "examples/snapshots/projected_files")
    files = {
        "snapshot_envelope.json": snapshot_build_result["envelope"],
        "snapshot_manifest.json": snapshot_build_result["manifest"],
        "snapshot_integrity_manifest.json": snapshot_build_result["integrity_manifest"],
    }
    written = []
    for name, payload in files.items():
        path = base / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(path.as_posix())
    return {
        "schema_version": "snapshot_files_projection.v0",
        "projection_profile": "files_read_only",
        "read_only": True,
        "written_files": written,
        "mutation_enabled": False,
        "deployment_performed": False,
    }
