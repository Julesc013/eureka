from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

try:
    import validate_local_staging_manifest
except ImportError:  # pragma: no cover - exercised through validator unavailability posture.
    validate_local_staging_manifest = None  # type: ignore[assignment]


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples" / "local_staging_manifests"
MANIFEST_NAME = "LOCAL_STAGING_MANIFEST.json"
INSPECTOR_ID = "staged_pack_inspector_v0"
SCHEMA_VERSION = "staged_pack_inspection.v0"

HARD_FALSE_FIELDS = (
    "model_calls_performed",
    "mutation_performed",
    "staging_performed",
    "import_performed",
    "indexing_performed",
    "upload_performed",
    "master_index_mutation_performed",
    "runtime_mutation_performed",
    "network_performed",
    "public_search_mutated",
    "local_index_mutated",
)
NO_MUTATION_MANIFEST_FIELDS = (
    "public_search_mutated",
    "local_index_mutated",
    "canonical_source_registry_mutated",
    "runtime_state_mutated",
    "master_index_mutated",
    "upload_performed",
    "live_network_performed",
)
SECRET_KEY_RE = re.compile(r"(api[_-]?key|auth[_-]?token|password|private[_-]?key|secret)", re.IGNORECASE)
SECRET_VALUE_RE = re.compile(r"(sk-[A-Za-z0-9_-]{8,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)", re.IGNORECASE)
PRIVATE_PATH_RE = re.compile(
    r"([A-Za-z]:[\\/](Users|Documents and Settings|Projects|Temp|tmp)[\\/][^\s\"']*|"
    r"\\\\[^\\/\s]+[\\/][^\\/\s]+(?:[\\/][^\s\"']*)?|"
    r"/(Users|home)/[^\s\"']+|"
    r"/(private/tmp|tmp|var/folders)/[^\s\"']*)",
    re.IGNORECASE,
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect Local Staging Manifest v0 files without staging or import.")
    parser.add_argument("--manifest", help="Inspect one LOCAL_STAGING_MANIFEST.json file.")
    parser.add_argument("--manifest-root", help="Inspect one manifest root containing LOCAL_STAGING_MANIFEST.json.")
    parser.add_argument("--all-examples", action="store_true", help="Inspect all committed synthetic manifest examples.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--strict", action="store_true", help="Pass strict mode to manifest validation.")
    parser.add_argument("--no-validate", action="store_true", help="Skip validation before inspection.")
    parser.add_argument("--list-examples", action="store_true", help="List committed manifest examples and exit.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    output = stdout or sys.stdout
    examples = discover_example_manifest_roots()

    if args.list_examples:
        report = _list_examples_report(examples)
        _emit(report, json_output=args.json, output=output)
        return 0 if report["ok"] else 1

    report = inspect_staged_manifests(
        manifest_path=Path(args.manifest) if args.manifest else None,
        manifest_root=Path(args.manifest_root) if args.manifest_root else None,
        all_examples=args.all_examples or (not args.manifest and not args.manifest_root),
        validate_first=not args.no_validate,
        strict=args.strict,
    )
    _emit(report, json_output=args.json, output=output)
    return 0 if report["ok"] else 1


def discover_example_manifest_roots() -> list[Path]:
    if not EXAMPLES_ROOT.exists():
        return []
    return sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir() and (path / MANIFEST_NAME).is_file())


def inspect_staged_manifests(
    *,
    manifest_path: Path | None = None,
    manifest_root: Path | None = None,
    all_examples: bool = True,
    validate_first: bool = True,
    strict: bool = False,
) -> dict[str, Any]:
    targets: list[tuple[Path, Path | None]]
    mode = "all_examples"
    errors: list[str] = []

    if all_examples:
        roots = discover_example_manifest_roots()
        targets = [(root / MANIFEST_NAME, root) for root in roots]
        if not targets:
            errors.append("No committed local staging manifest examples were found.")
    elif manifest_root is not None:
        root = _resolve(manifest_root)
        targets = [(root / MANIFEST_NAME, root)]
        mode = "single_manifest_root"
    elif manifest_path is not None:
        targets = [(_resolve(manifest_path), None)]
        mode = "single_manifest"
    else:
        targets = []
        errors.append("No manifest target supplied.")

    inspected = [
        inspect_staged_manifest_file(path, manifest_root=root, validate_first=validate_first, strict=strict)
        for path, root in targets
    ]
    errors.extend(f"{item['manifest_path']}: {error}" for item in inspected for error in item.get("errors", []))

    ok = not errors and all(item.get("ok") for item in inspected)
    report: dict[str, Any] = {
        "ok": ok,
        "schema_version": SCHEMA_VERSION,
        "inspector_id": INSPECTOR_ID,
        "mode": mode,
        "strict": strict,
        "validation_enabled": validate_first,
        "inspected_manifests": inspected,
        "summary": _summary(inspected),
        "errors": errors,
        "notes": [
            "Inspection only; no staging, import, indexing, upload, runtime mutation, public-search mutation, or master-index mutation performed.",
            "Staged entities are candidates and not canonical records, rights clearance, malware safety, source-trust decisions, or master-index acceptance.",
        ],
        **_hard_false_flags(),
    }
    return report


def inspect_staged_manifest_file(
    manifest_path: Path,
    *,
    manifest_root: Path | None = None,
    validate_first: bool = True,
    strict: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    resolved = _resolve(manifest_path)
    validation_status = "skipped" if not validate_first else "unavailable"

    if validate_first:
        if validate_local_staging_manifest is None:
            errors.append("validate_local_staging_manifest.py is unavailable.")
            validation_status = "unavailable"
        else:
            validation = validate_local_staging_manifest.validate_local_staging_manifest_file(
                resolved,
                manifest_root=manifest_root,
                strict=strict,
            )
            validation_status = "passed" if validation.get("ok") else "failed"
            for error in validation.get("errors", []):
                errors.append(redact_sensitive(str(error)))

    payload = _load_json(resolved, errors)
    if not isinstance(payload, Mapping):
        return _empty_result(resolved, validation_status, errors, warnings)

    sanitized_payload = redact_sensitive(payload)
    assert isinstance(sanitized_payload, Mapping)

    counts = _mapping(sanitized_payload.get("counts"))
    privacy_summary = _mapping(sanitized_payload.get("privacy_rights_risk_summary"))
    no_mutation = _no_mutation_guarantees(sanitized_payload)
    reset_policy = _mapping(sanitized_payload.get("reset_delete_export_policy"))
    source_report_ref = _mapping(sanitized_payload.get("source_validate_report_ref"))
    staged_pack_refs = _pack_ref_summaries(sanitized_payload.get("staged_pack_refs"))
    staged_entity_summary = _staged_entity_summary(sanitized_payload.get("staged_entities"))

    if any(no_mutation.get(field) is not False for field in NO_MUTATION_MANIFEST_FIELDS):
        errors.append("No-mutation guarantee fields must all be false.")
    if staged_entity_summary["canonical_record_claims"]:
        errors.append("Staged entities must not claim canonical records or acceptance.")

    result = {
        "ok": not errors,
        "manifest_path": _display_path(resolved),
        "manifest_id": sanitized_payload.get("manifest_id"),
        "status": sanitized_payload.get("status"),
        "validation_status": validation_status,
        "staging_mode": sanitized_payload.get("staging_mode"),
        "source_validate_report_ref": {
            "report_id": source_report_ref.get("report_id"),
            "report_status": source_report_ref.get("report_status"),
            "report_created_by_tool": source_report_ref.get("report_created_by_tool"),
            "report_path_policy": source_report_ref.get("report_path_policy"),
        },
        "staged_pack_refs": staged_pack_refs,
        "staged_pack_count": counts.get("staged_pack_count", len(staged_pack_refs)),
        "staged_entity_count": counts.get("staged_entity_count", staged_entity_summary["total"]),
        "counts": counts,
        "staged_entity_summary": staged_entity_summary,
        "privacy_rights_risk_summary": privacy_summary,
        "no_mutation_guarantees": no_mutation,
        "reset_delete_export_policy": reset_policy,
        "limitations": _string_list(sanitized_payload.get("limitations")),
        "warnings": warnings,
        "errors": errors,
        "next_safe_action": _next_safe_action(validation_status, errors),
    }
    return result


def redact_sensitive(value: Any) -> Any:
    if isinstance(value, Mapping):
        redacted: dict[str, Any] = {}
        for key, child in value.items():
            key_text = str(key)
            if SECRET_KEY_RE.search(key_text):
                redacted[key_text] = False if child is False else "<redacted-secret-field>"
            else:
                redacted[key_text] = redact_sensitive(child)
        return redacted
    if isinstance(value, list):
        return [redact_sensitive(child) for child in value]
    if isinstance(value, str):
        return _redact_text(value)
    return value


def _redact_text(value: str) -> str:
    text = SECRET_VALUE_RE.sub("<redacted-secret>", value)
    return PRIVATE_PATH_RE.sub("<redacted-local-path>", text)


def _pack_ref_summaries(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    summaries: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            continue
        summaries.append(
            {
                "staged_pack_ref": item.get("staged_pack_ref"),
                "pack_id": item.get("pack_id"),
                "pack_version": item.get("pack_version"),
                "pack_type": item.get("pack_type"),
                "validation_status": item.get("validation_status"),
                "privacy_classification": item.get("privacy_classification"),
                "rights_classification": item.get("rights_classification"),
                "risk_classification": item.get("risk_classification"),
                "pack_root_policy": item.get("pack_root_policy"),
            }
        )
    return summaries


def _staged_entity_summary(value: Any) -> dict[str, Any]:
    entities = value if isinstance(value, list) else []
    by_type: dict[str, int] = {}
    by_review_status: dict[str, int] = {}
    private_count = 0
    public_safe_count = 0
    issue_count = 0
    canonical_claims: list[str] = []
    examples: list[dict[str, Any]] = []
    for item in entities:
        if not isinstance(item, Mapping):
            continue
        entity_type = str(item.get("entity_type", "unknown"))
        review_status = str(item.get("review_status", "unknown"))
        by_type[entity_type] = by_type.get(entity_type, 0) + 1
        by_review_status[review_status] = by_review_status.get(review_status, 0) + 1
        if item.get("privacy_classification") in {"local_private", "restricted"}:
            private_count += 1
        if item.get("public_safe") is True:
            public_safe_count += 1
        if entity_type == "staged_issue":
            issue_count += 1
        text = " ".join(str(item.get(field, "")) for field in ["review_status", "summary"]).lower()
        if "accepted_public" in text or "canonical record" in text or "master index accepted" in text:
            canonical_claims.append(str(item.get("staged_entity_id", "unknown")))
        if len(examples) < 5:
            examples.append(
                {
                    "staged_entity_id": item.get("staged_entity_id"),
                    "entity_type": entity_type,
                    "review_status": review_status,
                    "public_safe": item.get("public_safe"),
                    "privacy_classification": item.get("privacy_classification"),
                    "rights_classification": item.get("rights_classification"),
                    "risk_classification": item.get("risk_classification"),
                    "summary": item.get("summary"),
                    "candidate_not_canonical": True,
                }
            )
    return {
        "total": len([item for item in entities if isinstance(item, Mapping)]),
        "by_type": by_type,
        "by_review_status": by_review_status,
        "issue_count": issue_count,
        "private_record_count": private_count,
        "public_safe_record_count": public_safe_count,
        "canonical_record_claims": canonical_claims,
        "examples": examples,
        "candidate_semantics": "staged entities are candidates only and not canonical records",
    }


def _no_mutation_guarantees(payload: Mapping[str, Any]) -> dict[str, Any]:
    nested = _mapping(payload.get("no_mutation_guarantees"))
    result: dict[str, Any] = {}
    for field in NO_MUTATION_MANIFEST_FIELDS:
        result[field] = payload.get(field) if field in payload else nested.get(field)
    return result


def _summary(results: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "total": len(results),
        "passed": sum(1 for result in results if result.get("ok")),
        "failed": sum(1 for result in results if not result.get("ok")),
        "unavailable": sum(1 for result in results if result.get("validation_status") == "unavailable"),
    }


def _next_safe_action(validation_status: str, errors: Sequence[str]) -> str:
    if errors:
        return "fix_manifest_and_reinspect"
    if validation_status == "skipped":
        return "validate_manifest_before_future_action"
    return "review_candidates_read_only"


def _empty_result(path: Path, validation_status: str, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "ok": False,
        "manifest_path": _display_path(path),
        "manifest_id": None,
        "status": None,
        "validation_status": validation_status,
        "staging_mode": None,
        "staged_pack_count": 0,
        "staged_entity_count": 0,
        "counts": {},
        "privacy_rights_risk_summary": {},
        "no_mutation_guarantees": {},
        "reset_delete_export_policy": {},
        "limitations": [],
        "warnings": warnings,
        "errors": errors,
        "next_safe_action": "fix_manifest_and_reinspect",
    }


def _list_examples_report(examples: Sequence[Path]) -> dict[str, Any]:
    return {
        "ok": bool(examples),
        "schema_version": SCHEMA_VERSION,
        "inspector_id": INSPECTOR_ID,
        "mode": "list_examples",
        "examples": [{"manifest_root": _display_path(root), "manifest": _display_path(root / MANIFEST_NAME)} for root in examples],
        "summary": {"total": len(examples), "passed": len(examples), "failed": 0, "unavailable": 0},
        "notes": ["Lists committed synthetic examples only; no recursive arbitrary directory scan is performed."],
        **_hard_false_flags(),
    }


def _emit(payload: Mapping[str, Any], *, json_output: bool, output: TextIO) -> None:
    if json_output:
        output.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(payload))


def _format_plain(payload: Mapping[str, Any]) -> str:
    if payload.get("mode") == "list_examples":
        lines = [
            "Staged Pack Inspector examples",
            f"status: {'available' if payload.get('ok') else 'unavailable'}",
            f"total: {payload.get('summary', {}).get('total', 0)}",
        ]
        for example in payload.get("examples", []):
            lines.append(f"- {example['manifest_root']} -> {example['manifest']}")
        lines.extend(_plain_side_effect_lines(payload))
        return "\n".join(lines) + "\n"

    lines = [
        "Staged Pack Inspection",
        f"status: {'valid' if payload.get('ok') else 'invalid'}",
        f"mode: {payload.get('mode')}",
        f"validation_enabled: {payload.get('validation_enabled')}",
        "inspection only; no staging/import/index/search/master-index mutation performed",
    ]
    summary = payload.get("summary", {})
    lines.append(
        "summary: "
        f"total={summary.get('total', 0)} "
        f"passed={summary.get('passed', 0)} "
        f"failed={summary.get('failed', 0)} "
        f"unavailable={summary.get('unavailable', 0)}"
    )
    for item in payload.get("inspected_manifests", []):
        lines.extend(_format_manifest_plain(item))
    lines.extend(_plain_side_effect_lines(payload))
    if payload.get("errors"):
        lines.append("Errors")
        lines.extend(f"- {error}" for error in payload["errors"])
    return "\n".join(lines) + "\n"


def _format_manifest_plain(item: Mapping[str, Any]) -> list[str]:
    report_ref = _mapping(item.get("source_validate_report_ref"))
    counts = _mapping(item.get("counts"))
    privacy = _mapping(item.get("privacy_rights_risk_summary"))
    no_mutation = _mapping(item.get("no_mutation_guarantees"))
    reset_policy = _mapping(item.get("reset_delete_export_policy"))
    entity_summary = _mapping(item.get("staged_entity_summary"))
    lines = [
        "",
        f"Manifest: {item.get('manifest_id')} ({item.get('manifest_path')})",
        f"  status: {item.get('status')}",
        f"  validation_status: {item.get('validation_status')}",
        f"  staging_mode: {item.get('staging_mode')}",
        f"  validate_report: {report_ref.get('report_id')} ({report_ref.get('report_status')})",
        f"  staged_packs: {item.get('staged_pack_count')}",
        f"  staged_entities: {item.get('staged_entity_count')}",
        f"  entity_types: {_compact_map(entity_summary.get('by_type'))}",
        f"  review_statuses: {_compact_map(entity_summary.get('by_review_status'))}",
        f"  privacy: {privacy.get('privacy_classification')} default={privacy.get('default_visibility')}",
        f"  rights: {privacy.get('rights_classification')}",
        f"  risk: {privacy.get('risk_classification')}",
        "  no_mutation: "
        f"public_search={no_mutation.get('public_search_mutated')} "
        f"local_index={no_mutation.get('local_index_mutated')} "
        f"runtime={no_mutation.get('runtime_state_mutated')} "
        f"master_index={no_mutation.get('master_index_mutated')}",
        "  reset/delete/export future: "
        f"delete={reset_policy.get('delete_staged_pack_supported_future')} "
        f"clear_all={reset_policy.get('clear_all_staged_state_supported_future')} "
        f"export_manifest={reset_policy.get('export_manifest_supported_future')} "
        f"export_private_default={reset_policy.get('export_private_data_default')}",
        f"  candidate_semantics: {entity_summary.get('candidate_semantics')}",
        f"  next_safe_action: {item.get('next_safe_action')}",
    ]
    for pack_ref in item.get("staged_pack_refs", []):
        lines.append(
            "  pack_ref: "
            f"{pack_ref.get('pack_type')} {pack_ref.get('pack_id')} "
            f"validation={pack_ref.get('validation_status')} "
            f"privacy={pack_ref.get('privacy_classification')} "
            f"rights={pack_ref.get('rights_classification')} "
            f"risk={pack_ref.get('risk_classification')}"
        )
    if counts:
        lines.append(f"  counts: {_compact_map(counts)}")
    if item.get("limitations"):
        lines.append("  limitations:")
        lines.extend(f"    - {limitation}" for limitation in item["limitations"])
    return lines


def _plain_side_effect_lines(payload: Mapping[str, Any]) -> list[str]:
    return [f"{field}: {payload.get(field)}" for field in HARD_FALSE_FIELDS]


def _compact_map(value: Any) -> str:
    if not isinstance(value, Mapping) or not value:
        return "{}"
    return ", ".join(f"{key}={value[key]}" for key in sorted(value))


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.exists():
        errors.append(f"{_display_path(path)}: file is missing.")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_display_path(path)}: invalid JSON: {exc}.")
        return None


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _hard_false_flags() -> dict[str, bool]:
    return {field: False for field in HARD_FALSE_FIELDS}


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return "<explicit-local-path>"


if __name__ == "__main__":
    raise SystemExit(main())
