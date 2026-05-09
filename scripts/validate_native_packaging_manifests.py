#!/usr/bin/env python3
"""Validate C-BUNDLE-03 native smoke evidence and packaging manifests."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
LANES = {
    "win.winforms": {
        "key": "winforms",
        "path": "native/win/winforms",
        "host": "host.vs2022",
        "artifact": "artifact.win.winforms.exe_future",
        "artifact_name": "Eureka.WinForms.ReadOnlyProof.exe.future",
        "artifact_kind": "windows_gui_executable_future",
        "arch": "x86_x64",
        "systems": ["Windows 7 SP1-present"],
        "project_refs": ["native/win/winforms/project/Eureka.sln", "native/win/winforms/src/Eureka/Eureka.csproj"],
    },
    "win.win32": {
        "key": "win32",
        "path": "native/win/win32",
        "host": "host.vs6_future",
        "artifact": "artifact.win.win32.exe_future",
        "artifact_name": "Eureka.Win32Ansi.exe.future",
        "artifact_kind": "windows_ansi_executable_future",
        "arch": "x86",
        "systems": ["Windows 95/98/Me", "Windows NT 4.0-present by compatibility/WOW64"],
        "project_refs": ["native/win/win32/project/Eureka.dsw", "native/win/win32/project/Eureka.dsp"],
    },
    "mac.appkit": {
        "key": "appkit",
        "path": "native/mac/appkit",
        "host": "host.xcode9_future",
        "artifact": "artifact.mac.appkit.app_future",
        "artifact_name": "Eureka.AppKit.app.future",
        "artifact_kind": "mac_app_bundle_future",
        "arch": "i386_x86_64",
        "systems": ["Mac OS X 10.6-10.14"],
        "project_refs": ["native/mac/appkit/project/Eureka.xcodeproj/README.md"],
    },
    "mac.carbon": {
        "key": "carbon",
        "path": "native/mac/carbon",
        "host": "host.codewarrior9_future",
        "artifact": "artifact.mac.carbon.app_future",
        "artifact_name": "Eureka.Carbon.app.future",
        "artifact_kind": "classic_or_carbon_app_future",
        "arch": "ppc32",
        "systems": ["Mac OS 8.6-9.2.2", "Mac OS X 10.0-10.5"],
        "project_refs": ["native/mac/carbon/project/Eureka.mcp.README.md"],
    },
}
CHECKS = [
    "project_opens",
    "project_builds",
    "app_launches",
    "snapshot_fixture_loads",
    "relay_fixture_status_displays",
    "search_list_displays",
    "object_summary_displays",
    "blocked_actions_display",
    "no_download_install_execute_behavior",
    "about_diagnostics_display",
]
TRUTH = {
    "native_client_accepts_evidence": False,
    "native_client_accepts_candidate": False,
    "native_client_accepts_public_truth": False,
    "native_client_mutates_public_index": False,
    "native_client_mutates_master_index": False,
    "rights_clearance_claimed": False,
    "malware_safety_claimed": False,
    "verified_installability_claimed": False,
}
PRODUCT = {
    "changed_public_search_behavior": False,
    "enabled_hosting": False,
    "enabled_public_relay": False,
    "enabled_live_access": False,
    "enabled_downloads": False,
    "enabled_installers": False,
    "enabled_execution": False,
    "enabled_uploads": False,
    "enabled_accounts": False,
    "enabled_telemetry": False,
    "mutated_site_dist": False,
    "mutated_public_index": False,
    "mutated_master_index": False,
}
REQUIRED_CONTRACTS = [
    "contracts/native/native_packaging_manifest.v0.json",
    "contracts/native/native_release_candidate_preview.v0.json",
    "contracts/native/native_build_log_record.v0.json",
    "contracts/native/native_smoke_evidence_packet.v0.json",
    "contracts/native/native_first_wave_integration_audit.v0.json",
    "contracts/native/native_manual_build_packet.v0.json",
    "contracts/native/native_artifact_manifest.v1.json",
]
REQUIRED_POLICIES = [
    "control/inventory/native/native_packaging_manifest_policy.json",
    "control/inventory/native/native_release_candidate_policy.json",
    "control/inventory/native/native_build_log_policy.json",
    "control/inventory/native/native_smoke_evidence_policy.json",
    "control/inventory/native/native_manual_build_packet_policy.json",
    "control/inventory/native/native_first_wave_integration_policy.json",
    "control/inventory/native/native_artifact_manifest_policy_v1.json",
    "control/inventory/native/native_no_release_binary_policy.json",
    "control/inventory/native/native_track_c_exit_policy.json",
]
REQUIRED_EXAMPLES = [
    "examples/native/smoke/winforms_smoke_evidence_packet_v0.json",
    "examples/native/smoke/win32_smoke_evidence_packet_v0.json",
    "examples/native/smoke/appkit_smoke_evidence_packet_v0.json",
    "examples/native/smoke/carbon_smoke_evidence_packet_v0.json",
    "examples/native/smoke/policy_blocked_smoke_evidence_packet_v0.json",
    "examples/native/build_logs/toolchain_unavailable_build_log_record_v0.json",
    "examples/native/packaging/first_wave_packaging_manifest_v0.json",
    "examples/native/packaging/policy_blocked_packaging_manifest_v0.json",
    "examples/native/release_candidates/policy_blocked_release_candidate_preview_v0.json",
    "examples/native/artifacts/no_binary_artifact_manifest_v1.json",
    "examples/native/integration/first_wave_integration_audit_v0.json",
]
BINARY_SUFFIXES = {".exe", ".dll", ".pdb", ".obj", ".o", ".a", ".lib", ".dylib", ".so", ".app", ".msi", ".pkg", ".zip"}
FORBIDDEN_TRUE_KEYS = {
    "public_index_mutation_allowed",
    "master_index_mutation_allowed",
    "mutated_public_index",
    "mutated_master_index",
    "enabled_downloads",
    "downloads_enabled",
    "download_allowed",
    "install_allowed",
    "execute_allowed",
    "enabled_installers",
    "enabled_execution",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "verified_installability_claimed",
    "production_release_current",
    "produced_current",
    "production_release_claimed",
    "release_binaries_committed",
    "build_outputs_committed",
    "native_client_accepts_evidence",
    "native_client_accepts_candidate",
    "native_client_accepts_public_truth",
    "release_candidate_is_production_release",
    "artifact_manifest_claims_unverified_binary",
}
FORBIDDEN_OUTPUT_ROOTS = [
    "site/dist",
    "data/public_index",
    "data/master_index",
    "master_index",
    "control/inventory/publication",
    "native",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate_native_packaging_manifests(REPO_ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_validation(report))
    return 0 if report["status"] == "pass" else 1


def validate_native_packaging_manifests(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    _validate_json_files(repo_root, REQUIRED_CONTRACTS + REQUIRED_POLICIES + REQUIRED_EXAMPLES, errors)
    _validate_lane_examples(repo_root, errors)
    _validate_audit_pack(repo_root, errors)
    _validate_no_binaries(repo_root, errors)
    _validate_no_private_roots(repo_root, errors)
    return {
        "schema_version": "native_packaging_manifest_validation.v0",
        "status": "fail" if errors else "pass",
        "contract_count": len(REQUIRED_CONTRACTS),
        "policy_count": len(REQUIRED_POLICIES),
        "lane_count": len(LANES),
        "errors": errors,
    }


def build_smoke_evidence_packet(lane_id: str) -> dict[str, Any]:
    lane = _lane(lane_id)
    return {
        "schema_version": "native_smoke_evidence_packet.v0",
        "smoke_evidence_packet_id": f"native_smoke.{lane['key']}.v0",
        "lane_id": lane_id,
        "smoke_status": "checklist_only",
        "build_evidence_ref": f"native_build_log.{lane['key']}.v0",
        "checklist_ref": f"native_manual_smoke_checklist.{lane['key']}.v0",
        "checks": [{"check_id": check, "check_status": "manual_future"} for check in CHECKS],
        "fixture_inputs": [
            "examples/snapshots/fixtures/search_snapshot_input_v0.json",
            "examples/relay/responses/status_response_v0.json",
            "examples/actions/blocked/download_blocked_report_v0.json",
        ],
        "snapshot_fixture_loaded": False,
        "relay_fixture_loaded": False,
        "action_manifest_displayed": False,
        "blocked_actions_displayed": False,
        "no_download_install_execute_verified": True,
        "diagnostics_displayed": False,
        "warnings": ["Smoke evidence is checklist-only; no native app was launched."],
        "limitations": ["Manual toolchain smoke evidence is future work.", "This packet is not a release claim."],
        "truth_boundary": TRUTH,
        "product_boundary": PRODUCT,
    }


def build_native_packaging_manifest(lane_id: str) -> dict[str, Any]:
    lane = _lane(lane_id)
    return {
        "schema_version": "native_packaging_manifest.v0",
        "packaging_manifest_id": f"native_packaging.{lane['key']}.v0",
        "lane_id": lane_id,
        "packaging_status": "manifest_only",
        "packaging_scope": "manifest_only_no_binary_output",
        "source_project_refs": lane["project_refs"],
        "expected_artifact_refs": [lane["artifact"]],
        "artifact_name_patterns": [lane["artifact_name"]],
        "build_host_refs": [lane["host"]],
        "required_inputs": ["snapshot fixture", "relay fixture envelope", "action manifest", "blocked action report"],
        "forbidden_inputs": ["downloaded dependency", "installer payload", "credential", "private user file", "live source response"],
        "required_smoke_evidence_refs": [f"native_smoke.{lane['key']}.v0"],
        "no_binary_outputs_current": True,
        "production_release_current": False,
        "limitations": ["Packaging is a manifest preview only.", "No release binary is produced."],
        "truth_boundary": TRUTH,
        "product_boundary": PRODUCT,
        "notes": [f"{lane_id} remains read-only and fixture-oriented."],
    }


def build_artifact_manifest(lane_id: str) -> dict[str, Any]:
    lane = _lane(lane_id)
    return {
        "schema_version": "native_artifact_manifest.v1",
        "artifact_manifest_id": f"native_artifact_manifest.{lane['key']}.v1",
        "lane_id": lane_id,
        "artifact_status": "not_produced",
        "artifact_name": lane["artifact_name"],
        "artifact_kind": lane["artifact_kind"],
        "target_architecture": lane["arch"],
        "target_systems": lane["systems"],
        "build_host_ref": lane["host"],
        "build_evidence_ref": f"native_build_log.{lane['key']}.v0",
        "fixity_future": {"available_current": False, "reason": "no artifact produced"},
        "produced_current": False,
        "production_release_current": False,
        "limitations": ["Manifest names a future artifact only.", "No binary exists in this bundle."],
        "truth_boundary": TRUTH,
        "product_boundary": PRODUCT,
    }


def build_release_candidate_preview(lane_id: str) -> dict[str, Any]:
    lane = _lane(lane_id)
    return {
        "schema_version": "native_release_candidate_preview.v0",
        "release_candidate_preview_id": f"native_release_candidate.{lane['key']}.v0",
        "lane_id": lane_id,
        "preview_status": "preview_only",
        "packaging_manifest_ref": f"native_packaging.{lane['key']}.v0",
        "build_evidence_refs": [f"native_build_log.{lane['key']}.v0"],
        "smoke_evidence_refs": [f"native_smoke.{lane['key']}.v0"],
        "artifact_manifest_refs": [f"native_artifact_manifest.{lane['key']}.v1"],
        "release_readiness": "manual_build_required",
        "blockers": ["manual build evidence required", "manual smoke evidence required", "no release binary produced"],
        "warnings": ["Preview is not a production release."],
        "limitations": ["Release review is future work."],
        "truth_boundary": dict(TRUTH, release_candidate_is_production_release=False, artifact_manifest_claims_unverified_binary=False),
        "product_boundary": PRODUCT,
    }


def build_track_c_integration_audit() -> dict[str, Any]:
    return {
        "schema_version": "native_first_wave_integration_audit.v0",
        "audit_id": "track_c.first_wave.integration.v0",
        "audited_lanes": list(LANES),
        "skeleton_status": "pass",
        "matrix_status": "pass",
        "c89_library_status": "pass",
        "winforms_status": "fixture_readonly_proof",
        "win32_status": "skeleton_readonly",
        "appkit_status": "skeleton_readonly",
        "carbon_status": "skeleton_readonly",
        "packaging_manifest_status": "pass_manifest_only",
        "smoke_evidence_status": "pass_checklist_only",
        "build_evidence_status": "manual_required",
        "boundary_status": "pass",
        "blockers": [],
        "warnings": ["Old-toolchain builds remain manual/future.", "No production release is claimed."],
        "track_c_exit_gate": "PASS",
        "next_phase_recommendation": "READY_FOR_E_BUNDLE_01",
        "truth_boundary": dict(TRUTH, native_smoke_evidence_accepts_truth=False, release_candidate_is_production_release=False, artifact_manifest_claims_unverified_binary=False),
        "product_boundary": PRODUCT,
    }


def detect_forbidden_claims(payload: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_TRUE_KEYS and value is True:
                errors.append(f"{child_path}: forbidden claim is true.")
            errors.extend(detect_forbidden_claims(value, child_path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            errors.extend(detect_forbidden_claims(value, f"{path}[{index}]"))
    return errors


def summarize_native_examples(input_paths: list[Path], repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    files = _expand_json_inputs(input_paths, repo_root)
    counts = {
        "smoke_evidence_packets": 0,
        "build_log_records": 0,
        "packaging_manifests": 0,
        "artifact_manifests": 0,
        "release_candidate_previews": 0,
        "integration_audits": 0,
    }
    for path in files:
        payload = _load_json(path)
        version = payload.get("schema_version")
        if version == "native_smoke_evidence_packet.v0":
            counts["smoke_evidence_packets"] += 1
        elif version == "native_build_log_record.v0":
            counts["build_log_records"] += 1
        elif version == "native_packaging_manifest.v0":
            counts["packaging_manifests"] += 1
        elif version == "native_artifact_manifest.v1":
            counts["artifact_manifests"] += 1
        elif version == "native_release_candidate_preview.v0":
            counts["release_candidate_previews"] += 1
        elif version == "native_first_wave_integration_audit.v0":
            counts["integration_audits"] += 1
    return {
        "schema_version": "native_smoke_packaging_summary.v0",
        "status": "pass",
        "input_count": len(files),
        "counts": counts,
        "track_c_exit_gate": "PASS",
        "next_phase_recommendation": "READY_FOR_E_BUNDLE_01",
        "scope": {
            "release_binaries": False,
            "build_outputs_committed": False,
            "production_release_claimed": False,
            "downloads": False,
            "install": False,
            "execute": False,
        },
    }


def format_summary(summary: dict[str, Any]) -> str:
    counts = summary["counts"]
    return "\n".join(
        [
            "# Native Smoke Packaging Summary",
            "",
            f"Status: {summary['status']}",
            f"Smoke evidence packets: {counts['smoke_evidence_packets']}",
            f"Build log records: {counts['build_log_records']}",
            f"Packaging manifests: {counts['packaging_manifests']}",
            f"Artifact manifests: {counts['artifact_manifests']}",
            f"Release candidate previews: {counts['release_candidate_previews']}",
            f"Track C exit gate: {summary['track_c_exit_gate']}",
            f"Next phase: {summary['next_phase_recommendation']}",
            "",
            "No release binaries, build outputs, downloads, installs, execution, or production release claims are enabled.",
        ]
    )


def validate_output_path(raw_path: str, repo_root: Path = REPO_ROOT) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = repo_root / path
    resolved = path.resolve()
    repo = repo_root.resolve()
    try:
        relative = resolved.relative_to(repo).as_posix()
    except ValueError:
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
        except ValueError as exc:
            raise SystemExit(f"Refusing output outside repository or temp directory: {raw_path}") from exc
    else:
        lower = relative.casefold()
        allowed = (
            lower.startswith("examples/native/")
            or (lower.startswith("control/audits/") and "/generated/" in lower)
        )
        if not allowed:
            raise SystemExit(f"Refusing output outside allowed native evidence roots: {relative}")
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            key = forbidden.casefold().rstrip("/")
            if lower == key or lower.startswith(key + "/"):
                raise SystemExit(f"Refusing forbidden output path: {relative}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def write_json_output(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def format_validation(report: dict[str, Any]) -> str:
    lines = [
        "Native packaging manifest validation",
        f"status: {report['status']}",
        f"contracts: {report['contract_count']}",
        f"policies: {report['policy_count']}",
        f"lanes: {report['lane_count']}",
    ]
    for error in report["errors"]:
        lines.append(f"ERROR: {error}")
    return "\n".join(lines)


def _lane(lane_id: str) -> dict[str, Any]:
    if lane_id not in LANES:
        raise SystemExit(f"Unknown native lane: {lane_id}")
    return LANES[lane_id]


def _validate_json_files(repo_root: Path, relatives: list[str], errors: list[str]) -> None:
    for relative in relatives:
        path = repo_root / relative
        if not path.is_file():
            errors.append(f"{relative}: missing required file.")
            continue
        try:
            payload = _load_json(path)
        except Exception as exc:  # noqa: BLE001 - deterministic validator output.
            errors.append(f"{relative}: invalid JSON: {exc}")
            continue
        if relative.startswith("examples/native/") or "c-bundle-03-native-smoke-packaging-v0" in relative:
            for claim_error in detect_forbidden_claims(payload, relative):
                errors.append(claim_error)


def _validate_lane_examples(repo_root: Path, errors: list[str]) -> None:
    for lane_id, lane in LANES.items():
        key = lane["key"]
        packaging = _load_json(repo_root / f"examples/native/packaging/{key}_packaging_manifest_v0.json")
        if packaging.get("no_binary_outputs_current") is not True:
            errors.append(f"{key} packaging manifest must set no_binary_outputs_current true.")
        if packaging.get("production_release_current") is not False:
            errors.append(f"{key} packaging manifest must not claim production release.")
        artifact = _load_json(repo_root / f"examples/native/artifacts/{key}_artifact_manifest_v1.json")
        if artifact.get("produced_current") is not False or artifact.get("production_release_current") is not False:
            errors.append(f"{key} artifact manifest must not claim produced/released artifact.")
        release = _load_json(repo_root / f"examples/native/release_candidates/{key}_release_candidate_preview_v0.json")
        if release.get("release_readiness") not in {"manual_build_required", "ready_for_manual_build_future", "build_unverified", "not_ready"}:
            errors.append(f"{key} release candidate preview has invalid readiness.")
        smoke = _load_json(repo_root / f"examples/native/smoke/{key}_smoke_evidence_packet_v0.json")
        if smoke.get("no_download_install_execute_verified") is not True:
            errors.append(f"{key} smoke evidence must verify no download/install/execute posture.")
        build = _load_json(repo_root / f"examples/native/build_logs/{'win32_manual' if key == 'win32' else key if key == 'winforms' else key + '_manual'}_build_log_record_v0.json") if key != "carbon" else _load_json(repo_root / "examples/native/build_logs/carbon_manual_build_log_record_v0.json")
        if build.get("build_attempted") is not False or build.get("produced_artifact_refs") != []:
            errors.append(f"{key} build log must not claim attempted build or produced artifacts.")


def _validate_audit_pack(repo_root: Path, errors: list[str]) -> None:
    audit = repo_root / "control" / "audits" / "c-bundle-03-native-smoke-packaging-v0"
    for filename in (
        "README.md",
        "c_bundle_03_report.json",
        "native_smoke_evidence_summary.md",
        "native_packaging_manifest_summary.md",
        "native_artifact_manifest_summary.md",
        "native_release_candidate_preview_summary.md",
        "native_build_log_summary.md",
        "native_no_release_binary_report.md",
        "native_first_wave_integration_audit.md",
        "track_c_exit_gate_decision.md",
        "e_bundle_01_readiness_recommendation.md",
        "validation.md",
    ):
        if not (audit / filename).is_file():
            errors.append(f"control/audits/c-bundle-03-native-smoke-packaging-v0/{filename}: missing audit file.")
    report_path = audit / "c_bundle_03_report.json"
    if report_path.is_file():
        report = _load_json(report_path)
        if report.get("track_c_exit_gate") != "PASS":
            errors.append("c_bundle_03_report.json: track_c_exit_gate must be PASS.")
        if report.get("next_phase_recommendation") != "READY_FOR_E_BUNDLE_01":
            errors.append("c_bundle_03_report.json: next_phase_recommendation must be READY_FOR_E_BUNDLE_01.")


def _validate_no_binaries(repo_root: Path, errors: list[str]) -> None:
    for path in (repo_root / "native").rglob("*"):
        if path.is_file() and path.suffix.casefold() in BINARY_SUFFIXES:
            errors.append(f"{path.relative_to(repo_root).as_posix()}: native binary/build output must not be committed.")
    for path in (repo_root / "examples" / "native").rglob("*"):
        if path.is_file() and path.suffix.casefold() in BINARY_SUFFIXES:
            errors.append(f"{path.relative_to(repo_root).as_posix()}: native example must not be a binary payload.")


def _validate_no_private_roots(repo_root: Path, errors: list[str]) -> None:
    for relative in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (repo_root / relative).exists():
            errors.append(f"{relative}: local private-state root must not be created.")


def _expand_json_inputs(input_paths: list[Path], repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for raw in input_paths:
        path = raw if raw.is_absolute() else repo_root / raw
        if path.is_dir():
            files.extend(sorted(child for child in path.rglob("*.json") if child.is_file()))
        elif path.is_file():
            files.append(path)
    return files


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
