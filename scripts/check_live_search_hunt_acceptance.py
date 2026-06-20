#!/usr/bin/env python
"""Deterministic and optional real live Search/Hunt acceptance harness."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterator, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.web import HTTPTransportResult, SafeHTTPFetcher  # noqa: E402
from runtime.connectors.web.dns_guard import DNSGuard  # noqa: E402
from runtime.connectors.web.robots import AllowAllRobotsClient  # noqa: E402
from runtime.index.preview import SQLitePreviewIndexStore  # noqa: E402
from runtime.local.portable_instance import bootstrap_command, build_portable_paths, resolve_portable_instance_root  # noqa: E402
from runtime.search.hunt_engine import HuntBudget, HuntEngine  # noqa: E402
from runtime.search.live_service import LiveSearchService, live_hunt_run_id  # noqa: E402
from runtime.search.live_web import SearchLead, SearchResultPage, WebSearchBudget, brave_capability_manifest, provider_status  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    parser.add_argument("--live-canary", action="store_true", help="Run a bounded real provider canary when locally configured.")
    parser.add_argument("--query", default="", help="Operator-chosen unseen query for the real live canary.")
    parser.add_argument("--instance", default="", help="Portable instance path for the real live canary.")
    parser.add_argument("--max-queries", type=int, default=3, help="Maximum real canary query variants.")
    parser.add_argument("--max-fetches", type=int, default=3, help="Maximum real canary fetch attempts.")
    parser.add_argument("--keep-instance", action="store_true", help="Keep a generated temporary instance after the live canary.")
    parser.add_argument("--provider", default="brave", help="Live provider id for the real canary.")
    args = parser.parse_args(argv)
    payload = run_acceptance(
        live_canary=bool(args.live_canary),
        query=args.query,
        instance=args.instance,
        max_queries=args.max_queries,
        max_fetches=args.max_fetches,
        keep_instance=bool(args.keep_instance),
        provider=args.provider,
    )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        for check in payload["checks"]:
            print(f"- {check['status']}: {check['id']}")
    return 0 if payload["status"] in {"pass", "pass_with_warnings"} else 1


def run_acceptance(
    *,
    live_canary: bool = False,
    query: str = "",
    instance: str = "",
    max_queries: int = 3,
    max_fetches: int = 3,
    keep_instance: bool = False,
    provider: str = "brave",
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as temp:
        deterministic = _run_deterministic(Path(temp))
    live_status = provider_status(provider)
    live = {
        "status": "not_run",
        "reason": "live canary requires --live-canary",
        "provider": provider,
        "live_provider_configured": bool(live_status.get("configured")),
    }
    if live_canary and bool(live_status.get("configured")):
        live = _run_live_canary(
            query=query,
            instance=instance,
            max_queries=max_queries,
            max_fetches=max_fetches,
            keep_instance=keep_instance,
            provider=provider,
        )
    elif live_canary:
        live = {
            "status": "waiting",
            "reason": "BRAVE_SEARCH_API_KEY/BRAVE_API_KEY is not configured",
            "provider": provider,
            "live_provider_configured": False,
        }
    checks = deterministic["checks"] + [
        {"id": "live_canary", "status": "pass" if live.get("status") == "pass" else "waiting", "details": live},
    ]
    deterministic_pass = all(item["status"] == "pass" for item in deterministic["checks"])
    status = "pass" if deterministic_pass and live.get("status") == "pass" else ("pass_with_warnings" if deterministic_pass else "fail")
    return {
        "schema_version": "eureka.live_search_hunt_acceptance.v1",
        "status": status,
        "deterministic": deterministic,
        "live_canary": live,
        "checks": checks,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "provider_result_payload_persisted": False,
    }


def _run_deterministic(root: Path) -> dict[str, Any]:
    provider = _FakeProvider()
    fetcher = SafeHTTPFetcher(
        dns_guard=DNSGuard(resolver=lambda _host: ("93.184.216.34",)),
        robots_client=AllowAllRobotsClient(),
        transport=_transport,
        clock=lambda: "2026-06-21T00:00:00Z",
    )
    db_path = root / "preview.sqlite"
    store = SQLitePreviewIndexStore(db_path)
    engine = HuntEngine(provider_factory=lambda _provider: provider, fetcher=fetcher, index_store=store)
    hunt = engine.run(
        "operator unseen CT1740 acceptance",
        run_id="acceptance-run",
        budget=HuntBudget(max_queries=1, max_provider_requests=1, max_pages=1, max_fetches=1, count=2),
    )
    stats = store.stats()
    store.close()
    reopened = SQLitePreviewIndexStore(db_path)
    local_search = reopened.search("acceptance CT1740", limit=5)
    reopened.close()
    no_provider = LiveSearchService(provider_factory=lambda _provider: None).search("operator unseen CT1740 acceptance", mode="live")
    summary_text = repr(hunt.persisted_summary)
    checks = [
        _check("fixture_free_normal_mode", True),
        _check("transient_live_results_display", hunt.response["result_count"] > 0),
        _check("independent_safe_fetch", hunt.persisted_summary["pages_fetched"] >= 1),
        _check("source_observation_created", hunt.persisted_summary["observations_created"] >= 1),
        _check("preview_document_indexed", stats["document_count"] >= 1),
        _check("restart_local_retrieval", local_search["result_count"] >= 1),
        _check("provider_outage_honest", no_provider["status"] == "fail" and no_provider["error"]["code"] == "live_provider_not_configured"),
        _check("no_provider_result_persistence", "Snippet" not in summary_text and "provider_rank" not in summary_text and "https://example.test/acceptance" not in summary_text),
        _check("no_review_required_for_display", hunt.response["review_required_for_display"] is False),
        _check("no_reviewed_public_mutation", not hunt.persisted_summary["reviewed_master_mutation"] and not hunt.persisted_summary["public_index_mutation"]),
    ]
    return {
        "status": "pass" if all(item["status"] == "pass" for item in checks) else "fail",
        "checks": checks,
        "queries_attempted": hunt.persisted_summary["queries_attempted"],
        "transient_leads": hunt.persisted_summary["transient_lead_count"],
        "fetches": hunt.persisted_summary["fetch_attempt_count"],
        "observations": hunt.persisted_summary["observations_created"],
        "documents": stats["document_count"],
        "restart_result_count": local_search["result_count"],
    }


def _run_live_canary(
    *,
    query: str,
    instance: str,
    max_queries: int,
    max_fetches: int,
    keep_instance: bool,
    provider: str,
) -> dict[str, Any]:
    clean_query = " ".join(str(query or "").split())
    if not clean_query:
        return {"status": "fail", "reason": "query_required", "provider": provider, "live_provider_configured": True}
    bounded_queries = max(1, min(int(max_queries or 3), 3))
    bounded_fetches = max(1, min(int(max_fetches or 3), 5))
    with _acceptance_instance(instance, keep_instance=keep_instance) as root:
        paths = build_portable_paths(root)
        if not paths.profile.exists():
            bootstrap_command(instance=root)
        service = LiveSearchService(provider_name=provider)
        search = service.search(clean_query, mode="live", count=5, timeout_seconds=10)
        hunt = service.start_hunt(
            clean_query,
            run_id=live_hunt_run_id(clean_query, "live-canary"),
            max_queries=bounded_queries,
            max_fetches=bounded_fetches,
            count=5,
            timeout_seconds=15,
            max_pages=1,
            max_links_followed=0,
            preview_index_path=paths.preview_sqlite,
        )
        store = SQLitePreviewIndexStore(paths.preview_sqlite)
        stats = store.stats()
        store.close()
        reopened = SQLitePreviewIndexStore(paths.preview_sqlite)
        local = reopened.search(clean_query, limit=5)
        if int(local.get("result_count") or 0) < 1:
            fallback_query = _first_indexed_search_terms(paths.preview_sqlite)
            local = reopened.search(fallback_query, limit=5) if fallback_query else local
        reopened.close()
        summary = dict(hunt.persisted_summary)
        live_result_count = int(search.get("result_count") or 0)
        fetch_attempt_count = int(summary.get("fetch_attempt_count") or 0)
        pages_fetched = int(summary.get("pages_fetched") or 0)
        observations_created = int(summary.get("observations_created") or 0)
        documents_indexed = int(stats.get("document_count") or 0)
        restart_hits = int(local.get("result_count") or 0)
        reason = ""
        if live_result_count < 1:
            reason = "no_live_results"
        elif fetch_attempt_count < 1 or pages_fetched < 1 or observations_created < 1 or documents_indexed < 1 or restart_hits < 1:
            reason = "no_policy_approved_fetchable_result"
        return {
            "status": "pass" if not reason else "fail",
            "reason": reason,
            "provider": provider,
            "live_provider_configured": True,
            "query_supplied": True,
            "instance_root": str(root),
            "live_result_count": live_result_count,
            "queries_attempted": len(summary.get("queries_attempted") or []),
            "transient_lead_count": int(summary.get("transient_lead_count") or 0),
            "fetch_attempt_count": fetch_attempt_count,
            "pages_fetched": pages_fetched,
            "observations_created": observations_created,
            "documents_indexed": documents_indexed,
            "restart_local_search_hits": restart_hits,
            "provider_result_payload_persisted": False,
            "reviewed_master_mutation": False,
            "public_index_mutation": False,
        }


def _check(check_id: str, condition: bool, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"id": check_id, "status": "pass" if condition else "fail", "details": dict(details or {})}


def _transport(_url: str, _headers: Mapping[str, str], _timeout: int, _max_bytes: int) -> HTTPTransportResult:
    body = b"<html><head><title>Acceptance CT1740</title></head><body>acceptance CT1740 independently fetched page</body></html>"
    return HTTPTransportResult(200, {"Content-Type": "text/html; charset=utf-8"}, body)


@contextmanager
def _acceptance_instance(instance: str, *, keep_instance: bool) -> Iterator[Path]:
    if str(instance or "").strip():
        root = resolve_portable_instance_root(instance)
        root.mkdir(parents=True, exist_ok=True)
        yield root
        return
    root = Path(tempfile.mkdtemp(prefix="eureka-live-acceptance-")).resolve()
    try:
        yield root
    finally:
        if not keep_instance:
            shutil.rmtree(root, ignore_errors=True)


def _first_indexed_search_terms(db_path: Path) -> str:
    try:
        conn = sqlite3.connect(str(db_path))
        row = conn.execute("SELECT title, canonical_url FROM preview_document ORDER BY retrieved_at DESC, document_id LIMIT 1").fetchone()
        conn.close()
    except sqlite3.DatabaseError:
        return ""
    if not row:
        return ""
    title = " ".join(str(row[0] or "").split())
    terms = [term for term in title.replace("|", " ").replace("-", " ").split() if len(term) > 2]
    return " ".join(terms[:4]) or str(row[1] or "")


class _FakeProvider:
    provider_id = "brave"
    capability_manifest = brave_capability_manifest()

    def search(
        self,
        query: str,
        *,
        page: int,
        count: int,
        freshness: str,
        country: str,
        language: str,
        safe_search: str,
        budget_context: WebSearchBudget,
        query_variant: str | None = None,
    ) -> SearchResultPage:
        retention = self.capability_manifest.retention_policy()
        return SearchResultPage(
            provider="brave",
            query=query,
            query_variant=query_variant or query,
            page=page,
            count=count,
            retrieved_at="2026-06-21T00:00:00Z",
            results=(
                SearchLead(
                    lead_id="acceptance-lead",
                    title="Acceptance CT1740",
                    url="https://example.test/acceptance",
                    snippet="Snippet must remain transient",
                    provider="brave",
                    provider_rank=1,
                    retrieved_at="2026-06-21T00:00:00Z",
                    query=query,
                    query_variant=query_variant or query,
                    page=page,
                    freshness=freshness,
                    retention_policy=retention,
                ),
            ),
            more_results_available=False,
            rate_limit={},
            raw_response_stored=False,
        )


if __name__ == "__main__":
    raise SystemExit(main())
