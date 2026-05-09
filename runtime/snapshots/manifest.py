"""Snapshot manifest and record builders.

The snapshot substrate packages explicit fixture/local records into deterministic
offline metadata. It does not fetch sources, host routes, mutate indexes, or
accept truth.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import tempfile
import hashlib
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_ROOT = REPO_ROOT / "control" / "inventory" / "snapshots"
MANIFEST_SCHEMA_VERSION = "snapshot_manifest.v0"
RECORD_SCHEMA_VERSION = "snapshot_record.v0"
RENDER_PROFILES = ("text", "lite_html", "file_tree", "json_manifest")
ALLOWED_RECORD_TYPES = {
    "search_result",
    "object_record",
    "source_record",
    "need_record",
    "candidate_record",
    "evidence_summary",
    "known_absence",
    "action_manifest",
    "acquisition_manifest",
    "citation_bundle",
    "export_manifest",
    "preservation_manifest",
    "blocked_action",
    "policy_blocked_record",
}
FORBIDDEN_TRUE_FIELDS = {
    "snapshot_is_public_truth",
    "snapshot_accepts_evidence",
    "snapshot_accepts_candidate",
    "snapshot_mutates_public_index",
    "snapshot_mutates_master_index",
    "snapshot_enables_live_access",
    "snapshot_downloads_files",
    "snapshot_mirrors_files",
    "snapshot_executes_actions",
    "fixity_implies_authenticity",
    "signature_placeholder_implies_trust",
    "public_index_mutated",
    "master_index_mutated",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "verified_installability_claimed",
    "compatibility_certification_claimed",
    "hosting_enabled",
    "relay_enabled",
    "site_dist_mutated",
    "download_enabled",
    "execution_enabled",
    "live_access_enabled",
}


def load_snapshot_policy(root: Path = REPO_ROOT) -> dict[str, Any]:
    names = [
        "snapshot_envelope_policy",
        "snapshot_manifest_policy",
        "snapshot_record_policy",
        "snapshot_fixity_policy",
        "snapshot_signature_policy",
        "snapshot_consumer_policy",
        "snapshot_render_policy",
        "snapshot_path_policy",
        "snapshot_truth_policy",
        "snapshot_no_live_access_policy",
        "snapshot_semantic_parity_policy",
    ]
    policy_root = root / "control" / "inventory" / "snapshots"
    bundle = {name: load_json(policy_root / f"{name}.json") for name in names}
    paths = bundle["snapshot_path_policy"]
    render = bundle["snapshot_render_policy"]
    return {
        "schema_version": "snapshot_policy_bundle.v0",
        **bundle,
        "allowed_output_roots": paths.get("allowed_output_roots", []),
        "forbidden_output_roots": paths.get("forbidden_output_roots", []),
        "allowed_render_profiles": render.get("allowed_profiles", list(RENDER_PROFILES)),
        "required_semantic_fields": render.get(
            "required_semantic_fields",
            [
                "identity",
                "source posture",
                "evidence posture",
                "rights posture",
                "risk posture",
                "action posture",
                "limitations/no-claims",
            ],
        ),
    }


def build_snapshot_manifest(records: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    snapshot_records = [build_snapshot_record(record, policy) for record in records]
    type_counts = Counter(record["record_type"] for record in snapshot_records)
    source_refs = sorted({record.get("source_ref", "") for record in snapshot_records if record.get("source_ref")})
    evidence_refs = sorted(
        {
            ref
            for record in snapshot_records
            for ref in _string_list(record.get("render_fields", {}).get("evidence_refs", []))
        }
    )
    action_refs = sorted(
        {
            record["canonical_ref"]
            for record in snapshot_records
            if record["record_type"] in {"action_manifest", "acquisition_manifest", "citation_bundle", "export_manifest", "preservation_manifest", "blocked_action"}
        }
    )
    manifest_id = stable_id("snapshot_manifest", [record["snapshot_record_id"] for record in snapshot_records])
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "snapshot_manifest_id": manifest_id,
        "manifest_status": "fixture_only",
        "generated_from": {
            "input_kind": "explicit_fixture_records",
            "generator": "runtime.snapshots.manifest.build_snapshot_manifest",
            "network_used": False,
            "site_dist_used": False,
        },
        "records": snapshot_records,
        "record_count": len(snapshot_records),
        "record_type_counts": dict(sorted(type_counts.items())),
        "source_summary": {
            "source_refs": source_refs,
            "source_count": len(source_refs),
            "source_posture": "fixture_or_local_ref_only",
        },
        "evidence_summary": {
            "evidence_refs": evidence_refs,
            "evidence_count": len(evidence_refs),
            "evidence_posture": "preview_or_reviewed_ref_only",
            "accepted_evidence": False,
        },
        "action_summary": {
            "action_refs": action_refs,
            "safe_action_manifest_only": True,
            "blocked_actions_preserved": True,
            "download_enabled": False,
            "execution_enabled": False,
        },
        "render_targets": list((policy or {}).get("allowed_render_profiles", RENDER_PROFILES)),
        "fixity_entries": [],
        "signature_summary": {
            "signature_status": "unsigned",
            "signature_placeholder_implies_trust": False,
        },
        "limitations": [
            "Fixture-only snapshot manifest.",
            "Records remain previews or examples unless separately reviewed.",
            "No live source access, hosting, downloads, mirroring, execution, or index mutation is enabled.",
        ],
        "no_claims": no_claims(),
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
    }
    manifest["fixity_entries"] = [
        {
            "record_ref": record["snapshot_record_id"],
            "hash_algorithm": "sha256",
            "hash_value": stable_hash(record),
        }
        for record in snapshot_records
    ]
    return manifest


def build_snapshot_record(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if record.get("schema_version") == RECORD_SCHEMA_VERSION:
        return dict(record)
    record_type = _record_type(record)
    canonical_ref = _canonical_ref(record)
    title = _title(record, record_type)
    limitations = _limitations(record)
    render_fields = {
        "identity": canonical_ref,
        "title": title,
        "summary": _summary(record, record_type),
        "source_posture": _posture(record, "source", "fixture_or_local_ref_only"),
        "evidence_posture": _posture(record, "evidence", "preview_or_reviewed_ref_only"),
        "compatibility_posture": _posture(record, "compatibility", "unknown_or_fixture_only"),
        "rights_posture": _posture(record, "rights", "unknown_not_cleared"),
        "risk_posture": _posture(record, "risk", "unknown_not_scanned"),
        "action_posture": _action_posture(record, record_type),
        "limitations": limitations,
        "no_claims": no_claims(),
        "evidence_refs": _extract_refs(record, "evidence"),
        "source_refs": _extract_refs(record, "source"),
        "blocked_actions": _extract_blocked_actions(record, record_type),
        "allowed_actions": _extract_allowed_actions(record),
    }
    return {
        "schema_version": RECORD_SCHEMA_VERSION,
        "snapshot_record_id": stable_id("snapshot_record", {"type": record_type, "ref": canonical_ref}),
        "record_type": record_type,
        "record_status": "fixture_only" if record_type != "policy_blocked_record" else "policy_blocked",
        "canonical_ref": canonical_ref,
        "source_ref": _first(render_fields["source_refs"], str(record.get("source_ref", ""))),
        "title": title,
        "summary": render_fields["summary"],
        "source_posture": render_fields["source_posture"],
        "evidence_posture": render_fields["evidence_posture"],
        "compatibility_posture": render_fields["compatibility_posture"],
        "rights_posture": render_fields["rights_posture"],
        "risk_posture": render_fields["risk_posture"],
        "action_posture": render_fields["action_posture"],
        "limitations": limitations,
        "render_fields": render_fields,
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
    }


def validate_snapshot_manifest(manifest: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "snapshot_manifest_id",
        "manifest_status",
        "generated_from",
        "records",
        "record_count",
        "record_type_counts",
        "source_summary",
        "evidence_summary",
        "action_summary",
        "render_targets",
        "fixity_entries",
        "signature_summary",
        "limitations",
        "no_claims",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required):
        if field not in manifest:
            errors.append(f"missing snapshot manifest field: {field}")
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        errors.append(f"schema_version must be {MANIFEST_SCHEMA_VERSION}")
    records = manifest.get("records", [])
    if not isinstance(records, list):
        errors.append("records must be a list")
    else:
        if manifest.get("record_count") != len(records):
            errors.append("record_count must equal records length")
        for index, record in enumerate(records):
            if isinstance(record, Mapping):
                errors.extend(f"records[{index}]: {error}" for error in validate_snapshot_record(record, policy))
            else:
                errors.append(f"records[{index}] must be an object")
    errors.extend(detect_snapshot_boundary_violations(manifest))
    return sorted(dict.fromkeys(errors))


def validate_snapshot_record(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "snapshot_record_id",
        "record_type",
        "record_status",
        "canonical_ref",
        "source_ref",
        "title",
        "summary",
        "source_posture",
        "evidence_posture",
        "compatibility_posture",
        "rights_posture",
        "risk_posture",
        "action_posture",
        "limitations",
        "render_fields",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required):
        if field not in record:
            errors.append(f"missing snapshot record field: {field}")
    if record.get("schema_version") != RECORD_SCHEMA_VERSION:
        errors.append(f"schema_version must be {RECORD_SCHEMA_VERSION}")
    if record.get("record_type") not in ALLOWED_RECORD_TYPES:
        errors.append(f"record_type is not allowed: {record.get('record_type')}")
    render_fields = record.get("render_fields", {})
    for field in ("identity", "title", "summary", "source_posture", "evidence_posture", "rights_posture", "risk_posture", "action_posture", "limitations", "no_claims"):
        if not isinstance(render_fields, Mapping) or field not in render_fields:
            errors.append(f"render_fields.{field} is required")
    errors.extend(detect_snapshot_boundary_violations(record))
    return sorted(dict.fromkeys(errors))


def canonicalize_snapshot_manifest(manifest: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    return json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def truth_boundary() -> dict[str, bool]:
    return {
        "snapshot_is_public_truth": False,
        "snapshot_accepts_evidence": False,
        "snapshot_accepts_candidate": False,
        "snapshot_mutates_public_index": False,
        "snapshot_mutates_master_index": False,
        "snapshot_enables_live_access": False,
        "snapshot_downloads_files": False,
        "snapshot_mirrors_files": False,
        "snapshot_executes_actions": False,
        "fixity_implies_authenticity": False,
        "signature_placeholder_implies_trust": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "compatibility_certification_claimed": False,
    }


def product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_relay": False,
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


def no_claims() -> list[str]:
    return [
        "no accepted public truth",
        "no rights clearance",
        "no malware safety",
        "no verified installability",
        "no compatibility certification",
        "no exhaustive source coverage",
        "no downloads or mirrors",
        "no execution or installation",
        "no hosting or relay activation",
    ]


def detect_snapshot_boundary_violations(value: Any) -> list[str]:
    violations: list[str] = []
    for path, key, child in iter_key_values(value):
        if key in FORBIDDEN_TRUE_FIELDS and child is True:
            violations.append(f"{path} must be false for D snapshot artifacts")
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
        "data/public_index/",
        "runtime/",
        "contracts/",
        "control/inventory/publication/",
        "master_index/",
        "data/master_index/",
        "relay/",
        "hosted/",
        ".aide.local/",
        ".local/eureka/",
        ".cache/eureka/",
    ]
    for root_text in forbidden:
        candidate = str(root_text).casefold().rstrip("/")
        if rel_lower == candidate or rel_lower.startswith(candidate + "/"):
            raise ValueError(f"refusing forbidden output root: {root_text}")
    allowed = (policy or {}).get("allowed_output_roots") or [
        "control/audits/**/generated/",
        "examples/snapshots/",
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
    raise ValueError(f"refusing output outside approved snapshot roots: {rel}")


def ensure_allowed_input_path(path: str | Path, root: Path = REPO_ROOT) -> Path:
    resolved = resolve_path(path, root)
    if not resolved.exists():
        raise ValueError(f"input path does not exist: {resolved}")
    if is_under_temp(resolved):
        return resolved
    rel = repo_relative_or_none(resolved, root)
    if rel and (
        rel == "examples/snapshots"
        or rel.startswith("examples/snapshots/")
        or rel == "examples/actions"
        or rel.startswith("examples/actions/")
        or rel == "examples/search_quality"
        or rel.startswith("examples/search_quality/")
        or rel == "control/audits"
        or rel.startswith("control/audits/")
    ):
        return resolved
    raise ValueError(f"refusing input outside approved snapshot/example roots: {rel or resolved}")


def load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON must be an object: {path}")
    return payload


def stable_id(prefix: str, value: Any) -> str:
    return f"{prefix}.{stable_hash(value)[:12]}.v0"


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, default=str, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def resolve_path(path: str | Path, root: Path = REPO_ROOT) -> Path:
    candidate = Path(path)
    return (root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()


def is_under_temp(path: Path) -> bool:
    try:
        path.resolve().relative_to(Path(tempfile.gettempdir()).resolve())
        return True
    except ValueError:
        return False


def repo_relative_or_none(path: Path, root: Path = REPO_ROOT) -> str | None:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


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


def _record_type(record: Mapping[str, Any]) -> str:
    explicit = str(record.get("record_type") or "").strip()
    if explicit in ALLOWED_RECORD_TYPES:
        return explicit
    schema = str(record.get("schema_version", ""))
    if schema == "action_manifest.v0":
        return "action_manifest"
    if schema == "acquisition_manifest.v0":
        return "acquisition_manifest"
    if schema == "citation_bundle.v0":
        return "citation_bundle"
    if schema == "export_manifest.v0":
        return "export_manifest"
    if schema == "preservation_manifest.v0":
        return "preservation_manifest"
    if schema == "blocked_action_report.v0":
        return "blocked_action"
    if schema == "known_absence_record.v0":
        return "known_absence"
    if "search" in str(record.get("view_family", "")).casefold() or "query" in record:
        return "search_result"
    if "source" in schema or record.get("source_id") or record.get("source_refs"):
        return "source_record"
    if "need" in schema or record.get("search_need_refs") or record.get("need_refs"):
        return "need_record"
    if record.get("policy_blocked") is True or record.get("status") == "policy_blocked":
        return "policy_blocked_record"
    return "object_record"


def _canonical_ref(record: Mapping[str, Any]) -> str:
    for key in (
        "canonical_ref",
        "snapshot_record_id",
        "action_manifest_id",
        "acquisition_manifest_id",
        "citation_bundle_id",
        "export_manifest_id",
        "preservation_manifest_id",
        "blocked_action_report_id",
        "known_absence_id",
        "view_model_id",
        "candidate_id",
        "source_record_id",
        "source_id",
        "id",
    ):
        if record.get(key):
            return str(record[key])
    return stable_id("record", record)


def _title(record: Mapping[str, Any], record_type: str) -> str:
    for key in ("title", "page_title", "action_label", "label", "name", "snapshot_label"):
        if record.get(key):
            return str(record[key])
    return record_type.replace("_", " ").title()


def _summary(record: Mapping[str, Any], record_type: str) -> str:
    for key in ("summary", "action_summary", "absence_summary", "claim_summary"):
        if record.get(key):
            return str(record[key])
    if isinstance(record.get("result_summary"), Mapping):
        return str(record["result_summary"].get("summary", "Snapshot record."))
    return f"Snapshot record for {record_type}."


def _limitations(record: Mapping[str, Any]) -> list[str]:
    value = record.get("limitations")
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            if isinstance(item, Mapping):
                result.append(str(item.get("description") or item.get("label") or item))
            else:
                result.append(str(item))
        return result or ["Fixture/local snapshot record only."]
    return ["Fixture/local snapshot record only.", "No public truth is accepted."]


def _posture(record: Mapping[str, Any], posture_name: str, default: str) -> str:
    key = f"{posture_name}_posture"
    if isinstance(record.get(key), str):
        return str(record[key])
    summary_key = f"{posture_name}_summary"
    summary = record.get(summary_key)
    if isinstance(summary, Mapping):
        return str(summary.get("posture") or summary.get("summary") or default)
    if isinstance(summary, str):
        return summary
    return default


def _action_posture(record: Mapping[str, Any], record_type: str) -> str:
    if record_type == "blocked_action":
        return "blocked_action_preserved"
    if record_type.endswith("manifest"):
        return "descriptive_action_manifest_only"
    if record.get("action_status") == "blocked_by_policy":
        return "blocked_action_preserved"
    return "safe_descriptive_actions_only"


def _extract_refs(record: Mapping[str, Any], family: str) -> list[str]:
    keys = [f"{family}_refs", f"{family}_ref"]
    if family == "evidence":
        keys.extend(["evidence_refs", "evidence_links"])
    if family == "source":
        keys.extend(["source_refs", "source_id", "source_ref"])
    refs: list[str] = []
    for key in keys:
        value = record.get(key)
        if isinstance(value, list):
            refs.extend(str(item) for item in value)
        elif value:
            refs.append(str(value))
    return sorted(dict.fromkeys(refs))


def _extract_blocked_actions(record: Mapping[str, Any], record_type: str) -> list[str]:
    actions = _string_list(record.get("blocked_actions"))
    if record_type == "blocked_action":
        actions.append(str(record.get("blocked_action_family", "unknown")))
    if record.get("action_status") == "blocked_by_policy":
        actions.append(str(record.get("action_family", "unknown")))
    return sorted(dict.fromkeys(action for action in actions if action))


def _extract_allowed_actions(record: Mapping[str, Any]) -> list[str]:
    actions = _string_list(record.get("allowed_current_actions")) + _string_list(record.get("allowed_effects"))
    if not actions:
        actions = ["view", "inspect", "cite", "export_manifest"]
    return sorted(dict.fromkeys(actions))


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value:
        return [str(value)]
    return []


def _first(values: list[str], fallback: str) -> str:
    return values[0] if values else fallback
