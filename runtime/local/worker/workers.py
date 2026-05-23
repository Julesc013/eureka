"""Deterministic local worker functions."""

from typing import Any, Mapping

from runtime.local.review import rebuild_reviewed_index


def run_noop_worker(runtime: Any, workunit: Any) -> dict[str, Any]:
    return {
        "outputs": {
            "message": "noop completed",
            "workunit_id": workunit.id,
        },
        "store_mutations": (),
        "warnings": (),
        "limitations": ("local deterministic noop only",),
    }


def run_review_queue_checker(runtime: Any, workunit: Any) -> dict[str, Any]:
    summary = runtime.review_queue.summarize()
    return {
        "outputs": {
            "review_queue": summary.to_dict() if hasattr(summary, "to_dict") else dict(summary),
        },
        "store_mutations": (),
        "warnings": (),
        "limitations": ("local review queue summary only",),
    }


def run_reviewed_index_rebuild_worker(runtime: Any, workunit: Any, operator_context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    context = operator_context if isinstance(operator_context, Mapping) else {}
    operator_label = str(context.get("operator_label") or "local_operator")
    dry_run = bool(workunit.payload.get("dry_run", False))
    result = rebuild_reviewed_index(runtime, operator_label=operator_label, dry_run=dry_run)
    mutation = () if dry_run else (
        {
            "store_id": "public_index",
            "mutation": "reviewed_index_rebuild",
            "allowed": True,
        },
    )
    return {
        "outputs": {
            "rebuild": result,
        },
        "store_mutations": mutation,
        "warnings": tuple(result.get("warnings", [])),
        "limitations": tuple(result.get("limitations", [])) + ("master index is not mutated",),
    }


def run_absence_report_worker(runtime: Any, workunit: Any) -> dict[str, Any]:
    query = str(workunit.payload.get("query") or workunit.payload.get("q") or workunit.title)
    report = runtime.public_index.absence_report(query).to_dict()
    return {
        "outputs": {
            "absence_report": report,
        },
        "store_mutations": (),
        "warnings": tuple(report.get("warnings", [])),
        "limitations": tuple(report.get("limitations", [])) + ("absence is local/current-index only",),
    }


def run_local_status_snapshot_worker(runtime: Any, workunit: Any) -> dict[str, Any]:
    status = runtime.status().to_dict()
    return {
        "outputs": {
            "runtime_status": status,
        },
        "store_mutations": (),
        "warnings": tuple(status.get("warnings", [])),
        "limitations": ("local status snapshot only",),
    }
