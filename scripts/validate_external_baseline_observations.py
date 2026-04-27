from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_BASELINE_ROOT = REPO_ROOT / "evals" / "search_usefulness" / "external_baselines"
DEFAULT_OBSERVATIONS_DIR = EXTERNAL_BASELINE_ROOT / "observations"
QUERY_PACK_PATH = REPO_ROOT / "evals" / "search_usefulness" / "queries" / "search_usefulness_v0.json"

VALID_STATUSES = {
    "observed",
    "pending_manual_observation",
    "not_applicable",
    "blocked",
    "stale",
}
PENDING_STATUS = "pending_manual_observation"
FORBIDDEN_COLLECTION_METHODS = {
    "scraped",
    "scraping",
    "automated",
    "automated_query",
    "api",
    "crawler",
    "crawled",
}
SCORE_FIELDS = {
    "object_type_fit",
    "smallest_actionable_unit",
    "evidence_quality",
    "compatibility_clarity",
    "actionability",
    "absence_explanation",
    "duplicate_handling",
    "user_cost_reduction",
    "overall",
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate manual external baseline observation records. This script "
            "does not query Google, Internet Archive, or any external system."
        )
    )
    parser.add_argument(
        "--observations-dir",
        default=str(DEFAULT_OBSERVATIONS_DIR),
        help="Directory of committed or temporary observation JSON files.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_external_baseline_observations(
        observations_dir=Path(args.observations_dir)
    )
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain_report(report))
    return 0 if report["status"] == "valid" else 1


def validate_external_baseline_observations(
    *,
    observations_dir: Path = DEFAULT_OBSERVATIONS_DIR,
) -> dict[str, Any]:
    errors: list[str] = []
    systems_payload = _load_json(EXTERNAL_BASELINE_ROOT / "systems.json", errors)
    schema_payload = _load_json(EXTERNAL_BASELINE_ROOT / "observation.schema.json", errors)
    template_payload = _load_json(EXTERNAL_BASELINE_ROOT / "observation_template.json", errors)
    query_pack = _load_json(QUERY_PACK_PATH, errors)

    system_ids = _validate_systems(systems_payload, errors)
    query_ids = _query_ids(query_pack, errors)
    _validate_schema(schema_payload, errors)
    _validate_template(template_payload, errors)

    observation_files = sorted(path for path in observations_dir.glob("*.json") if path.is_file())
    status_counts_by_system: dict[str, Counter[str]] = defaultdict(Counter)
    observed_query_ids_by_system: dict[str, set[str]] = defaultdict(set)
    pending_slot_counts_by_system: Counter[str] = Counter()
    manifest_count = 0
    record_count = 0

    for path in observation_files:
        payload = _load_json(path, errors)
        if not isinstance(payload, Mapping):
            errors.append(f"{_rel(path)}: observation file must contain a JSON object.")
            continue
        if "manifest_id" in payload:
            manifest_count += 1
            _validate_pending_manifest(
                payload,
                path=path,
                system_ids=system_ids,
                query_ids=query_ids,
                status_counts_by_system=status_counts_by_system,
                pending_slot_counts_by_system=pending_slot_counts_by_system,
                errors=errors,
            )
            continue
        records = payload.get("observations", [payload])
        if not isinstance(records, list):
            errors.append(f"{_rel(path)}: observations must be a list.")
            continue
        for index, record in enumerate(records):
            record_count += 1
            _validate_observation_record(
                record,
                source=f"{_rel(path)}#{index}",
                system_ids=system_ids,
                status_counts_by_system=status_counts_by_system,
                observed_query_ids_by_system=observed_query_ids_by_system,
                errors=errors,
            )

    systems = sorted(system_ids)
    status_counts = {
        system: dict(sorted(status_counts_by_system[system].items())) for system in systems
    }
    query_coverage = {
        system: {
            "pending_slots": pending_slot_counts_by_system[system],
            "observed_query_count": len(observed_query_ids_by_system[system]),
            "expected_query_count": len(query_ids),
        }
        for system in systems
    }
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "manual_external_baseline_observation_validator_v0",
        "systems": systems,
        "observations": {
            "directory": str(observations_dir),
            "file_count": len(observation_files),
            "manifest_count": manifest_count,
            "record_count": record_count,
        },
        "query_count": len(query_ids),
        "status_counts_by_system": status_counts,
        "query_coverage": query_coverage,
        "errors": errors,
    }


