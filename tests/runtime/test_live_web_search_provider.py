from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse
import unittest

from runtime.search.live_web import (
    BraveSearchProvider,
    HTTPTransportResult,
    MojeekSearchProvider,
    WebSearchBudget,
    WebSearchRateLimited,
    provider_from_environment,
)


class LiveWebSearchProviderTests(unittest.TestCase):
    def test_brave_adapter_normalizes_transient_leads_and_headers(self) -> None:
        captured: dict[str, object] = {}

        def transport(url: str, headers: object, timeout_seconds: int) -> HTTPTransportResult:
            captured["url"] = url
            captured["headers"] = dict(headers)  # type: ignore[arg-type]
            captured["timeout_seconds"] = timeout_seconds
            return HTTPTransportResult(
                status_code=200,
                headers={
                    "X-RateLimit-Limit": "1, 15000",
                    "X-RateLimit-Remaining": "0, 14999",
                    "X-RateLimit-Reset": "1, 1000",
                },
                body=json.dumps(
                    {
                        "query": {"original": "manual", "more_results_available": True},
                        "web": {
                            "results": [
                                {
                                    "title": "<b>Sound Blaster CT1740 Manual</b>",
                                    "url": "https://example.test/manual",
                                    "description": "A setup manual.",
                                }
                            ]
                        },
                    }
                ).encode("utf-8"),
            )

        provider = BraveSearchProvider("secret-token", transport=transport, clock=lambda: "2026-06-20T00:00:00Z")
        page = provider.search(
            "manual",
            page=2,
            count=5,
            freshness="py",
            country="us",
            language="en",
            safe_search="strict",
            budget_context=WebSearchBudget(timeout_seconds=7, max_retries=0),
        )

        parsed = urlparse(str(captured["url"]))
        params = parse_qs(parsed.query)
        self.assertEqual("https", parsed.scheme)
        self.assertEqual(["manual"], params["q"])
        self.assertEqual(["5"], params["count"])
        self.assertEqual(["2"], params["offset"])
        self.assertEqual(["py"], params["freshness"])
        self.assertEqual("secret-token", dict(captured["headers"])["X-Subscription-Token"])
        self.assertEqual(7, captured["timeout_seconds"])
        self.assertTrue(page.more_results_available)
        self.assertEqual("Sound Blaster CT1740 Manual", page.results[0].title)
        self.assertEqual("LIVE - UNREVIEWED", page.results[0].to_dict()["state"])
        policy = page.results[0].retention_policy
        self.assertTrue(policy.display_results)
        self.assertFalse(policy.persist_snippets)
        self.assertFalse(policy.persist_rank)
        self.assertFalse(policy.redistribute)
        self.assertIn("X-RateLimit-Remaining", page.rate_limit)

    def test_provider_from_environment_accepts_alias_without_exposing_key(self) -> None:
        self.assertIsNone(provider_from_environment(env={}))
        provider = provider_from_environment(env={"BRAVE_API_KEY": "alias-token"}, transport=lambda _u, _h, _t: HTTPTransportResult(200, {}, b"{}"))
        self.assertIsInstance(provider, BraveSearchProvider)
        self.assertIsNone(provider_from_environment(env={"BRAVE_SEARCH_API_KEY": "PASTE_REAL_BRAVE_KEY_HERE"}))

    def test_mojeek_adapter_normalizes_transient_leads(self) -> None:
        captured: dict[str, object] = {}

        def transport(url: str, headers: object, timeout_seconds: int) -> HTTPTransportResult:
            captured["url"] = url
            captured["headers"] = dict(headers)  # type: ignore[arg-type]
            captured["timeout_seconds"] = timeout_seconds
            return HTTPTransportResult(
                status_code=200,
                headers={},
                body=json.dumps(
                    {
                        "response": {
                            "status": "OK",
                            "head": {"results": "2", "return": "1", "start": "1"},
                            "results": [
                                {
                                    "url": "https://example.test/mojeek-manual",
                                    "title": "<b>Mojeek Manual Result</b>",
                                    "desc": "Mojeek transient snippet.",
                                }
                            ],
                        }
                    }
                ).encode("utf-8"),
            )

        provider = MojeekSearchProvider("mojeek-token", transport=transport, clock=lambda: "2026-06-21T00:00:00Z")
        page = provider.search(
            "manual",
            page=0,
            count=1,
            freshness="year",
            country="us",
            language="en",
            safe_search="moderate",
            budget_context=WebSearchBudget(timeout_seconds=6, max_retries=0),
        )

        parsed = urlparse(str(captured["url"]))
        params = parse_qs(parsed.query)
        self.assertEqual("https", parsed.scheme)
        self.assertEqual(["manual"], params["q"])
        self.assertEqual(["json"], params["fmt"])
        self.assertEqual(["mojeek-token"], params["api_key"])
        self.assertEqual("application/json", dict(captured["headers"])["Accept"])
        self.assertEqual(6, captured["timeout_seconds"])
        self.assertEqual(1, len(page.results))
        self.assertEqual("Mojeek Manual Result", page.results[0].title)
        self.assertEqual("LIVE - UNREVIEWED", page.results[0].to_dict()["state"])
        self.assertFalse(page.results[0].retention_policy.persist_snippets)
        self.assertFalse(page.raw_response_stored)

    def test_rate_limit_raises_with_headers(self) -> None:
        def transport(_url: str, _headers: object, _timeout_seconds: int) -> HTTPTransportResult:
            return HTTPTransportResult(
                status_code=429,
                headers={"X-RateLimit-Reset": "1", "X-RateLimit-Remaining": "0, 14999"},
                body=b"{}",
            )

        provider = BraveSearchProvider("secret-token", transport=transport)
        with self.assertRaises(WebSearchRateLimited) as raised:
            provider.search(
                "manual",
                page=0,
                count=5,
                freshness="",
                country="",
                language="",
                safe_search="moderate",
                budget_context=WebSearchBudget(max_retries=0),
            )

        self.assertEqual(429, raised.exception.status_code)
        self.assertEqual("0, 14999", raised.exception.rate_limit["X-RateLimit-Remaining"])


if __name__ == "__main__":
    unittest.main()
