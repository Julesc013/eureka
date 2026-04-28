from __future__ import annotations

import argparse
import hashlib
from html import escape
import json
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "snapshots" / "examples" / "static_snapshot_v0"
DEFAULT_DATA_ROOT = REPO_ROOT / "public_site" / "data"
SNAPSHOT_CONTRACT = REPO_ROOT / "control" / "inventory" / "publication" / "snapshot_contract.json"

SCHEMA_VERSION = "0.1.0"
SNAPSHOT_FORMAT_VERSION = "0.1.0"
GENERATED_BY = "scripts/generate_static_snapshot.py"
SLICE_ID = "signed_snapshot_format_v0"

PUBLIC_DATA_INPUTS = {
    "SOURCE_SUMMARY.json": "source_summary.json",
    "EVAL_SUMMARY.json": "eval_summary.json",
    "ROUTE_SUMMARY.json": "route_summary.json",
    "PAGE_REGISTRY.json": "page_registry.json",
}
REQUIRED_FILES = (
    "README_FIRST.txt",
    "index.html",
    "index.txt",
    "SNAPSHOT_MANIFEST.json",
    "BUILD_MANIFEST.json",
    "SOURCE_SUMMARY.json",
    "EVAL_SUMMARY.json",
    "ROUTE_SUMMARY.json",
    "PAGE_REGISTRY.json",
    "CHECKSUMS.SHA256",
    "SIGNATURES.README.txt",
    "data/README.txt",
)