def _validate_systems(payload: Any, errors: list[str]) -> set[str]:
    system_ids: set[str] = set()
    if not isinstance(payload, Mapping):
        errors.append("systems.json: must contain an object.")
        return system_ids
    systems = payload.get("systems")
    if not isinstance(systems, list):
        errors.append("systems.json: systems must be a list.")
        return system_ids
    for index, system in enumerate(systems):
        if not isinstance(system, Mapping):
            errors.append(f"systems.json#systems/{index}: system must be an object.")
            continue
        system_id = _string(system.get("system_id"))
        if not system_id:
            errors.append(f"systems.json#systems/{index}: missing system_id.")
            continue
        system_ids.add(system_id)
        if system.get("observation_mode") != "manual_only":
            errors.append(f"systems.json#{system_id}: observation_mode must be manual_only.")
        if system.get("scraping_allowed") is not False:
            errors.append(f"systems.json#{system_id}: scraping_allowed must be false.")
        if system.get("automated_querying_allowed") is not False:
            errors.append(
                f"systems.json#{system_id}: automated_querying_allowed must be false."
            )
        if system.get("live_api_allowed") is not False:
            errors.append(f"systems.json#{system_id}: live_api_allowed must be false.")
    return system_ids


def _validate_schema(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("observation.schema.json: must contain an object.")
        return
    statuses = (
        payload.get("properties", {})
        .get("observation_status", {})
        .get("enum", [])
    )
    if set(statuses) != VALID_STATUSES:
        errors.append("observation.schema.json: observation_status enum drifted.")
    score_schema = payload.get("properties", {}).get("usefulness_scores", {})
    score_props = score_schema.get("properties", {}) if isinstance(score_schema, Mapping) else {}
    for field in SCORE_FIELDS:
        maximum = score_props.get(field, {}).get("maximum") if isinstance(score_props, Mapping) else None
        if maximum != 3:
            errors.append(f"observation.schema.json: score {field} must max at 3.")


def _validate_template(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("observation_template.json: must contain an object.")
        return
    if payload.get("observation_status") != PENDING_STATUS:
        errors.append("observation_template.json: must remain pending.")
    if payload.get("top_results") != []:
        errors.append("observation_template.json: must not contain top results.")
    if payload.get("collection_method") != PENDING_STATUS:
        errors.append("observation_template.json: collection_method must be pending.")
    if "<" not in json.dumps(payload, sort_keys=True):
        errors.append("observation_template.json: must contain placeholder markers.")


def _validate_pending_manifest(
    payload: Mapping[str, Any],
    *,
    path: Path,
    system_ids: set[str],
    query_ids: set[str],
    status_counts_by_system: dict[str, Counter[str]],
    pending_slot_counts_by_system: Counter[str],
    errors: list[str],
) -> None:
    if payload.get("observation_status") != PENDING_STATUS:
        errors.append(f"{_rel(path)}: pending manifest must use {PENDING_STATUS}.")
    if "top_results" in payload:
        errors.append(f"{_rel(path)}: pending manifest must not contain top_results.")
    required_systems = payload.get("required_system_ids")
    manifest_queries = payload.get("query_ids")
    if not isinstance(required_systems, list) or not all(isinstance(item, str) for item in required_systems):
        errors.append(f"{_rel(path)}: required_system_ids must be a string list.")
        required_systems = []
    if not isinstance(manifest_queries, list) or not all(isinstance(item, str) for item in manifest_queries):
        errors.append(f"{_rel(path)}: query_ids must be a string list.")
        manifest_queries = []
    unknown_systems = sorted(set(required_systems) - system_ids)
    if unknown_systems:
        errors.append(f"{_rel(path)}: unknown system ids {unknown_systems}.")
    missing_queries = sorted(query_ids - set(manifest_queries))
    extra_queries = sorted(set(manifest_queries) - query_ids)
    if missing_queries:
        errors.append(f"{_rel(path)}: missing query ids {missing_queries}.")
    if extra_queries:
        errors.append(f"{_rel(path)}: unknown query ids {extra_queries}.")
    for system_id in required_systems:
        if system_id not in system_ids:
            continue
        slot_count = len(manifest_queries)
        pending_slot_counts_by_system[system_id] += slot_count
        status_counts_by_system[system_id][PENDING_STATUS] += slot_count


def _validate_observation_record(
    record: Any,
    *,
    source: str,
    system_ids: set[str],
    status_counts_by_system: dict[str, Counter[str]],
    observed_query_ids_by_system: dict[str, set[str]],
    errors: list[str],
) -> None:
    if not isinstance(record, Mapping):
        errors.append(f"{source}: observation record must be an object.")
        return
    system_id = _string(record.get("system_id"))
    if system_id not in system_ids:
        errors.append(f"{source}: unknown system_id '{system_id}'.")
    status = _string(record.get("observation_status"))
    if status not in VALID_STATUSES:
        errors.append(f"{source}: invalid observation_status '{status}'.")
    collection_method = _string(record.get("collection_method")).casefold()
    if collection_method in FORBIDDEN_COLLECTION_METHODS:
        errors.append(f"{source}: collection_method must be manual, not {collection_method}.")
    if "scrap" in collection_method or "automated" in collection_method or "crawl" in collection_method:
        errors.append(f"{source}: collection_method claims prohibited automation.")
    if system_id in system_ids and status in VALID_STATUSES:
        status_counts_by_system[system_id][status] += 1
    top_results = record.get("top_results")
    if not isinstance(top_results, list):
        errors.append(f"{source}: top_results must be a list.")
    if status == "observed":
        for required in ("operator", "observed_at", "browser_or_tool", "exact_query_submitted"):
            value = _string(record.get(required))
            if not value or value.startswith("<"):
                errors.append(f"{source}: observed record missing {required}.")
        if system_id in system_ids:
            query_id = _string(record.get("query_id"))
            if query_id:
                observed_query_ids_by_system[system_id].add(query_id)
    if status == PENDING_STATUS:
        if top_results not in ([], None):
            errors.append(f"{source}: pending record must not contain top_results.")
        rank = record.get("first_useful_result_rank")
        if rank is not None:
            errors.append(f"{source}: pending record must not contain first useful rank.")
    scores = record.get("usefulness_scores")
    if scores is not None:
        if not isinstance(scores, Mapping):
            errors.append(f"{source}: usefulness_scores must be an object.")
        else:
            for key, value in scores.items():
                if not isinstance(value, int) or value < 0 or value > 3:
                    errors.append(f"{source}: score {key} must be an integer from 0 to 3.")


def _query_ids(payload: Any, errors: list[str]) -> set[str]:
    if not isinstance(payload, Mapping):
        errors.append("search_usefulness_v0.json: must contain an object.")
        return set()
    queries = payload.get("queries")
    if not isinstance(queries, list):
        errors.append("search_usefulness_v0.json: queries must be a list.")
        return set()
    query_ids = set()
    for index, query in enumerate(queries):
        if not isinstance(query, Mapping):
            errors.append(f"search_usefulness_v0.json#queries/{index}: query must be an object.")
            continue
        query_id = _string(query.get("id"))
        if not query_id:
            errors.append(f"search_usefulness_v0.json#queries/{index}: missing id.")
            continue
        query_ids.add(query_id)
    return query_ids


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: file not found.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON at line {exc.lineno}: {exc.msg}.")
    return None


def _format_plain_report(report: Mapping[str, Any]) -> str:
    lines = [
        "Manual external baseline observations",
        f"status: {report['status']}",
        f"query_count: {report['query_count']}",
        f"observation_files: {report['observations']['file_count']}",
    ]
    lines.append("")
    lines.append("Systems")
    for system_id in report["systems"]:
        coverage = report["query_coverage"][system_id]
        counts = report["status_counts_by_system"][system_id]
        lines.append(
            "- "
            f"{system_id}: pending={counts.get(PENDING_STATUS, 0)}, "
            f"observed={counts.get('observed', 0)}, "
            f"expected_queries={coverage['expected_query_count']}"
        )
    if report["errors"]:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


def _string(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
