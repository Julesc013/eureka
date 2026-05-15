"""Deterministic local evaluation suites."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


OVERLONG_QUERY = "x" * 300
DEFAULT_QUERY_SUITE = (
    "sampleproject",
    "definitely-not-present-local-10",
    "visual studio 2008 express",
    "old printer driver windows xp",
    "mac os 9 utility",
    "query with <unsafe> chars",
    OVERLONG_QUERY,
)


@dataclass(frozen=True)
class LocalEvalCase:
    case_id: str
    method: str
    path: str
    params: Mapping[str, str] | None = None
    body: Mapping[str, str] | None = None
    expect_statuses: tuple[int, ...] = (200,)
    expect_content: str = ""
    markers: tuple[str, ...] = ()
    absent_markers: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class LocalEvalSuite:
    name: str
    cases: tuple[LocalEvalCase, ...]
    purpose: str


def get_default_local_eval_suites() -> tuple[LocalEvalSuite, ...]:
    return (
        LocalEvalSuite(
            name="service_health",
            purpose="loopback route health",
            cases=(
                LocalEvalCase("home", "GET", "/", expect_content="html", markers=("Eureka Local Appliance",)),
                LocalEvalCase("status_html", "GET", "/status", expect_content="html", markers=("Status", "Store status")),
                LocalEvalCase("health", "GET", "/health", expect_content="json", markers=("schema_version",)),
                LocalEvalCase("status_json", "GET", "/api/v1/status", expect_content="json", markers=("service",)),
                LocalEvalCase("health_json", "GET", "/api/v1/health", expect_content="json", markers=("localhost_only",)),
            ),
        ),
        LocalEvalSuite(
            name="json_search",
            purpose="fixed local reviewed-index JSON searches",
            cases=(
                LocalEvalCase("sample", "GET", "/api/v1/search", {"q": "sampleproject"}, expect_content="json", markers=("results",)),
                LocalEvalCase(
                    "missing",
                    "GET",
                    "/api/v1/search",
                    {"q": "definitely-not-present-local-10"},
                    expect_content="json",
                    markers=("result_count",),
                ),
                LocalEvalCase("empty", "GET", "/api/v1/search", {"q": "   "}, expect_content="json", markers=("warnings",)),
                LocalEvalCase("overlong", "GET", "/api/v1/search", {"q": OVERLONG_QUERY}, expect_statuses=(200, 400, 405), markers=("query", "error")),
                LocalEvalCase("special", "GET", "/api/v1/search", {"q": "query with <unsafe> chars"}, expect_content="json", markers=("query",)),
            ),
        ),
        LocalEvalSuite(
            name="html_workbench",
            purpose="server-rendered workbench availability",
            cases=(
                LocalEvalCase("home", "GET", "/", expect_content="html", markers=("Local appliance prototype",)),
                LocalEvalCase("status", "GET", "/status", expect_content="html", markers=("Runtime and non-claim flags",)),
                LocalEvalCase("search", "GET", "/search", {"q": "sampleproject"}, expect_content="html", markers=("Submitted query",)),
                LocalEvalCase("absence", "GET", "/absence", {"q": "definitely-not-present-local-10"}, expect_content="html", markers=("Checked local layers",)),
                LocalEvalCase("object_missing", "GET", "/object/nonexistent-local-10", expect_statuses=(200, 404), expect_content="html", markers=("Object not found",)),
                LocalEvalCase("source_missing", "GET", "/source/nonexistent-local-10", expect_content="html", markers=("Source coverage shown here is local",)),
            ),
        ),
        LocalEvalSuite(
            name="absence",
            purpose="local current-index absence semantics",
            cases=(
                LocalEvalCase(
                    "absence_json",
                    "GET",
                    "/api/v1/absence",
                    {"q": "definitely-not-present-local-10"},
                    expect_content="json",
                    markers=("absence", "limitations"),
                ),
                LocalEvalCase(
                    "absence_html",
                    "GET",
                    "/absence",
                    {"q": "definitely-not-present-local-10"},
                    expect_content="html",
                    markers=("local current-index absence only", "Unchecked and deferred layers"),
                ),
            ),
        ),
        LocalEvalSuite(
            name="read_only_safety",
            purpose="mutation rejection and local-only safety",
            cases=(
                LocalEvalCase("post_search", "POST", "/api/v1/search", expect_statuses=(400, 401, 403, 404, 405)),
                LocalEvalCase("put_search", "PUT", "/api/v1/search", expect_statuses=(400, 401, 403, 404, 405)),
                LocalEvalCase("patch_search", "PATCH", "/api/v1/search", expect_statuses=(400, 401, 403, 404, 405)),
                LocalEvalCase("delete_search", "DELETE", "/api/v1/search", expect_statuses=(400, 401, 403, 404, 405)),
                LocalEvalCase("review_without_token", "POST", "/review/nonexistent-local-10/decision", expect_statuses=(400, 401, 403, 404, 405)),
                LocalEvalCase("rebuild_without_token", "POST", "/rebuild", expect_statuses=(400, 401, 403, 404, 405)),
                LocalEvalCase("probe_absent", "GET", "/api/v1/source-probe", expect_statuses=(400, 404)),
                LocalEvalCase("download_absent", "GET", "/api/v1/download", expect_statuses=(404,)),
            ),
        ),
        LocalEvalSuite(
            name="worker_queue_safety",
            purpose="deterministic worker registry safety",
            cases=(
                LocalEvalCase("worker_registry", "INPROC", "worker_registry"),
                LocalEvalCase("status_no_execution", "GET", "/api/v1/status", expect_content="json", markers=("workunit_execution_enabled",)),
            ),
        ),
        LocalEvalSuite(
            name="latency_smoke",
            purpose="bounded route timing",
            cases=(
                LocalEvalCase("status", "GET", "/api/v1/status", expect_content="json"),
                LocalEvalCase("search", "GET", "/api/v1/search", {"q": "sampleproject"}, expect_content="json"),
                LocalEvalCase("absence", "GET", "/api/v1/absence", {"q": "definitely-not-present-local-10"}, expect_content="json"),
            ),
        ),
        LocalEvalSuite(
            name="local_state_cleanliness",
            purpose="explicit local-state boundary posture",
            cases=(
                LocalEvalCase("status_flags", "GET", "/api/v1/status", expect_content="json", markers=("deployment_performed", "lan_enabled")),
            ),
        ),
    )


def get_default_query_suite() -> tuple[str, ...]:
    return DEFAULT_QUERY_SUITE
