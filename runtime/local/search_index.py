"""Deterministic local search index helpers for the Eureka local MVP."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence
from urllib.parse import quote_plus

from evals.hard_queries import fixture_cases


INDEX_SCHEMA_VERSION = "eureka.local_search_index.v0"
INDEX_DOCUMENT_SCHEMA_VERSION = "eureka.local_search_index_document.v0"
DEFAULT_INDEX_PATH = ".eureka/local_search_index.json"
SUPPORTED_INDEX_MODES = ("none", "local")
LOCAL_DEMO_SOURCE = "local_demo"
CANONICAL_STATUSES = (
    "verified",
    "candidate",
    "need",
    "near_miss",
    "policy_blocked",
    "unavailable",
    "unknown",
)
REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_METADATA_FIXTURE_PATH = REPO_ROOT / "evals" / "hard_queries" / "local_metadata_fallback_demo" / "ia_metadata_fixtures.json"
HARD_QUERY_FIXTURE_PATH = REPO_ROOT / "evals" / "hard_queries" / "fixtures_v0.py"

_STOPWORDS = {
    "a",
    "an",
    "and",
    "app",
    "apps",
    "for",
    "in",
    "index",
    "local",
    "of",
    "query",
    "the",
    "to",
    "with",
}


@dataclass(frozen=True)
class IndexSearchState:
    enabled: bool
    loaded: bool
    path: str
    document_count: int
    results: tuple[dict[str, Any], ...]
    errors: tuple[str, ...] = ()
    reviewed_record_count: int = 0
    artifact_verified_count: int = 0


def build_local_demo_index(*, reviewed_records_path: str | Path | None = None) -> dict[str, Any]:
    """Build a deterministic local-demo search index from committed fixtures."""

    reviewed_documents = _documents_from_reviewed_records(reviewed_records_path)
    documents = _sorted_documents(
        [
            *_documents_from_hard_query_fixtures(),
            *_documents_from_ia_demo_fixtures(),
            *reviewed_documents,
        ]
    )
    source_manifest = _source_manifest(reviewed_records_path)
    metadata_without_digest = {
        "index_schema_version": INDEX_SCHEMA_VERSION,
        "source": LOCAL_DEMO_SOURCE,
        "source_manifest": source_manifest,
        "source_digest": "",
        "reviewed_records_source": str(reviewed_records_path or ""),
        "document_count": len(documents),
        "status_counts": _counts(document.get("status") for document in documents),
        "source_family_counts": _counts(document.get("source_family") for document in documents),
        "reviewed_record_count": sum(1 for document in documents if document.get("record_state") == "reviewed"),
        "review_state_counts": _counts(document.get("review_state") for document in documents if document.get("review_state")),
        "artifact_verified_count": sum(1 for document in documents if document.get("artifact_verified") is True),
        "deterministic_build": True,
    }
    digest = _stable_digest({"metadata": metadata_without_digest, "documents": documents})
    metadata = {**metadata_without_digest, "source_digest": digest}
    return {
        **metadata,
        "documents": documents,
    }


def write_index(path: str | Path, index: Mapping[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_index_json(index), encoding="utf-8")


def render_index_json(index: Mapping[str, Any]) -> str:
    return json.dumps(index, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def load_index(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_index(index: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if index.get("index_schema_version") != INDEX_SCHEMA_VERSION:
        errors.append("index_schema_version must be eureka.local_search_index.v0")
    documents = index.get("documents")
    if not isinstance(documents, list):
        errors.append("documents must be a list")
        documents = []
    document_count = index.get("document_count")
    if not isinstance(document_count, int) or document_count != len(documents):
        errors.append("document_count must match documents length")

    status_counts = _counts(document.get("status") for document in documents if isinstance(document, Mapping))
    if dict(index.get("status_counts") or {}) != status_counts:
        errors.append("status_counts must match documents")
    source_family_counts = _counts(document.get("source_family") for document in documents if isinstance(document, Mapping))
    if dict(index.get("source_family_counts") or {}) != source_family_counts:
        errors.append("source_family_counts must match documents")
    reviewed_record_count = sum(1 for document in documents if isinstance(document, Mapping) and document.get("record_state") == "reviewed")
    if int(index.get("reviewed_record_count") or 0) != reviewed_record_count:
        errors.append("reviewed_record_count must match documents")
    review_state_counts = _counts(document.get("review_state") for document in documents if isinstance(document, Mapping) and document.get("review_state"))
    if dict(index.get("review_state_counts") or {}) != review_state_counts:
        errors.append("review_state_counts must match documents")
    artifact_verified_count = sum(1 for document in documents if isinstance(document, Mapping) and document.get("artifact_verified") is True)
    if int(index.get("artifact_verified_count") or 0) != artifact_verified_count:
        errors.append("artifact_verified_count must match documents")

    seen_ids: set[str] = set()
    for position, document in enumerate(documents):
        if not isinstance(document, Mapping):
            errors.append(f"documents[{position}] must be an object")
            continue
        doc_id = str(document.get("id") or "")
        if not doc_id:
            errors.append(f"documents[{position}].id is required")
        if doc_id in seen_ids:
            errors.append(f"duplicate document id: {doc_id}")
        seen_ids.add(doc_id)
        status = str(document.get("status") or "unknown")
        if status not in CANONICAL_STATUSES:
            errors.append(f"{doc_id or position}: unsupported status {status}")
        if document.get("verified") is True and status != "verified":
            errors.append(f"{doc_id or position}: non-reviewed document cannot be verified")
        if document.get("accepted_truth") is True and status != "verified":
            errors.append(f"{doc_id or position}: non-reviewed document cannot be accepted truth")
        if document.get("artifact_verified") is True and document.get("accepted_truth") is not True:
            errors.append(f"{doc_id or position}: artifact_verified requires accepted truth")
        if status != "verified" and not str(document.get("non_verified_reason") or ""):
            errors.append(f"{doc_id or position}: non_verified_reason is required")
        if not str(document.get("normalized_search_text") or ""):
            errors.append(f"{doc_id or position}: normalized_search_text is required")
    if index.get("deterministic_build") is not True:
        errors.append("deterministic_build must be true")
    return errors


def stats_payload(index: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "index_schema_version": str(index.get("index_schema_version") or ""),
        "source": str(index.get("source") or ""),
        "source_digest": str(index.get("source_digest") or ""),
        "document_count": int(index.get("document_count") or 0),
        "status_counts": dict(index.get("status_counts") or {}),
        "source_family_counts": dict(index.get("source_family_counts") or {}),
        "reviewed_records_source": str(index.get("reviewed_records_source") or ""),
        "reviewed_record_count": int(index.get("reviewed_record_count") or 0),
        "review_state_counts": dict(index.get("review_state_counts") or {}),
        "artifact_verified_count": int(index.get("artifact_verified_count") or 0),
        "deterministic_build": bool(index.get("deterministic_build")),
    }


def search_index_path(path: str | Path, query: str, *, limit: int) -> IndexSearchState:
    index_path = str(path)
    if not Path(path).is_file():
        return IndexSearchState(
            enabled=True,
            loaded=False,
            path=index_path,
            document_count=0,
            results=(),
            errors=(f"index file not found: {index_path}",),
        )
    try:
        index = load_index(path)
    except (OSError, json.JSONDecodeError) as exc:
        return IndexSearchState(
            enabled=True,
            loaded=False,
            path=index_path,
            document_count=0,
            results=(),
            errors=(f"index file could not be loaded: {type(exc).__name__}",),
        )
    validation_errors = tuple(validate_index(index))
    documents = index.get("documents") if isinstance(index.get("documents"), list) else []
    if validation_errors:
        return IndexSearchState(
            enabled=True,
            loaded=False,
            path=index_path,
            document_count=len(documents),
            results=(),
            errors=validation_errors,
        )
    matches = tuple(_search_documents(documents, query, limit=max(1, min(int(limit), 25))))
    return IndexSearchState(
        enabled=True,
        loaded=True,
        path=index_path,
        document_count=len(documents),
        results=matches,
        reviewed_record_count=int(index.get("reviewed_record_count") or 0),
        artifact_verified_count=int(index.get("artifact_verified_count") or 0),
    )


def index_file_status(index_mode: str, index_path: str) -> dict[str, Any]:
    enabled = index_mode == "local"
    if not enabled:
        return {
            "index_mode": "none",
            "index_enabled": False,
            "index_loaded": False,
            "index_path": str(index_path),
            "index_document_count": 0,
            "reviewed_record_count": 0,
            "artifact_verified_count": 0,
            "index_errors": [],
        }
    state = search_index_path(index_path, "", limit=1)
    return {
        "index_mode": "local",
        "index_enabled": True,
        "index_loaded": state.loaded,
        "index_path": state.path,
        "index_document_count": state.document_count,
        "reviewed_record_count": state.reviewed_record_count,
        "artifact_verified_count": state.artifact_verified_count,
        "index_errors": list(state.errors),
    }


def document_to_result_card(document: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "result_id": str(document.get("id") or "index-result"),
        "status": str(document.get("status") or "unknown"),
        "title": str(document.get("title") or "Indexed result"),
        "summary": str(document.get("summary") or ""),
        "source_hints": _string_list(document.get("source_hints")),
        "evidence_hints": _string_list(document.get("evidence_hints")),
        "missing": _string_list(document.get("missing_information")),
        "safe_next_action": str(document.get("safe_next_action") or "review indexed result before reuse"),
        "non_verified_reason": str(document.get("non_verified_reason") or ""),
        "verified": bool(document.get("verified") is True),
        "accepted_truth": bool(document.get("accepted_truth") is True),
        "review_required": bool(document.get("review_required") is True),
        "record_state": str(document.get("record_state") or ""),
        "review_state": str(document.get("review_state") or ""),
        "reviewed_record_id": str(document.get("reviewed_record_id") or ""),
        "review_event_id": str(document.get("review_event_id") or ""),
        "artifact_verified": bool(document.get("artifact_verified") is True),
        "provenance": dict(document.get("provenance") or {}),
        "index_document_id": str(document.get("id") or ""),
    }


def _documents_from_hard_query_fixtures() -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for fixture in fixture_cases():
        fallback = dict(fixture.get("fallback_summary") or {})
        query_text = str(fixture.get("query_text") or "")
        status = str(fixture.get("expected_status") or fallback.get("status") or "unknown")
        candidates = [item for item in fallback.get("candidates") or [] if isinstance(item, Mapping)]
        needs = [item for item in fallback.get("needs") or [] if isinstance(item, Mapping)]
        if candidates:
            for candidate in candidates:
                documents.append(_document_from_hard_query_item(fixture, fallback, candidate, status=str(candidate.get("status") or status), kind="candidate"))
        elif needs:
            for need in needs:
                documents.append(_document_from_hard_query_item(fixture, fallback, need, status=str(need.get("status") or status), kind="need"))
        else:
            documents.append(_document_from_hard_query_item(fixture, fallback, fallback, status=status, kind="fallback_state"))
        if query_text:
            documents[-1]["matched_queries"] = sorted(set([*documents[-1]["matched_queries"], query_text]))
    return documents


def _document_from_hard_query_item(
    fixture: Mapping[str, Any],
    fallback: Mapping[str, Any],
    item: Mapping[str, Any],
    *,
    status: str,
    kind: str,
) -> dict[str, Any]:
    query_text = str(fixture.get("query_text") or fallback.get("query") or "")
    query_id = str(fixture.get("query_id") or _stable_id("hard-query", query_text))
    item_id = str(item.get("candidate_id") or item.get("need_id") or query_id)
    title = str(item.get("title") or fallback.get("title") or query_text or item_id)
    summary = str(item.get("summary") or fallback.get("evidence_summary") or "Local demo fixture result; review required.")
    source_family = str(fallback.get("source_family") or "eval_fixture")
    source_id = str(fallback.get("source_id") or "synthetic_hard_query_fixture")
    reason_codes = _string_list(fallback.get("reason_codes"))
    missing = _missing_information(status, reason_codes)
    return _index_document(
        doc_id=f"local-demo:hard-query:{query_id}:{item_id}",
        title=title,
        summary=summary,
        query_hints=[query_text, title, summary, query_id, *reason_codes],
        matched_queries=[query_text],
        status=status,
        category=kind,
        source_family=source_family,
        source_hints=[source_id, source_family],
        evidence_hints=[summary, *[f"reason: {reason}" for reason in reason_codes]],
        missing_information=missing,
        safe_next_action=_safe_next_action(status, reason_codes),
        non_verified_reason="local demo hard-query fixture is not reviewed truth",
        provenance={
            "source": LOCAL_DEMO_SOURCE,
            "source_kind": "hard_query_fixture",
            "source_ref": "evals/hard_queries/fixtures_v0.py",
            "query_id": query_id,
        },
    )


def _documents_from_ia_demo_fixtures() -> list[dict[str, Any]]:
    if not LOCAL_METADATA_FIXTURE_PATH.is_file():
        return []
    payload = json.loads(LOCAL_METADATA_FIXTURE_PATH.read_text(encoding="utf-8"))
    documents: list[dict[str, Any]] = []
    for case in payload.get("cases") or []:
        if not isinstance(case, Mapping):
            continue
        query_text = str(case.get("query_text") or "")
        case_id = str(case.get("case_id") or _stable_id("ia-demo", query_text))
        docs = [item for item in case.get("docs") or [] if isinstance(item, Mapping)]
        if not docs:
            documents.append(
                _index_document(
                    doc_id=f"local-demo:ia-fixture:{case_id}:need",
                    title=f"Need more source evidence for {query_text}",
                    summary="IA fixture contains no metadata candidate for this query; more source evidence or narrower scope is needed.",
                    query_hints=[query_text, case_id],
                    matched_queries=[query_text],
                    status="need",
                    category="need",
                    source_family="internet_archive",
                    source_hints=["internet_archive_metadata", "internet_archive"],
                    evidence_hints=["reason: fallback_no_candidates"],
                    missing_information=["more source evidence or narrower query scope"],
                    safe_next_action="collect missing scope or source evidence",
                    non_verified_reason="fixture-derived search need is not reviewed truth",
                    provenance={
                        "source": LOCAL_DEMO_SOURCE,
                        "source_kind": "ia_metadata_fixture",
                        "source_ref": "evals/hard_queries/local_metadata_fallback_demo/ia_metadata_fixtures.json",
                        "case_id": case_id,
                    },
                )
            )
            continue
        for doc in docs:
            identifier = str(doc.get("identifier") or _stable_id("ia-doc", doc))
            title = str(doc.get("title") or identifier)
            summary = str(doc.get("description") or "IA fixture metadata candidate; review required.")
            documents.append(
                _index_document(
                    doc_id=f"local-demo:ia-fixture:{case_id}:{identifier}",
                    title=title,
                    summary=summary,
                    query_hints=[query_text, case_id, identifier, title, summary],
                    matched_queries=[query_text],
                    status="candidate",
                    category="ia_metadata_candidate",
                    source_family="internet_archive",
                    source_hints=[
                        "internet_archive_metadata",
                        "internet_archive",
                        f"https://archive.org/details/{quote_plus(identifier)}",
                    ],
                    evidence_hints=[summary, identifier, "reason: fallback_candidates_available"],
                    missing_information=["human review before truth promotion"],
                    safe_next_action="review candidate metadata and evidence before promotion",
                    non_verified_reason="IA fixture metadata is not reviewed truth",
                    provenance={
                        "source": LOCAL_DEMO_SOURCE,
                        "source_kind": "ia_metadata_fixture",
                        "source_ref": "evals/hard_queries/local_metadata_fallback_demo/ia_metadata_fixtures.json",
                        "case_id": case_id,
                        "identifier": identifier,
                    },
                )
            )
    return documents


def _documents_from_reviewed_records(path: str | Path | None) -> list[dict[str, Any]]:
    if path is None or str(path or "") == "":
        return []
    source = Path(path)
    if not source.is_file():
        raise ValueError(f"reviewed records file not found: {source}")
    documents: list[dict[str, Any]] = []
    for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{source}:{line_number}: invalid reviewed-record JSONL row: {exc.msg}") from exc
        if not isinstance(record, Mapping):
            raise ValueError(f"{source}:{line_number}: reviewed-record row must be an object")
        errors = _validate_reviewed_record(record)
        if errors:
            raise ValueError(f"{source}:{line_number}: " + "; ".join(errors))
        documents.append(_document_from_reviewed_record(record, source))
    return documents


def _document_from_reviewed_record(record: Mapping[str, Any], source: Path) -> dict[str, Any]:
    record_id = str(record.get("reviewed_record_id") or "")
    title = str(record.get("title") or record_id)
    summary = str(record.get("summary") or "Local reviewed source lead.")
    status = str(record.get("status") or "candidate")
    evidence_hints = _string_list(record.get("evidence_hints"))
    source_hints = _string_list(record.get("source_hints"))
    query_hints = _string_list(record.get("query_hints")) or [
        title,
        summary,
        str(record.get("source_candidate_id") or ""),
        str(record.get("review_reason") or ""),
    ]
    matched_queries = _string_list(record.get("matched_queries")) or query_hints
    return _index_document(
        doc_id=record_id,
        title=title,
        summary=summary,
        query_hints=query_hints,
        matched_queries=matched_queries,
        status=status,
        category="local_reviewed_record",
        source_family=str(record.get("source_family") or "local_review"),
        source_hints=source_hints,
        evidence_hints=evidence_hints,
        missing_information=_string_list(record.get("missing_information")),
        safe_next_action=str(
            record.get("safe_next_action")
            or "use this local reviewed source lead as search context; artifact verification remains deferred"
        ),
        non_verified_reason=str(record.get("non_verified_reason") or "local reviewed metadata/source lead is not a verified artifact"),
        provenance={
            **dict(record.get("provenance") or {}),
            "source_ref": str(source).replace("\\", "/"),
        },
        extra_fields={
            "record_state": str(record.get("record_state") or "reviewed"),
            "review_state": str(record.get("review_state") or "accepted"),
            "reviewed_record_id": record_id,
            "review_event_id": str(record.get("source_review_event_id") or ""),
            "source_candidate_id": str(record.get("source_candidate_id") or ""),
            "artifact_verified": bool(record.get("artifact_verified") is True),
            "accepted_truth": bool(record.get("accepted_truth") is True),
            "verified": bool(record.get("accepted_truth") is True),
            "review_required": False,
            "reviewer": str(record.get("reviewer") or ""),
            "review_reason": str(record.get("review_reason") or ""),
            "reviewed_at": str(record.get("reviewed_at") or ""),
        },
    )


def _validate_reviewed_record(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("reviewed_record_id", "source_candidate_id", "source_review_event_id", "title", "review_state"):
        if not str(record.get(key) or "").strip():
            errors.append(f"{key} is required")
    if str(record.get("review_state") or "") != "accepted":
        errors.append("review_state must be accepted")
    if bool(record.get("artifact_verified") is True):
        errors.append("artifact_verified must remain false for local reviewed metadata/source leads")
    if bool(record.get("accepted_truth") is True):
        errors.append("accepted_truth must remain false for local reviewed metadata/source leads")
    if not _string_list(record.get("evidence_hints")):
        errors.append("evidence_hints are required")
    return errors


def _index_document(
    *,
    doc_id: str,
    title: str,
    summary: str,
    query_hints: Sequence[str],
    matched_queries: Sequence[str],
    status: str,
    category: str,
    source_family: str,
    source_hints: Sequence[str],
    evidence_hints: Sequence[str],
    missing_information: Sequence[str],
    safe_next_action: str,
    non_verified_reason: str,
    provenance: Mapping[str, Any],
    extra_fields: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    searchable_text = _normalize_search_text(
        " ".join([title, summary, status, category, source_family, *query_hints, *evidence_hints])
    )
    verified = status == "verified"
    document = {
        "schema_version": INDEX_DOCUMENT_SCHEMA_VERSION,
        "id": doc_id,
        "title": title,
        "summary": summary,
        "query_hints": sorted(set(query_hints)),
        "matched_queries": sorted(set(matched_queries)),
        "normalized_search_text": searchable_text,
        "status": status if status in CANONICAL_STATUSES else "unknown",
        "type": category,
        "category": category,
        "source_family": source_family,
        "source_hints": sorted(set(source_hints)),
        "evidence_hints": sorted(set(evidence_hints)),
        "missing_information": sorted(set(missing_information)),
        "safe_next_action": safe_next_action,
        "non_verified_reason": "" if verified else non_verified_reason,
        "verified": verified,
        "accepted_truth": verified,
        "review_required": status in {"candidate", "near_miss"},
        "provenance": dict(provenance),
        "no_mutation": {
            "reviewed_records_mutated": False,
            "review_ledgers_mutated": False,
            "reviewed_index_mutated": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "truth_promotion_performed": False,
        },
    }
    document.update(dict(extra_fields or {}))
    return document


def _search_documents(documents: Sequence[Any], query: str, limit: int) -> list[dict[str, Any]]:
    query_text = _normalize_search_text(query)
    query_tokens = _query_tokens(query)
    scored: list[tuple[int, int, int, str, dict[str, Any]]] = []
    for item in documents:
        if not isinstance(item, Mapping):
            continue
        score = _document_score(item, query_text, query_tokens)
        if score <= 0:
            continue
        document = dict(item)
        document["index_score"] = score
        scored.append(
            (
                score,
                _review_rank(document),
                _status_rank(str(document.get("status") or "unknown")),
                str(document.get("id") or ""),
                document,
            )
        )
    scored.sort(key=lambda item: (-item[0], item[1], item[2], item[3]))
    return [document for _score, _review_rank_value, _status_rank_value, _doc_id, document in scored[:limit]]


def _document_score(document: Mapping[str, Any], query_text: str, query_tokens: Sequence[str]) -> int:
    if not query_text:
        return 0
    matched_queries = [_normalize_search_text(item) for item in _string_list(document.get("matched_queries"))]
    if query_text in matched_queries:
        return 1000
    searchable = str(document.get("normalized_search_text") or "")
    if query_text and query_text in searchable:
        return 600 + len(query_text)
    if not query_tokens:
        return 0
    token_matches = sum(1 for token in query_tokens if token in searchable)
    required = max(1, min(2, len(query_tokens)))
    if token_matches < required:
        return 0
    return token_matches * 20


def _query_tokens(query: str) -> list[str]:
    tokens = [token for token in re.findall(r"[a-z0-9]+", _normalize_search_text(query)) if token not in _STOPWORDS]
    return sorted(set(tokens))


def _normalize_search_text(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())[:4000]


def _sorted_documents(documents: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return sorted((dict(document) for document in documents), key=lambda item: str(item.get("id") or ""))


def _source_manifest(reviewed_records_path: str | Path | None = None) -> list[dict[str, str]]:
    paths = [HARD_QUERY_FIXTURE_PATH, LOCAL_METADATA_FIXTURE_PATH]
    if reviewed_records_path:
        paths.append(Path(reviewed_records_path))
    manifest = []
    for path in paths:
        resolved = path if path.is_absolute() else REPO_ROOT / path
        if not resolved.is_file():
            continue
        try:
            display_path = str(resolved.relative_to(REPO_ROOT)).replace("\\", "/")
        except ValueError:
            display_path = str(resolved).replace("\\", "/")
        manifest.append(
            {
                "path": display_path,
                "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest(),
            }
        )
    return sorted(manifest, key=lambda item: item["path"])


def _counts(values: Any) -> dict[str, int]:
    counter = Counter(str(value or "unknown") for value in values)
    return {key: counter[key] for key in sorted(counter)}


def _stable_digest(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _stable_id(prefix: str, *parts: Any) -> str:
    encoded = json.dumps(parts, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str).encode("utf-8")
    return f"{prefix}:{hashlib.sha256(encoded).hexdigest()[:16]}"


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple, set)):
        return []
    return [str(item) for item in value if item not in (None, "")]


def _missing_information(status: str, reason_codes: Sequence[str]) -> list[str]:
    reasons = set(reason_codes)
    missing: list[str] = []
    if "hardware_identifier_missing" in reasons:
        missing.extend(["hardware vendor", "hardware model", "device id or chipset", "exact Windows 98 version"])
    if status in {"candidate", "near_miss"}:
        missing.append("human review before truth promotion")
    if status == "need":
        missing.append("more source evidence or narrower query scope")
    if status == "policy_blocked":
        missing.append("policy/review approval")
    if status == "unavailable":
        missing.append("available source response or fixture coverage")
    return sorted(set(missing))


def _safe_next_action(status: str, reason_codes: Sequence[str]) -> str:
    if "hardware_identifier_missing" in set(reason_codes):
        return "collect hardware vendor, model, device id or chipset, bus/interface, and exact Windows 98 version"
    if status == "verified":
        return "inspect local evidence before reuse"
    if status == "candidate":
        return "review candidate metadata and evidence before promotion"
    if status == "near_miss":
        return "refine identity clues and compare near-miss evidence"
    if status == "need":
        return "collect missing scope or source evidence"
    if status == "policy_blocked":
        return "wait for the relevant review or policy gate"
    if status == "unavailable":
        return "retry with narrower scope or add reviewed fixture coverage"
    return "refine the query"


def _status_rank(status: str) -> int:
    order = {
        "verified": 0,
        "candidate": 1,
        "need": 2,
        "near_miss": 3,
        "policy_blocked": 4,
        "unavailable": 5,
        "unknown": 6,
    }
    return order.get(status, 6)


def _review_rank(document: Mapping[str, Any]) -> int:
    if document.get("record_state") == "reviewed" and document.get("review_state") == "accepted":
        return 0
    return 1
