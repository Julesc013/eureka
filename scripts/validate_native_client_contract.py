from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
CONTRACT = PUBLICATION_DIR / "native_client_contract.json"
LANES = PUBLICATION_DIR / "native_client_lanes.json"
SURFACE_CAPABILITIES = PUBLICATION_DIR / "surface_capabilities.json"
CLIENT_PROFILES = PUBLICATION_DIR / "client_profiles.json"
SNAPSHOT_CONSUMER_CONTRACT = PUBLICATION_DIR / "snapshot_consumer_contract.json"
SNAPSHOT_CONSUMER_PROFILES = PUBLICATION_DIR / "snapshot_consumer_profiles.json"
RELAY_SURFACE = PUBLICATION_DIR / "relay_surface.json"
CLI_ROOT = REPO_ROOT / "surfaces" / "native" / "cli"
PUBLIC_DATA_ROOT = REPO_ROOT / "site/dist" / "data"
SNAPSHOT_ROOT = REPO_ROOT / "snapshots" / "examples" / "static_snapshot_v0"

REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "native_client_contract_id",
    "status",
    "stability",
    "native_gui_implemented",
    "cli_surface_implemented",
    "first_candidate_lane",
    "required_inputs",
    "optional_inputs",
    "prohibited_behaviors_v0",
    "required_verification_behaviors",
    "allowed_actions_future",
    "disallowed_actions_until_policy",
    "snapshot_dependency",
    "public_data_dependency",
    "live_backend_dependency",
    "relay_dependency",
    "rust_dependency_status",
    "python_oracle_status",
    "client_lane_policy",
    "minimum_native_client_profile",
    "full_native_client_profile",
    "created_by_slice",
    "notes",
}
REQUIRED_LANE_IDS = {
    "windows_7_x64_winforms_net48",
    "windows_xp_x86_win32_unicode",
    "windows_95_nt4_x86_win32_ansi",
    "windows_win16_research",
    "windows_modern_winui_future",
    "macos_10_6_10_15_intel_appkit",
    "macos_11_plus_modern",
    "macos_10_4_10_5_ppc_intel_research",
    "classic_mac_7_1_9_2_research",
}
FUTURE_LANE_STATUSES = {"future", "future_deferred", "deferred", "lab_verify", "research", "design_only"}
PROJECT_SUFFIXES = {
    ".sln",
    ".vcxproj",
    ".csproj",
    ".xcodeproj",
    ".xcworkspace",
    ".pbxproj",
}
REQUIRED_DOC_PHRASES = {
    "docs/reference/NATIVE_CLIENT_CONTRACT.md": [
        "does not create a Visual Studio project",
        "does not create a native GUI",
        "CLI remains the only current local native-like surface",
        "Native clients are future super-clients, not website wrappers",
        "Those actions are prohibited until Native Action / Download / Install Policy v0",
    ],
    "docs/reference/NATIVE_CLIENT_LANES.md": [
        "Windows 7 x64 WinForms is the first pragmatic native client candidate",
        "Win16 does not run natively on x64 or ARM64 Windows",
        "Catalina does not force a split by itself",
        "No Visual Studio project",
        "No lane may claim",
    ],
    "docs/operations/NATIVE_CLIENT_READINESS_CHECKLIST.md": [
        "Status: future/unsigned",
        "Action, security, rights, download, and install policy exists",
        "No private data is consumed by default",
        "No Rust FFI or runtime wiring is assumed",
    ],
}
POSITIVE_NATIVE_CLAIMS = (
    re.compile(r"\bnative (gui )?client(s)? (is|are) implemented\b", re.IGNORECASE),
    re.compile(r"\bwindows native client (is )?(implemented|available)\b", re.IGNORECASE),
    re.compile(r"\bmac(os)? native client (is )?(implemented|available)\b", re.IGNORECASE),
    re.compile(r"\bproduction native client\b", re.IGNORECASE),
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Native Client Contract v0.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_native_client_contract(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_native_client_contract(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    publication_dir = repo_root / "control" / "inventory" / "publication"

    contract = _load_json(publication_dir / "native_client_contract.json", repo_root, errors)
    lanes = _load_json(publication_dir / "native_client_lanes.json", repo_root, errors)
    capabilities = _load_json(publication_dir / "surface_capabilities.json", repo_root, errors)
    client_profiles = _load_json(publication_dir / "client_profiles.json", repo_root, errors)
    snapshot_contract = _load_json(publication_dir / "snapshot_consumer_contract.json", repo_root, errors)
    snapshot_profiles = _load_json(publication_dir / "snapshot_consumer_profiles.json", repo_root, errors)
    relay_surface = _load_json(publication_dir / "relay_surface.json", repo_root, errors)

    lane_ids = _validate_contract(contract, repo_root, errors)
    actual_lane_ids = _validate_lanes(lanes, errors)
    _validate_related_inventories(capabilities, client_profiles, snapshot_contract, snapshot_profiles, relay_surface, errors)
    _validate_docs(repo_root, errors)
    project_paths = _validate_no_native_project_files(repo_root, errors)

    if lane_ids and actual_lane_ids and lane_ids - actual_lane_ids:
        errors.append(f"native_client_contract.json: referenced lanes missing from native_client_lanes.json: {sorted(lane_ids - actual_lane_ids)}.")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "native_client_contract_validator_v0",
        "contract": "control/inventory/publication/native_client_contract.json",
        "lanes": "control/inventory/publication/native_client_lanes.json",
        "lane_count": len(actual_lane_ids),
        "lane_ids": sorted(actual_lane_ids),
        "first_candidate_lane": _mapping(contract).get("first_candidate_lane"),
        "native_gui_implemented": _mapping(contract).get("native_gui_implemented"),
        "cli_surface_implemented": _mapping(contract).get("cli_surface_implemented"),
        "project_file_count": len(project_paths),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_contract(payload: Any, repo_root: Path, errors: list[str]) -> set[str]:
    referenced_lanes: set[str] = set()
    if not isinstance(payload, Mapping):
        errors.append("native_client_contract.json: must be a JSON object.")
        return referenced_lanes
    missing = sorted(REQUIRED_CONTRACT_FIELDS - set(payload))
    if missing:
        errors.append(f"native_client_contract.json: missing fields {missing}.")
    expected_scalars = {
        "schema_version": "0.1.0",
        "native_client_contract_id": "eureka-native-client-contract",
        "status": "design_only",
        "stability": "experimental",
        "native_gui_implemented": False,
        "cli_surface_implemented": True,
        "first_candidate_lane": "windows_7_x64_winforms_net48",
        "created_by_slice": "native_client_contract_v0",
    }
    for key, expected in expected_scalars.items():
        if payload.get(key) != expected:
            errors.append(f"native_client_contract.json: {key} must be {expected!r}.")

    cli_exists = (repo_root / "surfaces" / "native" / "cli").is_dir()
    if payload.get("cli_surface_implemented") is not cli_exists:
        errors.append("native_client_contract.json: cli_surface_implemented must match surfaces/native/cli existence.")

    input_ids = {str(item.get("id")) for item in _mapping_list(payload.get("required_inputs"))}
    for required_id in ("public_data_summaries", "snapshot_consumer_contract", "client_profile_contract"):
        if required_id not in input_ids:
            errors.append(f"native_client_contract.json: required_inputs missing {required_id}.")
    if not (repo_root / "site/dist" / "data").is_dir():
        errors.append("site/dist/data: required public data dependency is missing.")
    if not (repo_root / "snapshots" / "examples" / "static_snapshot_v0").is_dir():
        errors.append("snapshots/examples/static_snapshot_v0: snapshot seed dependency is missing.")

    prohibited = {str(item).casefold() for item in _list(payload.get("prohibited_behaviors_v0"))}
    for required in (
        "visual studio project creation",
        "xcode project creation",
        "native gui implementation",
        "installer automation",
        "download automation",
        "execution automation",
        "ffi binding",
        "rust runtime wiring",
    ):
        if required not in prohibited:
            errors.append(f"native_client_contract.json: prohibited_behaviors_v0 missing {required!r}.")

    blocked_actions = {str(item).casefold() for item in _list(payload.get("disallowed_actions_until_policy"))}
    for required in ("download executable artifacts", "run installers", "install software", "modify package manager state"):
        if required not in blocked_actions:
            errors.append(f"native_client_contract.json: disallowed_actions_until_policy missing {required!r}.")

    snapshot = _mapping(payload.get("snapshot_dependency"))
    if snapshot.get("consumer_contract") != "docs/reference/SNAPSHOT_CONSUMER_CONTRACT.md":
        errors.append("native_client_contract.json: snapshot_dependency.consumer_contract must reference snapshot consumer docs.")
    if snapshot.get("production_signing_required_before_authenticity_claims") is not True:
        errors.append("native_client_contract.json: production signing must be required before authenticity claims.")

    live = _mapping(payload.get("live_backend_dependency"))
    if live.get("status") not in {"future_disabled", "future", "deferred", "planned"}:
        errors.append("native_client_contract.json: live_backend_dependency must remain future/disabled.")
    if live.get("production_api_guarantee") is not False:
        errors.append("native_client_contract.json: live backend dependency must not claim production API guarantee.")

    relay = _mapping(payload.get("relay_dependency"))
    if relay.get("status") not in {"future_deferred", "future", "deferred", "planned"}:
        errors.append("native_client_contract.json: relay_dependency must remain future/deferred.")
    if relay.get("native_sidecar_implemented") is not False:
        errors.append("native_client_contract.json: relay native sidecar must not be implemented.")

    rust = _mapping(payload.get("rust_dependency_status"))
    if rust.get("status") != "parity_only_unwired":
        errors.append("native_client_contract.json: rust_dependency_status.status must be parity_only_unwired.")
    if rust.get("native_ffi_implemented") is not False:
        errors.append("native_client_contract.json: native FFI must not be implemented.")
    if rust.get("production_rust_backend") is not False:
        errors.append("native_client_contract.json: Rust must not be claimed as production backend.")

    lane_policy = _mapping(payload.get("client_lane_policy"))
    if lane_policy.get("all_gui_lanes_future") is not True:
        errors.append("native_client_contract.json: all_gui_lanes_future must be true.")
    if lane_policy.get("no_lane_implemented_by_v0") is not True:
        errors.append("native_client_contract.json: no_lane_implemented_by_v0 must be true.")
    referenced_lanes.add(str(lane_policy.get("first_candidate_lane", "")))
    referenced_lanes.add(str(payload.get("first_candidate_lane", "")))
    return {lane for lane in referenced_lanes if lane}


def _validate_lanes(payload: Any, errors: list[str]) -> set[str]:
    lane_ids: set[str] = set()
    if not isinstance(payload, Mapping):
        errors.append("native_client_lanes.json: must be a JSON object.")
        return lane_ids
    expected = {
        "schema_version": "0.1.0",
        "registry_id": "eureka-native-client-lanes",
        "status": "design_only",
        "stability": "experimental",
        "created_by_slice": "native_client_contract_v0",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append(f"native_client_lanes.json: {key} must be {value!r}.")
    lanes = payload.get("lanes")
    if not isinstance(lanes, list) or not lanes:
        errors.append("native_client_lanes.json: lanes must be a non-empty list.")
        return lane_ids
    for lane in lanes:
        if not isinstance(lane, Mapping):
            errors.append("native_client_lanes.json: each lane must be an object.")
            continue
        lane_id = lane.get("lane_id")
        if not isinstance(lane_id, str) or not lane_id:
            errors.append("native_client_lanes.json: lane_id must be a non-empty string.")
            continue
        lane_ids.add(lane_id)
        for field in (
            "platform_family",
            "target_os_range",
            "architecture",
            "implementation_stack",
            "status",
            "verification_status",
            "first_allowed_scope",
            "prohibited_scope",
            "depends_on",
            "notes",
        ):
            if field not in lane:
                errors.append(f"native_client_lanes.json: {lane_id} missing {field}.")
        if lane.get("status") not in FUTURE_LANE_STATUSES:
            errors.append(f"native_client_lanes.json: {lane_id}.status must remain future/deferred/lab-verify/research.")
        lane_text = json.dumps(lane, sort_keys=True).casefold()
        if "implemented" in str(lane.get("status", "")).casefold():
            errors.append(f"native_client_lanes.json: {lane_id}.status must not claim implemented.")
        for forbidden in ("installer automation", "download execution", "private data by default"):
            if forbidden not in lane_text:
                errors.append(f"native_client_lanes.json: {lane_id} should prohibit {forbidden}.")
    missing = sorted(REQUIRED_LANE_IDS - lane_ids)
    if missing:
        errors.append(f"native_client_lanes.json: missing required lanes {missing}.")
    if "windows_7_x64_winforms_net48" in lane_ids:
        first_lane = next((item for item in lanes if isinstance(item, Mapping) and item.get("lane_id") == "windows_7_x64_winforms_net48"), {})
        if _mapping(first_lane).get("status") != "future":
            errors.append("native_client_lanes.json: windows_7_x64_winforms_net48 must be future first candidate, not implemented.")
    return lane_ids


def _validate_related_inventories(
    capabilities: Any,
    client_profiles: Any,
    snapshot_contract: Any,
    snapshot_profiles: Any,
    relay_surface: Any,
    errors: list[str],
) -> None:
    caps_by_id = _by_id(_mapping(capabilities).get("capabilities"))
    native = _mapping(caps_by_id.get("native_client"))
    native_alias = _mapping(caps_by_id.get("native_clients"))
    cli = _mapping(caps_by_id.get("cli"))
    if native.get("status") not in {"deferred", "planned", "future_deferred"}:
        errors.append("surface_capabilities.json: native_client must remain deferred/planned.")
    native_text = json.dumps(native, sort_keys=True).casefold()
    if "native client contract" not in native_text:
        errors.append("surface_capabilities.json: native_client capability should reference Native Client Contract v0.")
    if native.get("enabled_by_default") is not False:
        errors.append("surface_capabilities.json: native_client.enabled_by_default must be false.")
    if native.get("supports_downloads") is not False:
        errors.append("surface_capabilities.json: native_client.supports_downloads must be false.")
    if native.get("supports_private_user_state") is not False:
        errors.append("surface_capabilities.json: native_client.supports_private_user_state must be false.")
    if cli.get("status") != "implemented":
        errors.append("surface_capabilities.json: cli must remain implemented.")
    if native_alias and native_alias.get("status") not in {"deferred", "planned", "future_deferred"}:
        errors.append("surface_capabilities.json: native_clients alias must remain deferred/planned.")

    profiles_by_id = _by_id(_mapping(client_profiles).get("profiles"))
    native_profile = _mapping(profiles_by_id.get("native_client"))
    if native_profile.get("status") not in {"deferred", "planned", "future_deferred"}:
        errors.append("client_profiles.json: native_client profile must remain deferred/planned.")
    profile_text = json.dumps(native_profile, sort_keys=True).casefold()
    if "native client contract" not in profile_text:
        errors.append("client_profiles.json: native_client profile should reference Native Client Contract v0.")
    if "installer automation" not in profile_text:
        errors.append("client_profiles.json: native_client profile should prohibit installer automation.")

    snapshot_text = json.dumps(snapshot_contract, sort_keys=True).casefold()
    if "native client contract" not in snapshot_text:
        errors.append("snapshot_consumer_contract.json: should reference Native Client Contract v0 for native consumers.")

    profile_entries = _by_id(_mapping(snapshot_profiles).get("profiles"))
    native_snapshot = _mapping(profile_entries.get("native_snapshot_consumer"))
    if native_snapshot.get("status") not in {"future_deferred", "future", "deferred", "design_only"}:
        errors.append("snapshot_consumer_profiles.json: native_snapshot_consumer must remain future/deferred.")

    relay_text = json.dumps(relay_surface, sort_keys=True).casefold()
    if "native client contract" not in relay_text:
        errors.append("relay_surface.json: should reference Native Client Contract v0 before native sidecar work.")


def _validate_docs(repo_root: Path, errors: list[str]) -> None:
    combined_text_parts: list[str] = []
    for relative, phrases in REQUIRED_DOC_PHRASES.items():
        path = repo_root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            errors.append(f"{relative}: required native client document is missing.")
            continue
        combined_text_parts.append(text)
        lowered = text.casefold()
        for phrase in phrases:
            if phrase.casefold() not in lowered:
                errors.append(f"{relative}: missing phrase {phrase!r}.")
    combined = "\n".join(combined_text_parts)
    for pattern in POSITIVE_NATIVE_CLAIMS:
        for match in pattern.finditer(combined):
            context = combined[max(0, match.start() - 80) : match.end() + 80].casefold()
            if any(token in context for token in ("no ", "not ", "future", "deferred", "does not", "there are no")):
                continue
            errors.append(f"native client docs include forbidden positive claim {match.group(0)!r}.")


def _validate_no_native_project_files(repo_root: Path, errors: list[str]) -> list[str]:
    offenders: list[str] = []
    for path in repo_root.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.suffix.casefold() in PROJECT_SUFFIXES:
            offenders.append(_rel(path, repo_root))
    for offender in offenders:
        errors.append(f"{offender}: native project file/directory is not allowed by Native Client Contract v0.")
    return offenders


def _load_json(path: Path, repo_root: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path, repo_root)}: missing JSON file.")
    except json.JSONDecodeError as error:
        errors.append(f"{_rel(path, repo_root)}: invalid JSON: {error}.")
    return {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _by_id(value: Any) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    if not isinstance(value, list):
        return result
    for item in value:
        if isinstance(item, Mapping) and isinstance(item.get("id"), str):
            result[item["id"]] = item
    return result


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Native client contract validation",
        f"status: {report['status']}",
        f"lanes: {report['lane_count']}",
        f"first_candidate_lane: {report['first_candidate_lane']}",
        f"native_gui_implemented: {report['native_gui_implemented']}",
        f"cli_surface_implemented: {report['cli_surface_implemented']}",
        f"native_project_files: {report['project_file_count']}",
    ]
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
