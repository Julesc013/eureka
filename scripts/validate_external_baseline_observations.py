from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_BASELINE_ROOT = REPO_ROOT / "evals" / "search_usefulness" / "external_baselines"
DEFAULT_OBSERVATIONS_DIR = EXTERNAL_BASELINE_ROOT / "observations"
DEFAULT_BATCHES_DIR = EXTERNAL_BASELINE_ROOT / "batches"
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
    parser.add_argument(
        "--batches-dir",
        default=str(DEFAULT_BATCHES_DIR),
        help="Directory of manual observation batch directories.",
    )
    parser.add_argument(
        "--file",
        help="Validate one observation JSON file instead of the full observation area.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.file:
        report = validate_external_baseline_observation_file(Path(args.file))
    else:
        report = validate_external_baseline_observations(
            observations_dir=Path(args.observations_dir),
            batches_dir=Path(args.batches_dir),
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
    batches_dir: Path = DEFAULT_BATCHES_DIR,
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
                query_ids=query_ids,
                status_counts_by_system=status_counts_by_system,
                observed_query_ids_by_system=observed_query_ids_by_system,
                errors=errors,
            )

    batches = _validate_batches(
        batches_dir,
        system_ids=system_ids,
        query_ids=query_ids,
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
        "batches": batches,
        "query_count": len(query_ids),
        "status_counts_by_system": status_counts,
        "query_coverage": query_coverage,
        "errors": errors,
    }


def validate_external_baseline_observation_file(file_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    systems_payload = _load_json(EXTERNAL_BASELINE_ROOT / "systems.json", errors)
    schema_payload = _load_json(EXTERNAL_BASELINE_ROOT / "observation.schema.json", errors)
    template_payload = _load_json(EXTERNAL_BASELINE_ROOT / "observation_template.json", errors)
    query_pack = _load_json(QUERY_PACK_PATH, errors)

    system_ids = _validate_systems(systems_payload, errors)
    query_ids = _query_ids(query_pack, errors)
    _validate_schema(schema_payload, errors)
    _validate_template(template_payload, errors)

    status_counts_by_system: dict[str, Counter[str]] = defaultdict(Counter)
    observed_query_ids_by_system: dict[str, set[str]] = defaultdict(set)
    payload = _load_json(file_path, errors)
    record_count = 0
    if isinstance(payload, Mapping):
        records = payload.get("observations", [payload])
        if isinstance(records, list):
            for index, record in enumerate(records):
                record_count += 1
                _validate_observation_record(
                    record,
                    source=f"{_rel(file_path)}#{index}",
                    system_ids=system_ids,
                    query_ids=query_ids,
                    status_counts_by_system=status_counts_by_system,
                    observed_query_ids_by_system=observed_query_ids_by_system,
                    errors=errors,
                )
        else:
            errors.append(f"{_rel(file_path)}: observations must be a list.")
    elif payload is not None:
        errors.append(f"{_rel(file_path)}: observation file must contain a JSON object.")

    systems = sorted(system_ids)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "manual_external_baseline_observation_validator_v0",
        "file": str(file_path),
        "record_count": record_count,
        "systems": systems,
        "query_count": len(query_ids),
        "status_counts_by_system": {
            system: dict(sorted(status_counts_by_system[system].items()))
            for system in systems
        },
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
    query_ids: set[str],
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
    query_id = _string(record.get("query_id"))
    if query_id and query_id not in query_ids:
        errors.append(f"{source}: unknown query_id '{query_id}'.")
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
        if _contains_placeholder_value(record):
            errors.append(f"{source}: observed record must not contain template placeholders.")
        if not isinstance(top_results, list) or not top_results:
            errors.append(f"{source}: observed record must contain manually recorded top_results.")
        elif isinstance(top_results, list):
            for result_index, result in enumerate(top_results):
                _validate_top_result(
                    result,
                    source=f"{source}: top_results/{result_index}",
                    errors=errors,
                )
        scores = record.get("usefulness_scores")
        if not isinstance(scores, Mapping):
            errors.append(f"{source}: observed record must contain usefulness_scores.")
        else:
            missing_scores = sorted(SCORE_FIELDS - set(scores))
            if missing_scores:
                errors.append(f"{source}: observed record missing scores {missing_scores}.")
        if system_id in system_ids:
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


def _validate_top_result(result: Any, *, source: str, errors: list[str]) -> None:
    if not isinstance(result, Mapping):
        errors.append(f"{source}: result must be an object.")
        return
    rank = result.get("rank")
    if not isinstance(rank, int) or rank < 1:
        errors.append(f"{source}: rank must be an integer >= 1.")
    for required in ("title", "url_or_locator", "result_type"):
        value = _string(result.get(required))
        if not value or value.startswith("<"):
            errors.append(f"{source}: missing {required}.")
    if _contains_placeholder_value(result):
        errors.append(f"{source}: result must not contain template placeholders.")


def _contains_placeholder_value(value: Any) -> bool:
    if isinstance(value, str):
        normalized = value.strip().casefold()
        return normalized.startswith("<") or "<manual" in normalized or "manual observation required" in normalized
    if isinstance(value, Mapping):
        return any(_contains_placeholder_value(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_placeholder_value(item) for item in value)
    return False


def _validate_batches(
    batches_dir: Path,
    *,
    system_ids: set[str],
    query_ids: set[str],
    errors: list[str],
) -> dict[str, Any]:
    if not batches_dir.exists():
        return {}
    batch_reports: dict[str, Any] = {}
    for batch_dir in sorted(path for path in batches_dir.iterdir() if path.is_dir()):
        manifest_path = batch_dir / "batch_manifest.json"
        manifest = _load_json(manifest_path, errors)
        if not isinstance(manifest, Mapping):
            errors.append(f"{_rel(manifest_path)}: batch manifest must contain an object.")
            continue
        batch_id = _string(manifest.get("batch_id"))
        if not batch_id:
            errors.append(f"{_rel(manifest_path)}: missing batch_id.")
            batch_id = batch_dir.name
        selected_query_ids = _string_list(
            manifest.get("selected_query_ids"),
            source=f"{_rel(manifest_path)}: selected_query_ids",
            errors=errors,
        )
        selected_system_ids = _string_list(
            manifest.get("selected_system_ids"),
            source=f"{_rel(manifest_path)}: selected_system_ids",
            errors=errors,
        )
        expected_observation_count = manifest.get("expected_observation_count")
        unknown_queries = sorted(set(selected_query_ids) - query_ids)
        unknown_systems = sorted(set(selected_system_ids) - system_ids)
        if unknown_queries:
            errors.append(f"{_rel(manifest_path)}: unknown selected query ids {unknown_queries}.")
        if unknown_systems:
            errors.append(f"{_rel(manifest_path)}: unknown selected system ids {unknown_systems}.")
        if manifest.get("status") != PENDING_STATUS:
            errors.append(f"{_rel(manifest_path)}: batch status must be {PENDING_STATUS}.")

        computed_expected = len(selected_query_ids) * len(selected_system_ids)
        if expected_observation_count != computed_expected:
            errors.append(
                f"{_rel(manifest_path)}: expected_observation_count must be {computed_expected}."
            )

        observations_path = (
            batch_dir / "observations" / f"pending_{batch_id}_observations.json"
        )
        payload = _load_json(observations_path, errors)
        records = []
        if not isinstance(payload, Mapping):
            errors.append(f"{_rel(observations_path)}: batch observations must contain an object.")
        else:
            if payload.get("observation_status") != PENDING_STATUS:
                errors.append(
                    f"{_rel(observations_path)}: batch pending file must use {PENDING_STATUS}."
                )
            raw_records = payload.get("observations")
            if not isinstance(raw_records, list):
                errors.append(f"{_rel(observations_path)}: observations must be a list.")
            else:
                records = raw_records

        selected_query_set = set(selected_query_ids)
        selected_system_set = set(selected_system_ids)
        slot_keys: set[tuple[str, str]] = set()
        status_counts: Counter[str] = Counter()
        observed_query_ids: set[str] = set()
        observation_slots: list[dict[str, Any]] = []
        for index, record in enumerate(records):
            source = f"{_rel(observations_path)}#{index}"
            if isinstance(record, Mapping):
                query_id = _string(record.get("query_id"))
                system_id = _string(record.get("system_id"))
                status = _string(record.get("observation_status"))
                observation_slots.append(
                    {
                        "batch_id": batch_id,
                        "observation_id": _string(record.get("observation_id")),
                        "query_id": query_id,
                        "query_text": _string(record.get("query_text")),
                        "system_id": system_id,
                        "observation_status": status,
                    }
                )
                if query_id not in selected_query_set:
                    errors.append(f"{source}: query_id must be selected by the batch.")
                if system_id not in selected_system_set:
                    errors.append(f"{source}: system_id must be selected by the batch.")
                if (query_id, system_id) in slot_keys:
                    errors.append(f"{source}: duplicate query/system slot {query_id}/{system_id}.")
                slot_keys.add((query_id, system_id))
                if record.get("observation_status") == PENDING_STATUS and record.get("top_results") != []:
                    errors.append(f"{source}: pending batch slot must not contain top_results.")
            temp_status_counts: dict[str, Counter[str]] = defaultdict(Counter)
            temp_observed_query_ids: dict[str, set[str]] = defaultdict(set)
            _validate_observation_record(
                record,
                source=source,
                system_ids=system_ids,
                query_ids=query_ids,
                status_counts_by_system=temp_status_counts,
                observed_query_ids_by_system=temp_observed_query_ids,
                errors=errors,
            )
            if isinstance(record, Mapping):
                status = _string(record.get("observation_status"))
                if status in VALID_STATUSES:
                    status_counts[status] += 1
                if status == "observed":
                    query_id = _string(record.get("query_id"))
                    if query_id:
                        observed_query_ids.add(query_id)

        missing_slots = sorted(
            f"{query_id}::{system_id}"
            for query_id in selected_query_ids
            for system_id in selected_system_ids
            if (query_id, system_id) not in slot_keys
        )
        if missing_slots:
            errors.append(f"{_rel(observations_path)}: missing observation slots {missing_slots}.")
        if len(records) != computed_expected:
            errors.append(
                f"{_rel(observations_path)}: expected {computed_expected} observations, found {len(records)}."
            )
        observed_count = status_counts.get("observed", 0)
        batch_reports[batch_id] = {
            "directory": str(batch_dir),
            "status": manifest.get("status"),
            "selected_query_count": len(selected_query_ids),
            "selected_system_count": len(selected_system_ids),
            "expected_observation_count": computed_expected,
            "observation_file": str(observations_path),
            "observation_count": len(records),
            "status_counts": dict(sorted(status_counts.items())),
            "pending_observation_count": status_counts.get(PENDING_STATUS, 0),
            "observed_observation_count": observed_count,
            "completion_percent": 0
            if computed_expected == 0
            else round((observed_count / computed_expected) * 100, 2),
            "selected_query_ids": selected_query_ids,
            "selected_system_ids": selected_system_ids,
            "missing_observation_slots": missing_slots,
            "observed_query_ids": sorted(observed_query_ids),
            "observation_slots": observation_slots,
            "next_pending_slots": [
                slot for slot in observation_slots if slot["observation_status"] == PENDING_STATUS
            ],
        }
    return dict(sorted(batch_reports.items()))


def _string_list(value: Any, *, source: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{source} must be a string list.")
        return []
    return list(value)


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
    if "file" in report:
        lines = [
            "Manual external baseline observation file",
            f"status: {report['status']}",
            f"file: {report['file']}",
            f"record_count: {report['record_count']}",
        ]
        if report["errors"]:
            lines.append("")
            lines.append("Errors")
            lines.extend(f"- {error}" for error in report["errors"])
        return "\n".join(lines) + "\n"

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
    batches = report.get("batches", {})
    if isinstance(batches, Mapping) and batches:
        lines.append("")
        lines.append("Batches")
        for batch_id, batch in sorted(batches.items()):
            if not isinstance(batch, Mapping):
                continue
            lines.append(
                "- "
                f"{batch_id}: pending={batch.get('pending_observation_count', 0)}, "
                f"observed={batch.get('observed_observation_count', 0)}, "
                f"expected={batch.get('expected_observation_count', 0)}, "
                f"completion={batch.get('completion_percent', 0)}%"
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
