"""Policy helpers for J0 safe action manifests.

J0 action policy is deliberately descriptive. It validates whether an action
family is allowed to produce a manifest and builds common boundaries that keep
the runtime from implying execution, downloads, public-index mutation, or truth
acceptance.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_ROOT = REPO_ROOT / "control" / "inventory" / "actions"

SAFE_ACTIONS = {
    "view",
    "inspect",
    "compare",
    "cite",
    "export",
    "preserve_manifest",
    "acquisition_manifest",
    "blocked_action",
}
RISKY_ACTIONS = {"download", "mirror", "install", "execute", "emulate", "submit", "import"}
FUTURE_ACTIONS = {f"{item}_future" for item in RISKY_ACTIONS}
FORBIDDEN_EFFECTS = [
    "downloaded_file",
    "mirrored_file",
    "installed_artifact",
    "executed_artifact",
    "emulator_launch",
    "source_fetch",
    "accepted_evidence",
    "accepted_candidate",
    "accepted_public_record",
    "public_index_mutation",
    "master_index_mutation",
    "rights_clearance",
    "malware_safety",
    "verified_installability",
]
FORBIDDEN_TRUE_FIELDS = {
    "action_manifest_executes_action",
    "action_manifest_downloads_file",
    "action_manifest_installs_artifact",
    "action_manifest_runs_artifact",
    "action_manifest_mutates_public_index",
    "action_manifest_mutates_master_index",
    "acquisition_manifest_downloads_file",
    "acquisition_manifest_mirrors_file",
    "preservation_manifest_mirrors_file",
    "preservation_manifest_captures_file",
    "citation_bundle_accepts_truth",
    "export_manifest_imports_or_submits",
    "public_index_mutated",
    "master_index_mutated",
    "accepted_evidence",
    "accepted_candidate",
    "accepted_public_record",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "verified_installability_claimed",
    "compatibility_certification_claimed",
    "changed_public_search_behavior",
    "enabled_hosting",
    "enabled_downloads",
    "enabled_installers",
    "enabled_execution",
    "enabled_emulation",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "mutated_public_index",
    "mutated_master_index",
    "merge_allowed_current",
}


def load_action_policy(root: Path = REPO_ROOT) -> dict[str, Any]:
    names = [
        "action_taxonomy_policy",
        "safe_action_policy",
        "action_output_policy",
        "action_path_policy",
        "action_truth_policy",
        "acquisition_manifest_policy",
        "citation_bundle_policy",
        "export_manifest_policy",
        "preservation_manifest_policy",
        "blocked_action_policy",
        "future_risky_action_policy",
    ]
    policy_root = root / "control" / "inventory" / "actions"
    bundle = {name: load_json(policy_root / f"{name}.json") for name in names}
    path_policy = bundle["action_path_policy"]
    return {
        "schema_version": "action_policy_bundle.v0",
        **bundle,
        "safe_actions": list(bundle["safe_action_policy"].get("safe_actions_current", sorted(SAFE_ACTIONS))),
        "risky_actions": list(bundle["safe_action_policy"].get("risky_actions_future", sorted(RISKY_ACTIONS))),
        "allowed_output_roots": path_policy.get("allowed_output_roots", []),
        "forbidden_output_roots": path_policy.get("forbidden_output_roots", []),
    }


def validate_action_allowed(action_family: str, policy: Mapping[str, Any] | None = None) -> tuple[bool, list[str]]:
    family = normalize_action_family(action_family)
    safe = set((policy or {}).get("safe_actions", SAFE_ACTIONS))
    risky = set((policy or {}).get("risky_actions", RISKY_ACTIONS)) | FUTURE_ACTIONS
    if family in safe:
        return True, []
    if family in risky or family.removesuffix("_future") in RISKY_ACTIONS:
        return False, [
            f"{family} is disabled in J0",
            "future policy requires rights review, risk review, user confirmation, action audit, and no auto-run",
        ]
    return False, [f"unknown action family: {family}"]


def build_blocked_action_report(action_family: str, subject: Mapping[str, Any] | None, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    from runtime.actions.blocked_action import build_blocked_action_report as _build

    return _build(action_family, subject or {}, policy)


def action_truth_boundary() -> dict[str, bool]:
    return {
        "action_manifest_executes_action": False,
        "action_manifest_downloads_file": False,
        "action_manifest_installs_artifact": False,
        "action_manifest_runs_artifact": False,
        "action_manifest_mutates_public_index": False,
        "action_manifest_mutates_master_index": False,
        "acquisition_manifest_downloads_file": False,
        "acquisition_manifest_mirrors_file": False,
        "preservation_manifest_mirrors_file": False,
        "preservation_manifest_captures_file": False,
        "citation_bundle_accepts_truth": False,
        "export_manifest_imports_or_submits": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "accepted_evidence": False,
        "accepted_candidate": False,
        "accepted_public_record": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "compatibility_certification_claimed": False,
    }


def action_product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_downloads": False,
        "enabled_installers": False,
        "enabled_execution": False,
        "enabled_emulation": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def normalize_action_family(action_family: str) -> str:
    family = str(action_family).strip().casefold().replace("-", "_")
    aliases = {
        "export_manifest": "export",
        "preservation_manifest": "preserve_manifest",
        "preserve": "preserve_manifest",
        "acquire": "acquisition_manifest",
        "acquisition": "acquisition_manifest",
    }
    return aliases.get(family, family)


def subject_ref(subject: Mapping[str, Any] | None) -> str:
    subject = subject or {}
    for key in (
        "subject_ref",
        "action_manifest_id",
        "acquisition_manifest_id",
        "citation_bundle_id",
        "export_manifest_id",
        "preservation_manifest_id",
        "candidate_id",
        "source_record_id",
        "evidence_record_id",
        "pack_export_id",
        "search_need_id",
        "id",
    ):
        value = subject.get(key)
        if value:
            return str(value)
    return stable_id("action_subject", subject)


def subject_type(subject: Mapping[str, Any] | None) -> str:
    subject = subject or {}
    schema = str(subject.get("schema_version", ""))
    if schema:
        return schema.removesuffix(".v0")
    for key in ("subject_type", "result_kind", "export_subject_type", "input_pack_type"):
        if subject.get(key):
            return str(subject[key])
    return "local_fixture_record"


def detect_action_boundary_violations(value: Any) -> list[str]:
    violations: list[str] = []
    for path, key, child in iter_key_values(value):
        if key in FORBIDDEN_TRUE_FIELDS and child is True:
            violations.append(f"{path} must be false for J0 safe action artifacts")
    return sorted(dict.fromkeys(violations))


def ensure_allowed_output_path(path: str | Path, policy: Mapping[str, Any] | None = None, root: Path = REPO_ROOT) -> Path:
    resolved = resolve_path(path, root)
    if is_under_temp(resolved):
        return resolved
    rel = repo_relative_or_none(resolved, root)
    if rel is None:
        raise ValueError(f"refusing output outside repository approved roots or temp directory: {resolved}")
    rel_lower = rel.casefold().rstrip("/")
    forbidden = (policy or {}).get("forbidden_output_roots") or [
        "site/dist/",
        "site/dist/data/public_index/",
        "runtime/",
        "contracts/",
        "control/inventory/publication/",
        "master_index/",
        "data/master_index/",
        ".aide.local/",
        ".local/eureka/",
        ".cache/eureka/",
        "downloads/",
        "download/",
        "cache/",
        "staging/",
    ]
    for root_text in forbidden:
        candidate = str(root_text).casefold().rstrip("/")
        if rel_lower == candidate or rel_lower.startswith(candidate + "/"):
            raise ValueError(f"refusing forbidden output root: {root_text}")
    allowed = (policy or {}).get("allowed_output_roots") or [
        "control/audits/**/generated/",
        "examples/actions/",
        "explicit temp test directory",
    ]
    for root_text in allowed:
        candidate = str(root_text).casefold().rstrip("/")
        if "temp" in candidate:
            continue
        if candidate.endswith("/**/generated"):
            prefix = candidate[: -len("/**/generated")]
            if rel_lower.startswith(prefix + "/") and "/generated/" in rel_lower:
                return resolved
            continue
        if rel_lower == candidate or rel_lower.startswith(candidate + "/"):
            return resolved
    raise ValueError(f"refusing output outside approved action roots: {rel}")


def resolve_path(path: str | Path, root: Path = REPO_ROOT) -> Path:
    candidate = Path(path)
    return (root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()


def is_under_temp(path: Path) -> bool:
    try:
        path.resolve().relative_to(Path(tempfile.gettempdir()).resolve())
        return True
    except ValueError:
        return False


def repo_relative_or_none(path: Path, root: Path) -> str | None:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


def load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON must be an object: {path}")
    return payload


def stable_id(prefix: str, value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}.{digest}.v0"


def iter_key_values(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            yield path, key_text, child
            yield from iter_key_values(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_key_values(child, f"{prefix}[{index}]")
