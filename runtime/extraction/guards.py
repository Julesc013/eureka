"""Safety guards for fixture-only extraction."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_ROOT = REPO_ROOT / "control" / "inventory" / "extraction"

FORBIDDEN_TRUE_KEYS = {
    "accepted_as_truth",
    "accepted_candidate",
    "accepted_candidate_truth",
    "accepted_evidence",
    "accepted_evidence_truth",
    "accepted_public_record",
    "accepted_source_truth",
    "candidate_effect_is_accepted_candidate",
    "candidate_preview_is_accepted_candidate",
    "candidate_store_mutation_allowed",
    "compatibility_verified",
    "downloaded_file",
    "executed_file",
    "evidence_ledger_mutation_allowed",
    "evidence_preview_is_accepted_evidence",
    "explanation_accepts_candidate",
    "explanation_accepts_evidence",
    "explanation_accepts_result_as_truth",
    "explanation_mutates_master_index",
    "explanation_mutates_public_index",
    "explanation_mutates_public_search",
    "explanation_mutates_ranking",
    "global_absence_claimed",
    "known_absence_claims_global_absence",
    "automatic_dedup_allowed",
    "automatic_merge_allowed",
    "delete_allowed_current",
    "dedup_shadow_merges_or_deletes",
    "execution_enabled",
    "extraction_can_mutate_master_index",
    "extraction_can_mutate_public_index",
    "extraction_result_is_public_truth",
    "extraction_result_is_truth",
    "extraction_search_gap_is_public_truth",
    "installer_result",
    "integration_accepts_candidates",
    "integration_accepts_evidence",
    "integration_mutates_master_index",
    "integration_mutates_public_index",
    "integration_mutates_public_search",
    "malware_safety",
    "malware_safety_claimed",
    "manifest_candidate_is_accepted_evidence",
    "master_index_mutated",
    "merge_allowed_current",
    "member_listing_is_accepted_evidence",
    "mutates_master_index",
    "mutates_public_index",
    "network_used",
    "private_file_access_enabled",
    "production_quality_claim",
    "production_quality_claimed",
    "ranking_shadow_accepts_candidate",
    "ranking_shadow_accepts_candidates",
    "ranking_shadow_accepts_evidence",
    "ranking_shadow_accepts_result_as_truth",
    "ranking_shadow_mutates_master_index",
    "ranking_shadow_mutates_public_index",
    "ranking_shadow_mutates_public_ranking",
    "ranking_shadow_mutates_public_search",
    "public_ranking_mutation_allowed",
    "public_search_mutated",
    "public_search_mutation_allowed",
    "public_search_mutation_enabled",
    "public_index_mutated",
    "review_queue_mutation_allowed",
    "review_seed_is_review_decision",
    "rights_clearance",
    "rights_clearance_claimed",
    "source_cache_mutated",
    "verified_installability",
    "verified_installability_claimed",
    "workunit_executed",
    "workunit_seed_executes_work",
}

FORBIDDEN_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON must be an object: {path}")
    return payload


def load_extraction_policy(root: Path = REPO_ROOT) -> dict[str, Any]:
    """Load the committed F-BUNDLE-01 policy bundle."""

    policy_root = root / "control" / "inventory" / "extraction"
    sandbox = load_json(policy_root / "extraction_sandbox_policy.json")
    resource = load_json(policy_root / "extraction_resource_limit_policy.json")
    containers = load_json(policy_root / "extraction_container_type_policy.json")
    paths = load_json(policy_root / "extraction_path_safety_policy.json")
    bombs = load_json(policy_root / "extraction_archive_bomb_policy.json")
    tiers = load_json(policy_root / "extraction_tier_policy.json")
    output = load_json(policy_root / "extraction_output_policy.json")
    truth = load_json(policy_root / "extraction_truth_policy.json")
    review = load_json(policy_root / "extraction_review_policy.json")
    return {
        "schema_version": "extraction_policy_bundle.v0",
        "sandbox": sandbox,
        "resource_limits": resource,
        "container_types": containers,
        "path_safety": paths,
        "archive_bomb": bombs,
        "tiers": tiers,
        "output": output,
        "truth": truth,
        "review": review,
        "allowed_input_roots": sandbox.get("allowed_input_roots", []),
        "allowed_output_roots": sandbox.get("allowed_output_roots", []),
        "forbidden_output_roots": sandbox.get("forbidden_output_roots", []),
        "allowed_container_types": containers.get("allowed_current", []),
        "allowed_tiers": tiers.get("allowed_current_tiers", ["0", "1", "2"]),
        "allowed_manifest_names": resource.get(
            "allowed_manifest_names",
            ["manifest.json", "package.json", "pyproject.toml", "PKG-INFO", "METADATA", "setup.cfg"],
        ),
    }


def resolve_path(path: str | Path, root: Path = REPO_ROOT) -> Path:
    candidate = Path(path)
    return (root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()


def path_under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def is_under_temp(path: Path) -> bool:
    return path_under(path, Path(tempfile.gettempdir()))


def ensure_allowed_input_path(path: str | Path, policy: Mapping[str, Any] | None = None, root: Path = REPO_ROOT) -> Path:
    resolved = resolve_path(path, root)
    if not resolved.exists():
        raise ValueError(f"input path does not exist: {resolved}")
    if is_under_temp(resolved):
        return resolved
    allowed_roots = (policy or {}).get("allowed_input_roots") or [
        "examples/extraction/fixtures",
        "examples/extraction/targets",
    ]
    for root_text in allowed_roots:
        if "temp" in str(root_text).casefold():
            continue
        if path_under(resolved, resolve_path(str(root_text), root)):
            return resolved
    raise ValueError(f"refusing input outside allowed fixture roots: {resolved}")


def ensure_allowed_output_path(path: str | Path, policy: Mapping[str, Any] | None = None, root: Path = REPO_ROOT) -> Path:
    resolved = resolve_path(path, root)
    if is_under_temp(resolved):
        return resolved
    rel = _repo_relative_or_none(resolved, root)
    if rel is None:
        raise ValueError(f"refusing output outside repository approved roots or temp directory: {resolved}")
    rel_lower = rel.casefold().rstrip("/")
    forbidden = (policy or {}).get("forbidden_output_roots") or [
        "site/dist",
        "site/dist/data/public_index",
        "runtime",
        "contracts",
        "control/inventory/publication",
        "control/inventory/sources",
        "data/master_index",
        "master_index",
        ".aide.local",
        ".local/eureka",
        ".cache/eureka",
    ]
    for root_text in forbidden:
        forbidden_lower = str(root_text).casefold().rstrip("/")
        if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
            raise ValueError(f"refusing forbidden output root: {root_text}")
    allowed = (policy or {}).get("allowed_output_roots") or [
        "examples/extraction/results",
        "examples/extraction/candidate_effects",
        "control/audits/**/generated",
    ]
    for root_text in allowed:
        root_lower = str(root_text).casefold().rstrip("/")
        if root_lower.endswith("/**/generated"):
            prefix = root_lower[: -len("/**/generated")]
            if rel_lower.startswith(prefix + "/") and "/generated/" in rel_lower:
                return resolved
            continue
        if "temp" in root_lower:
            continue
        if rel_lower == root_lower or rel_lower.startswith(root_lower + "/"):
            return resolved
    raise ValueError(f"refusing output outside approved extraction roots: {rel}")


def check_path_safety(member_path: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return path-normalization and block status for an archive member name."""

    path_policy = (policy or {}).get("path_safety", policy or {})
    raw = str(member_path)
    reasons: list[str] = []
    if "\x00" in raw and path_policy.get("block_null_bytes", True):
        reasons.append("null_byte")
    normalized_text = raw.replace("\\", "/")
    if normalized_text.startswith("/") and path_policy.get("block_absolute_paths", True):
        reasons.append("absolute_path")
    if re.match(r"^[A-Za-z]:", normalized_text) and path_policy.get("block_drive_prefixes", True):
        reasons.append("drive_prefix")
    parts = [part for part in normalized_text.split("/") if part not in {"", "."}]
    if any(part == ".." for part in parts) and path_policy.get("block_parent_traversal", True):
        reasons.append("parent_traversal")
    normalized_parts: list[str] = []
    for part in parts:
        if part == "..":
            continue
        normalized_parts.append(part)
    normalized = PurePosixPath(*normalized_parts).as_posix() if normalized_parts else ""
    if len(normalized) > int((policy or {}).get("resource_limits", {}).get("max_member_name_length", 160)):
        reasons.append("member_name_too_long")
    return {
        "raw_path": raw,
        "normalized_member_path": normalized,
        "path_safe": not reasons,
        "block_reasons": reasons,
    }


