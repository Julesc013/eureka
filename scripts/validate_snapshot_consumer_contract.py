from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
CONTRACT = PUBLICATION_DIR / "snapshot_consumer_contract.json"
PROFILES = PUBLICATION_DIR / "snapshot_consumer_profiles.json"
SNAPSHOT_CONTRACT = PUBLICATION_DIR / "snapshot_contract.json"
RELAY_SURFACE = PUBLICATION_DIR / "relay_surface.json"
SURFACE_CAPABILITIES = PUBLICATION_DIR / "surface_capabilities.json"
CLIENT_PROFILES = PUBLICATION_DIR / "client_profiles.json"
SEED_SNAPSHOT_ROOT = REPO_ROOT / "snapshots" / "examples" / "static_snapshot_v0"
CONTRACT_DOC = REPO_ROOT / "docs" / "reference" / "SNAPSHOT_CONSUMER_CONTRACT.md"

REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "consumer_contract_id",
    "status",
    "stability",
    "snapshot_format_dependency",
    "production_consumer_implemented",
    "native_consumer_implemented",
    "relay_consumer_implemented",
    "minimum_consumer_profile",
    "full_consumer_profile",
    "required_read_order",
    "required_validation_steps",
    "optional_validation_steps",
    "checksum_policy",
    "signature_policy",
    "missing_optional_file_policy",
    "unsupported_feature_policy",
    "client_profiles",
    "prohibited_assumptions",
    "created_by_slice",
    "notes",
}
REQUIRED_READ_ORDER = [
    "README_FIRST.txt",
    "SNAPSHOT_MANIFEST.json",
    "BUILD_MANIFEST.json",
    "CHECKSUMS.SHA256",
    "SOURCE_SUMMARY.json",
    "EVAL_SUMMARY.json",
    "ROUTE_SUMMARY.json",
    "PAGE_REGISTRY.json",
]
REQUIRED_PROFILE_IDS = {
    "minimal_file_tree_consumer",
    "text_snapshot_consumer",
    "lite_html_snapshot_consumer",
    "relay_snapshot_consumer",
    "native_snapshot_consumer",
    "audit_tool_consumer",
}
DESIGN_ONLY_STATUSES = {
    "design_only",
    "future",
    "future_deferred",
    "deferred",
    "planned",
}
FORBIDDEN_KEY_SUFFIXES = {
    ".pem",
    ".key",
    ".pfx",
    ".p12",
    ".crt",
    ".cer",
}
POSITIVE_CONSUMER_CLAIMS = (
    re.compile(r"\bsnapshot consumer (is )?(implemented|available|production-ready)\b", re.IGNORECASE),
    re.compile(r"\bnative snapshot consumer (is )?(implemented|available)\b", re.IGNORECASE),
    re.compile(r"\brelay snapshot consumer (is )?(implemented|available)\b", re.IGNORECASE),
    re.compile(r"\bproduction snapshot consumer\b", re.IGNORECASE),
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Signed Snapshot Consumer Contract v0.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_snapshot_consumer_contract(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_snapshot_consumer_contract(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    publication_dir = repo_root / "control" / "inventory" / "publication"
    seed_root = repo_root / "snapshots" / "examples" / "static_snapshot_v0"

    contract = _load_json(publication_dir / "snapshot_consumer_contract.json", repo_root, errors)
    profiles = _load_json(publication_dir / "snapshot_consumer_profiles.json", repo_root, errors)
    snapshot_contract = _load_json(publication_dir / "snapshot_contract.json", repo_root, errors)
    relay_surface = _load_json(publication_dir / "relay_surface.json", repo_root, errors)
    surface_capabilities = _load_json(publication_dir / "surface_capabilities.json", repo_root, errors)
    client_profiles = _load_json(publication_dir / "client_profiles.json", repo_root, errors)

    _validate_contract(contract, seed_root, errors)
    profile_ids = _validate_profiles(profiles, errors)
    _validate_related_inventories(snapshot_contract, relay_surface, surface_capabilities, client_profiles, errors)
    _validate_docs(repo_root, errors)
    _validate_no_key_files(repo_root, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "snapshot_consumer_contract_validator_v0",
        "contract": "control/inventory/publication/snapshot_consumer_contract.json",
        "profiles": "control/inventory/publication/snapshot_consumer_profiles.json",
        "seed_snapshot_root": "snapshots/examples/static_snapshot_v0",
        "required_read_order": REQUIRED_READ_ORDER,
        "profile_count": len(profile_ids),
        "profile_ids": sorted(profile_ids),
        "production_consumer_implemented": _mapping(contract).get("production_consumer_implemented"),
        "native_consumer_implemented": _mapping(contract).get("native_consumer_implemented"),
        "relay_consumer_implemented": _mapping(contract).get("relay_consumer_implemented"),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_contract(payload: Any, seed_root: Path, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("snapshot_consumer_contract.json: must be a JSON object.")
        return
    missing = sorted(REQUIRED_CONTRACT_FIELDS - set(payload))
    if missing:
        errors.append(f"snapshot_consumer_contract.json: missing fields {missing}.")
    expected_scalars = {
        "schema_version": "0.1.0",
        "consumer_contract_id": "eureka-static-snapshot-consumer-contract",
        "status": "design_only",
        "stability": "experimental",
        "production_consumer_implemented": False,
        "native_consumer_implemented": False,
        "relay_consumer_implemented": False,
        "created_by_slice": "signed_snapshot_consumer_contract_v0",
    }
    for key, expected in expected_scalars.items():
        if payload.get(key) != expected:
            errors.append(f"snapshot_consumer_contract.json: {key} must be {expected!r}.")

    dependency = _mapping(payload.get("snapshot_format_dependency"))
    if dependency.get("snapshot_format_version") != "0.1.0":
        errors.append("snapshot_consumer_contract.json: snapshot_format_dependency.snapshot_format_version must be 0.1.0.")
    if dependency.get("seed_example_root") != "snapshots/examples/static_snapshot_v0":
        errors.append("snapshot_consumer_contract.json: seed_example_root must reference the repo seed snapshot.")

    read_order = payload.get("required_read_order")
    if read_order != REQUIRED_READ_ORDER:
        errors.append("snapshot_consumer_contract.json: required_read_order must match the v0 contract order.")
    for relative in REQUIRED_READ_ORDER:
        if not (seed_root / relative).is_file():
            errors.append(f"snapshots/examples/static_snapshot_v0/{relative}: required read-order file is missing.")

    minimum = _mapping(payload.get("minimum_consumer_profile"))
    if minimum.get("profile_id") != "minimal_file_tree_consumer":
        errors.append("snapshot_consumer_contract.json: minimum_consumer_profile.profile_id must be minimal_file_tree_consumer.")
    if minimum.get("requires_live_backend") is not False:
        errors.append("snapshot_consumer_contract.json: minimum consumer must not require a live backend.")

    checksum = _mapping(payload.get("checksum_policy"))
    if checksum.get("algorithm") != "sha256":
        errors.append("snapshot_consumer_contract.json: checksum_policy.algorithm must be sha256.")
    if checksum.get("required_for_compliant_consumers") is not True:
        errors.append("snapshot_consumer_contract.json: checksum verification must be required for compliant consumers.")

    signature = _mapping(payload.get("signature_policy"))
    if signature.get("status") != "placeholder_only":
        errors.append("snapshot_consumer_contract.json: signature_policy.status must be placeholder_only.")
    if signature.get("can_verify_real_signatures_in_v0") is not False:
        errors.append("snapshot_consumer_contract.json: v0 consumers must not claim real signature verification.")
    if signature.get("real_signing_keys_expected_in_repo") is not False:
        errors.append("snapshot_consumer_contract.json: real signing keys must not be expected in repo.")

    prohibited = {str(item).casefold() for item in _list(payload.get("prohibited_assumptions"))}
    for required in (
        "snapshot consumption is implemented",
        "native clients are implemented",
        "relay consumption is implemented",
        "v0 signatures are real production signatures",
        "snapshots include executable downloads",
    ):
        if required not in prohibited:
            errors.append(f"snapshot_consumer_contract.json: prohibited_assumptions missing {required!r}.")


def _validate_profiles(payload: Any, errors: list[str]) -> set[str]:
    profile_ids: set[str] = set()
    if not isinstance(payload, Mapping):
        errors.append("snapshot_consumer_profiles.json: must be a JSON object.")
        return profile_ids
    if payload.get("schema_version") != "0.1.0":
        errors.append("snapshot_consumer_profiles.json: schema_version must be 0.1.0.")
    if payload.get("status") != "design_only":
        errors.append("snapshot_consumer_profiles.json: status must be design_only.")
    profiles = payload.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        errors.append("snapshot_consumer_profiles.json: profiles must be a non-empty list.")
        return profile_ids
    for item in profiles:
        if not isinstance(item, Mapping):
            errors.append("snapshot_consumer_profiles.json: each profile must be an object.")
            continue
        profile_id = item.get("id")
        if not isinstance(profile_id, str) or not profile_id:
            errors.append("snapshot_consumer_profiles.json: profile id must be a non-empty string.")
            continue
        profile_ids.add(profile_id)
        if item.get("status") not in DESIGN_ONLY_STATUSES:
            errors.append(f"snapshot_consumer_profiles.json: {profile_id}.status must remain design/future/deferred.")
        implementation = str(item.get("current_implementation_status", "")).casefold()
        if "implemented runtime" in implementation or implementation == "implemented":
            errors.append(f"snapshot_consumer_profiles.json: {profile_id} must not claim implemented runtime consumer status.")
        if item.get("can_verify_signatures") is not False:
            errors.append(f"snapshot_consumer_profiles.json: {profile_id}.can_verify_signatures must be false for v0.")
        if item.get("can_handle_private_data") is not False:
            errors.append(f"snapshot_consumer_profiles.json: {profile_id}.can_handle_private_data must be false.")
        if item.get("requires_live_backend") is not False:
            errors.append(f"snapshot_consumer_profiles.json: {profile_id}.requires_live_backend must be false.")
        if not _list(item.get("required_files")):
            errors.append(f"snapshot_consumer_profiles.json: {profile_id}.required_files must be non-empty.")
    missing = sorted(REQUIRED_PROFILE_IDS - profile_ids)
    if missing:
        errors.append(f"snapshot_consumer_profiles.json: missing profiles {missing}.")
    return profile_ids


def _validate_related_inventories(
    snapshot_contract: Any,
    relay_surface: Any,
    surface_capabilities: Any,
    client_profiles: Any,
    errors: list[str],
) -> None:
    snapshot = _mapping(snapshot_contract)
    notes = "\n".join(str(item) for item in _list(snapshot.get("notes"))).casefold()
    if "consumer" not in notes:
        errors.append("snapshot_contract.json: notes should reference the consumer contract.")

    relay = _mapping(relay_surface)
    if relay.get("no_relay_implemented") is not True:
        errors.append("relay_surface.json: no_relay_implemented must remain true.")
    relay_text = json.dumps(relay, sort_keys=True).casefold()
    if "snapshot consumer" not in relay_text:
        errors.append("relay_surface.json: should reference snapshot consumer policy before relay runtime.")

    capabilities = _mapping(surface_capabilities).get("capabilities")
    if isinstance(capabilities, list):
        by_id = {item.get("id"): item for item in capabilities if isinstance(item, Mapping)}
        snapshots = _mapping(by_id.get("snapshots"))
        relay_cap = _mapping(by_id.get("relay"))
        native = _mapping(by_id.get("native_client"))
        if "consumer contract" not in json.dumps(snapshots, sort_keys=True).casefold():
            errors.append("surface_capabilities.json: snapshots capability should reference consumer contract.")
        if relay_cap.get("status") not in {"deferred", "planned", "future_deferred"}:
            errors.append("surface_capabilities.json: relay must remain deferred/planned.")
        if native.get("status") not in {"deferred", "planned", "future_deferred"}:
            errors.append("surface_capabilities.json: native_client must remain deferred/planned.")
    else:
        errors.append("surface_capabilities.json: capabilities must be a list.")

    profiles = _mapping(client_profiles).get("profiles")
    if isinstance(profiles, list):
        by_id = {item.get("id"): item for item in profiles if isinstance(item, Mapping)}
        snapshot_profile = _mapping(by_id.get("snapshot"))
        if "consumer contract" not in json.dumps(snapshot_profile, sort_keys=True).casefold():
            errors.append("client_profiles.json: snapshot profile should reference the consumer contract.")
    else:
        errors.append("client_profiles.json: profiles must be a list.")


def _validate_docs(repo_root: Path, errors: list[str]) -> None:
    doc_paths = [
        repo_root / "docs" / "reference" / "SNAPSHOT_CONSUMER_CONTRACT.md",
        repo_root / "docs" / "reference" / "SNAPSHOT_FORMAT_CONTRACT.md",
        repo_root / "docs" / "reference" / "SNAPSHOT_SIGNATURE_POLICY.md",
    ]
    for path in doc_paths:
        if not path.is_file():
            errors.append(f"{_rel(path, repo_root)}: required doc is missing.")
            continue
    text = "\n".join(
        path.read_text(encoding="utf-8") for path in doc_paths if path.is_file()
    ).casefold()
    required_phrases = [
        "no production consumer",
        "v0 signatures are placeholders",
        "no real signing keys",
        "no private keys are stored",
        "does not implement a snapshot reader runtime",
        "does not implement a relay",
        "does not implement a native client",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            errors.append(f"snapshot consumer docs missing phrase {phrase!r}.")
    for claim in POSITIVE_CONSUMER_CLAIMS:
        if claim.search(text):
            errors.append(f"snapshot consumer docs include forbidden positive claim: {claim.pattern}")


def _validate_no_key_files(repo_root: Path, errors: list[str]) -> None:
    for path in repo_root.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        suffix = path.suffix.casefold()
        if suffix in FORBIDDEN_KEY_SUFFIXES:
            errors.append(f"{_rel(path, repo_root)}: key/certificate-like file is not allowed for this contract.")


def _load_json(path: Path, repo_root: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path, repo_root)}: missing JSON file.")
    except json.JSONDecodeError as error:
        errors.append(f"{_rel(path, repo_root)}: invalid JSON: {error}")
    return {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Snapshot consumer contract validation",
        f"status: {report['status']}",
        f"profiles: {report['profile_count']}",
        f"production_consumer_implemented: {report['production_consumer_implemented']}",
        f"native_consumer_implemented: {report['native_consumer_implemented']}",
        f"relay_consumer_implemented: {report['relay_consumer_implemented']}",
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
        return str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
