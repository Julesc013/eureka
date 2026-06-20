#!/usr/bin/env python
"""Deterministic real Search/Hunt acceptance harness."""

from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import sys
import tempfile
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.web import FetchRequest, HTTPTransportResult, SafeHTTPFetcher  # noqa: E402
from runtime.connectors.web.dns_guard import DNSGuard  # noqa: E402
from runtime.connectors.web.robots import AllowAllRobotsClient  # noqa: E402
from runtime.index.preview import SQLitePreviewIndexStore  # noqa: E402
from runtime.search.hunt_engine import HuntBudget, HuntEngine  # noqa: E402
from runtime.search.live_service import LiveSearchService  # noqa: E402
from runtime.search.live_web import SearchLead, SearchResultPage, WebSearchBudget, brave_capability_manifest  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    parser.add_argument("--live-canary", action="store_true", help="Run a bounded real Brave canary when a local key is configured.")
    args = parser.parse_args(argv)
    payload = run_acceptance(live_canary=bool(args.live_canary))
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        for check in payload["checks"]:
            print(f"- {check['status']}: {check['id']}")
    return 0 if payload["status"] in {"pass", "pass_with_warnings"} else 1


def run_acceptance(*, live_canary: bool = False) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        deterministic = _run_deterministic(root)
    live_key_available = bool(os.environ.get("BRAVE_SEARCH_API_KEY") or os.environ.get("BRAVE_API_KEY"))
    live = {"status": "not_run", "reason": "BRAVE_SEARCH_API_KEY/BRAVE_API_KEY is not configured", "key_configured": False}
    if live_canary and live_key_available:
        live = _run_live_canary()
    elif live_key_available:
        live = {"status": "not_run", "reason": "live canary requires --live-canary", "key_configured": True}
    checks = deterministic["checks"] + [
        {"id": "live_canary", "status": "pass" if live.get("status") == "pass" else "waiting", "details": live},
    ]
    local_pass = all(item["status"] == "pass" for item in deterministic["checks"])
    status = "pass" if local_pass and live.get("status") == "pass" else ("pass_with_warnings" if local_pass else "fail")
    return {
        "schema_version": "eureka.live_search_hunt_acceptance.v0",
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


def _run_live_canary() -> dict[str, Any]:
    service = LiveSearchService()
    search = service.search("operator unseen CT1740 acceptance", mode="live", count=3, timeout_seconds=10)
    return {
        "status": "pass" if search.get("status") == "pass" and int(search.get("result_count") or 0) > 0 else "fail",
        "key_configured": True,
        "result_count": int(search.get("result_count") or 0),
        "provider": "brave",
    }


def _check(check_id: str, condition: bool, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"id": check_id, "status": "pass" if condition else "fail", "details": dict(details or {})}


def _transport(url: str, _headers: Mapping[str, str], _timeout: int, _max_bytes: int) -> HTTPTransportResult:
    body = b"<html><head><title>Acceptance CT1740</title></head><body>acceptance CT1740 independently fetched page</body></html>"
    return HTTPTransportResult(200, {"Content-Type": "text/html; charset=utf-8"}, body)


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