def check_archive_bomb_risk(member_infos: Iterable[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    limits = (policy or {}).get("resource_limits", {})
    bomb = (policy or {}).get("archive_bomb", {})
    max_total = int(bomb.get("max_total_uncompressed_bytes", limits.get("max_total_uncompressed_bytes", 262144)))
    max_members = int(limits.get("max_member_count", 64))
    max_ratio = float(bomb.get("max_compression_ratio", 20.0))
    block_missing = bool(bomb.get("block_if_missing_size_metadata", True))
    total = 0
    reasons: list[str] = []
    count = 0
    for info in member_infos:
        count += 1
        uncomp = info.get("size_uncompressed")
        comp = info.get("size_compressed")
        if uncomp is None or comp is None:
            if block_missing:
                reasons.append("missing_size_metadata")
            continue
        uncomp_int = int(uncomp)
        comp_int = int(comp)
        total += max(uncomp_int, 0)
        if comp_int <= 0 and uncomp_int > 0:
            reasons.append("zero_or_missing_compressed_size")
        elif comp_int > 0 and uncomp_int / comp_int > max_ratio:
            reasons.append("compression_ratio_exceeded")
    if count > max_members:
        reasons.append("member_count_exceeded")
    if total > max_total:
        reasons.append("total_uncompressed_bytes_exceeded")
    return {
        "archive_bomb_risk": bool(reasons),
        "block_reasons": sorted(set(reasons)),
        "member_count": count,
        "total_uncompressed_bytes": total,
        "max_total_uncompressed_bytes": max_total,
        "max_compression_ratio": max_ratio,
    }


def manifest_like(member_path: str, policy: Mapping[str, Any] | None = None) -> bool:
    names = {str(item).casefold() for item in (policy or {}).get("allowed_manifest_names", [])}
    normalized = check_path_safety(member_path, policy)["normalized_member_path"].casefold()
    basename = normalized.rsplit("/", 1)[-1]
    return basename in names or basename.endswith((".manifest", ".spdx.json", ".sbom.json"))


def manifest_kind(member_path: str) -> str:
    basename = member_path.replace("\\", "/").rsplit("/", 1)[-1].casefold()
    if basename == "package.json":
        return "package_json"
    if basename == "pyproject.toml":
        return "pyproject_toml"
    if basename in {"pkg-info", "metadata"}:
        return "python_package_metadata"
    if basename == "manifest.json" or basename.endswith(".manifest"):
        return "generic_manifest"
    if "spdx" in basename or "sbom" in basename:
        return "sbom"
    return "manifest_like"


def truth_boundary() -> dict[str, bool]:
    return {
        "extraction_result_is_public_truth": False,
        "member_listing_is_accepted_evidence": False,
        "manifest_candidate_is_accepted_evidence": False,
        "candidate_effect_is_accepted_candidate": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
    }


def product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_execution": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def detect_truth_or_product_violations(value: Any) -> list[str]:
    violations: list[str] = []
    for path, key, child in iter_key_values(value):
        if key in FORBIDDEN_TRUE_KEYS and child is True:
            violations.append(f"{path}=true is forbidden for extraction artifacts")
    return violations


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


def stable_id(prefix: str, value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))
    digest = __import__("hashlib").sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}.{digest}.v0"


def repo_relative(path: Path, root: Path = REPO_ROOT) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _repo_relative_or_none(path: Path, root: Path) -> str | None:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


def file_sha256(path: Path) -> str:
    digest = __import__("hashlib").sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def looks_like_private_path(path_text: str) -> bool:
    text = str(path_text).casefold().replace("\\", "/")
    if text.startswith(("c:/users/", "/users/", "/home/")):
        return True
    return any(part in text.split("/") for part in {"secrets", ".ssh", ".aide.local", ".cache", ".local"})
