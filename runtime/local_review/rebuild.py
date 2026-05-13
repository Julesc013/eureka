"""Local reviewed-index rebuild service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from runtime.public_index.rebuild import rebuild_reviewed_public_index

from .audit import build_rebuild_audit_event
from .errors import LocalReviewRebuildError


@dataclass(frozen=True)
class LocalReviewedIndexRebuildRequest:
    operator_label: str = "local_operator"
    dry_run: bool = True


@dataclass(frozen=True)
class LocalReviewedIndexRebuildResult:
    schema_version: str
    status: str
    dry_run: bool
    included_count: int
    excluded_count: int
    records: tuple[Mapping[str, Any], ...]
    excluded: tuple[Mapping[str, Any], ...]
    rebuild: Mapping[str, Any]
    audit_event: Mapping[str, Any]
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = (
        "local reviewed projection only",
        "input stores are not mutated by rebuild",
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "status": self.status,
            "dry_run": self.dry_run,
            "included_count": self.included_count,
            "excluded_count": self.excluded_count,
            "records": [dict(item) for item in self.records],
            "excluded": [dict(item) for item in self.excluded],
            "rebuild": dict(self.rebuild),
            "audit_event": dict(self.audit_event),
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
            "accepted_review_included_in_rebuild": self.included_count > 0,
            "rejected_blocked_reviews_excluded": True,
            "input_stores_mutated": False,
            "master_index_mutated": False,
            "site_dist_mutated": False,
            "deployment_performed": False,
        }


def rebuild_local_reviewed_index(runtime: Any, request: LocalReviewedIndexRebuildRequest) -> LocalReviewedIndexRebuildResult:
    if not str(request.operator_label or "").strip():
        raise LocalReviewRebuildError("operator label is required")
    root = Path(runtime.instance_ref.instance_root)
    paths = {
        store_id: root / runtime.store_manifest.stores[store_id].relative_path
        for store_id in ("source_cache", "evidence_ledger", "review_queue", "public_index")
    }
    report = rebuild_reviewed_public_index(
        paths["source_cache"],
        paths["evidence_ledger"],
        paths["review_queue"],
        paths["public_index"],
        include_statuses=("accepted",),
        dry_run=bool(request.dry_run),
    )
    audit_event = build_rebuild_audit_event(
        request.operator_label,
        bool(request.dry_run),
        int(report.get("included_count", 0) or 0),
        int(report.get("excluded_count", 0) or 0),
    )
    return LocalReviewedIndexRebuildResult(
        schema_version="local_reviewed_index_rebuild_result.v0",
        status="pass",
        dry_run=bool(request.dry_run),
        included_count=int(report.get("included_count", 0) or 0),
        excluded_count=int(report.get("excluded_count", 0) or 0),
        records=tuple(dict(item) for item in report.get("records", []) if isinstance(item, Mapping)),
        excluded=tuple(dict(item) for item in report.get("excluded", []) if isinstance(item, Mapping)),
        rebuild=dict(report.get("rebuild", {})),
        audit_event=audit_event,
    )