class SnapshotGenerationError(RuntimeError):
    pass


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Eureka static snapshot seed example.")
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Directory that receives the generated snapshot example.",
    )
    parser.add_argument(
        "--data-root",
        default=str(DEFAULT_DATA_ROOT),
        help="Directory containing public data summaries.",
    )
    parser.add_argument("--update", action="store_true", help="Write generated snapshot files.")
    parser.add_argument("--check", action="store_true", help="Verify committed snapshot files match generated output.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    output = stdout or sys.stdout
    output_root = Path(args.output_root)
    data_root = Path(args.data_root)

    try:
        if args.check:
            report = check_snapshot(output_root, data_root)
        elif args.update:
            report = write_snapshot(output_root, data_root)
        else:
            files = generate_snapshot_files(data_root)
            report = _summary_report(output_root, data_root, files, updated=False)
        if args.json:
            output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        else:
            output.write(_format_plain(report))
        return 0 if report["status"] == "valid" else 1
    except SnapshotGenerationError as exc:
        report = {"status": "invalid", "created_by": SLICE_ID, "errors": [str(exc)]}
        if args.json:
            output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        else:
            output.write(_format_plain(report))
        return 1


def generate_snapshot_files(data_root: Path = DEFAULT_DATA_ROOT) -> dict[str, str]:
    data_root = data_root.resolve()
    public_data = _load_public_data(data_root)
    contract = _load_json(SNAPSHOT_CONTRACT)

    files: dict[str, str] = {}
    for output_name, input_name in PUBLIC_DATA_INPUTS.items():
        files[output_name] = _stable_json(public_data[input_name])

    files["BUILD_MANIFEST.json"] = _stable_json(_build_manifest(public_data, contract))
    files["README_FIRST.txt"] = _readme_first()
    files["index.txt"] = _index_txt(public_data)
    files["index.html"] = _index_html(public_data)
    files["SIGNATURES.README.txt"] = _signature_readme()
    files["data/README.txt"] = _data_readme()

    manifest = _snapshot_manifest(public_data, contract, sorted(files))
    files["SNAPSHOT_MANIFEST.json"] = _stable_json(manifest)
    files["CHECKSUMS.SHA256"] = _checksums(files)
    return dict(sorted(files.items()))


def write_snapshot(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    data_root: Path = DEFAULT_DATA_ROOT,
) -> dict[str, Any]:
    files = generate_snapshot_files(data_root)
    output_root = output_root.resolve()
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    for relative, text in files.items():
        path = output_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    return _summary_report(output_root, data_root, files, updated=True)


def check_snapshot(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    data_root: Path = DEFAULT_DATA_ROOT,
) -> dict[str, Any]:
    files = generate_snapshot_files(data_root)
    output_root = output_root.resolve()
    errors: list[str] = []
    expected = set(files)
    actual = {
        str(path.relative_to(output_root)).replace("\\", "/")
        for path in output_root.rglob("*")
        if path.is_file()
    } if output_root.exists() else set()
    for relative, expected_text in files.items():
        path = output_root / relative
        if not path.exists():
            errors.append(f"{_display_path(path)}: generated snapshot file is missing.")
            continue
        actual_text = path.read_text(encoding="utf-8")
        if actual_text != expected_text:
            errors.append(f"{_display_path(path)}: generated snapshot file is stale.")
    extra = sorted(actual - expected)
    if extra:
        errors.append(f"{_display_path(output_root)}: unexpected snapshot files {extra}.")
    return {
        **_summary_report(output_root, data_root, files, updated=False),
        "status": "valid" if not errors else "invalid",
        "check_mode": True,
        "errors": errors,
    }


def _load_public_data(data_root: Path) -> dict[str, Mapping[str, Any]]:
    required = set(PUBLIC_DATA_INPUTS.values()) | {"build_manifest.json"}
    data: dict[str, Mapping[str, Any]] = {}
    for name in sorted(required):
        path = data_root / name
        payload = _load_json(path)
        if not isinstance(payload, Mapping):
            raise SnapshotGenerationError(f"{_display_path(path)} must contain a JSON object.")
        data[name] = payload
    return data


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SnapshotGenerationError(f"missing required input: {_display_path(path)}") from exc
    except json.JSONDecodeError as exc:
        raise SnapshotGenerationError(f"invalid JSON input {_display_path(path)}: {exc}") from exc


def _build_manifest(
    public_data: Mapping[str, Mapping[str, Any]],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    public_build = dict(public_data["build_manifest.json"])
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "source": SLICE_ID,
        "snapshot_format_version": SNAPSHOT_FORMAT_VERSION,
        "snapshot_contract_id": contract.get("snapshot_contract_id", "eureka-static-snapshot-format"),
        "snapshot_example_root": "snapshots/examples/static_snapshot_v0",
        "public_build_manifest": {
            "repo": public_build.get("repo", "Julesc013/eureka"),
            "branch": public_build.get("branch", "UNKNOWN_UNTIL_CI"),
            "commit": public_build.get("commit", "UNKNOWN_UNTIL_CI"),
            "built_at": public_build.get("built_at", "UNKNOWN_UNTIL_CI"),
            "source": public_build.get("source", "generated_public_data_summaries_v0"),
        },
        "artifact_kind": "seed_snapshot_example",
        "production_signed_release": False,
        "real_signing_keys_present": False,
        "contains_real_binaries": False,
        "contains_live_backend": False,
        "contains_live_probes": False,
        "contains_external_observations": False,
        "deployment_performed": False,
        "source_inputs": [
            "control/inventory/publication/snapshot_contract.json",
            "public_site/data/source_summary.json",
            "public_site/data/eval_summary.json",
            "public_site/data/route_summary.json",
            "public_site/data/page_registry.json",
            "public_site/data/build_manifest.json",
        ],
        "validations_expected": [
            "python scripts/generate_static_snapshot.py --check",
            "python scripts/validate_static_snapshot.py",
        ],
    }


def _snapshot_manifest(
    public_data: Mapping[str, Mapping[str, Any]],
    contract: Mapping[str, Any],
    pre_manifest_files: Sequence[str],
) -> dict[str, Any]:
    required_files = list(contract.get("required_files", [])) or list(REQUIRED_FILES)
    files = sorted(set(pre_manifest_files) | {"SNAPSHOT_MANIFEST.json", "CHECKSUMS.SHA256"})
    return {
        "schema_version": SCHEMA_VERSION,
        "snapshot_id": "eureka-static-snapshot-v0-seed",
        "snapshot_format_version": SNAPSHOT_FORMAT_VERSION,
        "status": "static_demo",
        "stability": "experimental",
        "generated_by": GENERATED_BY,
        "created_by_slice": SLICE_ID,
        "artifact_kind": "seed_example",
        "production_signed_release": False,
        "real_signing_keys_present": False,
        "contains_real_binaries": False,
        "contains_live_backend": False,
        "contains_live_probes": False,
        "contains_external_observations": False,
        "required_files": required_files,
        "files": files,
        "checksummed_files": sorted(path for path in files if path != "CHECKSUMS.SHA256"),
        "checksum_file": "CHECKSUMS.SHA256",
        "checksum_algorithm": "sha256",
        "signature_placeholder": "SIGNATURES.README.txt",
        "public_data_files": [
            "SOURCE_SUMMARY.json",
            "EVAL_SUMMARY.json",
            "ROUTE_SUMMARY.json",
            "PAGE_REGISTRY.json",
            "BUILD_MANIFEST.json",
        ],
        "source_counts": {
            "sources": public_data["source_summary.json"].get("source_count", 0),
            "archive_eval_tasks": _mapping(public_data["eval_summary.json"].get("archive_resolution")).get("task_count", 0),
            "search_audit_queries": _mapping(public_data["eval_summary.json"].get("search_usefulness")).get("query_count", 0),
            "public_pages": len(public_data["page_registry.json"].get("pages", [])),
        },
        "relationships": {
            "public_site": "public_site remains the current GitHub Pages static artifact.",
            "files_surface": "public_site/files references this seed format but does not publish production snapshots.",
            "live_backend": "Snapshots are static offline data and are not live backend routes.",
            "relay": "Future relay surfaces may consume snapshots after separate design and operator policy.",
            "native_client": "Future native clients may consume snapshots after readiness prerequisites are met.",
        },
        "limitations": [
            "This is not a production signed release.",
            "No real signing keys are included.",
            "No executable downloads or software binaries are included.",
            "No live backend data, live probe data, or external observations are included.",
            "The public /snapshots/ route remains future/deferred.",
        ],
    }


def _readme_first() -> str:
    return "\n".join(
        [
            "Eureka Static Snapshot v0 Seed",
            "==============================",
            "",
            "This is a deterministic seed example for Signed Snapshot Format v0.",
            "It is not a production signed release.",
            "It contains no private signing keys.",
            "It contains no executable downloads or software mirrors.",
            "It contains no live backend output, live probe output, or external observations.",
            "",
            "Start with SNAPSHOT_MANIFEST.json, CHECKSUMS.SHA256, and SIGNATURES.README.txt.",
            "Use index.txt for a plain-text overview and index.html for a simple static overview.",
            "",
        ]
    )


def _index_txt(public_data: Mapping[str, Mapping[str, Any]]) -> str:
    source_count = public_data["source_summary.json"].get("source_count", "unknown")
    route_counts = _mapping(public_data["route_summary.json"].get("route_counts"))
    return "\n".join(
        [
            "Eureka Static Snapshot v0",
            "=========================",
            "",
            "Format: 0.1.0",
            "Status: seed example, not production",
            "Signing: placeholder documentation only",
            "Private keys: none",
            "Executable downloads: none",
            "Live backend: none",
            "Live probes: none",
            "External observations: none",
            "",
            f"Source records summarized: {source_count}",
            f"Public-alpha routes summarized: {route_counts.get('total', 'unknown')}",
            "",
            "Files:",
            "- SNAPSHOT_MANIFEST.json",
            "- BUILD_MANIFEST.json",
            "- SOURCE_SUMMARY.json",
            "- EVAL_SUMMARY.json",
            "- ROUTE_SUMMARY.json",
            "- PAGE_REGISTRY.json",
            "- CHECKSUMS.SHA256",
            "- SIGNATURES.README.txt",
            "",
        ]
    )


def _index_html(public_data: Mapping[str, Mapping[str, Any]]) -> str:
    source_count = escape(str(public_data["source_summary.json"].get("source_count", "unknown")))
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            "  <title>Eureka Static Snapshot v0</title>",
            "</head>",
            "<body>",
            "  <h1>Eureka Static Snapshot v0 Seed</h1>",
            "  <p><strong>Seed example only.</strong> This is not a production signed release.</p>",
            "  <p>No private keys, executable downloads, live backend output, live probes, or external observations are included.</p>",
            f"  <p>Source records summarized: {source_count}</p>",
            "  <ul>",
            '    <li><a href="SNAPSHOT_MANIFEST.json">SNAPSHOT_MANIFEST.json</a></li>',
            '    <li><a href="BUILD_MANIFEST.json">BUILD_MANIFEST.json</a></li>',
            '    <li><a href="SOURCE_SUMMARY.json">SOURCE_SUMMARY.json</a></li>',
            '    <li><a href="EVAL_SUMMARY.json">EVAL_SUMMARY.json</a></li>',
            '    <li><a href="ROUTE_SUMMARY.json">ROUTE_SUMMARY.json</a></li>',
            '    <li><a href="PAGE_REGISTRY.json">PAGE_REGISTRY.json</a></li>',
            '    <li><a href="CHECKSUMS.SHA256">CHECKSUMS.SHA256</a></li>',
            '    <li><a href="SIGNATURES.README.txt">SIGNATURES.README.txt</a></li>',
            '    <li><a href="index.txt">index.txt</a></li>',
            "  </ul>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _signature_readme() -> str:
    return "\n".join(
        [
            "Snapshot Signature Placeholder",
            "==============================",
            "",
            "No production signing is performed for Signed Snapshot Format v0.",
            "No private keys are stored in this repository.",
            "No production trust chain exists for this seed example.",
            "This file is documentation only; it is not a detached signature.",
            "",
            "CHECKSUMS.SHA256 can detect accidental corruption or generator drift.",
            "Checksums obtained from the same untrusted channel are not full authenticity proof.",
            "",
            "Future real signatures require key management, release provenance, revocation, rotation, and operator signoff.",
            "",
        ]
    )


def _data_readme() -> str:
    return "\n".join(
        [
            "Snapshot Data Notes",
            "===================",
            "",
            "The v0 seed snapshot keeps public data summary files at the snapshot root with uppercase names.",
            "This data directory is explanatory only.",
            "No live data, private data, executable downloads, or external observations are stored here.",
            "",
        ]
    )


def _checksums(files: Mapping[str, str]) -> str:
    lines = []
    for relative in sorted(files):
        if relative == "CHECKSUMS.SHA256":
            continue
        digest = hashlib.sha256(files[relative].encode("utf-8")).hexdigest()
        lines.append(f"{digest}  {relative}")
    return "\n".join(lines) + "\n"


def _stable_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _summary_report(
    output_root: Path,
    data_root: Path,
    files: Mapping[str, str],
    *,
    updated: bool,
) -> dict[str, Any]:
    return {
        "status": "valid",
        "created_by": SLICE_ID,
        "generated_by": GENERATED_BY,
        "output_root": _display_path(output_root),
        "data_root": _display_path(data_root),
        "snapshot_format_version": SNAPSHOT_FORMAT_VERSION,
        "file_count": len(files),
        "files": sorted(files),
        "checksum_file": "CHECKSUMS.SHA256",
        "production_signed_release": False,
        "real_signing_keys_present": False,
        "contains_real_binaries": False,
        "contains_live_backend": False,
        "contains_live_probes": False,
        "contains_external_observations": False,
        "updated": updated,
        "errors": [],
    }


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Static snapshot generation",
        f"status: {report['status']}",
        f"output_root: {report.get('output_root', _display_path(DEFAULT_OUTPUT_ROOT))}",
    ]
    if report.get("check_mode"):
        lines.append("check_mode: true")
    if report.get("file_count") is not None:
        lines.append(f"files: {report['file_count']}")
    if report.get("errors"):
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
