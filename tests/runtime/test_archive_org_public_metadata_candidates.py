from __future__ import annotations

import urllib.parse
import unittest

from runtime.source.observation.archive_org_public_metadata import (
    ArchiveOrgMetadataCandidateProvider,
    build_archive_org_metadata_search_url,
)
from runtime.source.observation.internet_archive_live_transport import (
    IALiveTransportPolicy,
    IALiveTransportResponse,
)


class ArchiveOrgPublicMetadataCandidateTest(unittest.TestCase):
    def test_builds_advancedsearch_metadata_url_with_bounded_rows(self) -> None:
        url = build_archive_org_metadata_search_url("windows 7 utilities", 99)
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)

        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "archive.org")
        self.assertEqual(parsed.path, "/advancedsearch.php")
        self.assertEqual(params["q"], ["windows 7 utilities"])
        self.assertEqual(params["rows"], ["10"])
        self.assertEqual(params["output"], ["json"])
        self.assertIn("identifier", params["fl[]"])
        self.assertIn("title", params["fl[]"])
        self.assertIn("description", params["fl[]"])

    def test_search_returns_review_only_candidates_without_payload_actions(self) -> None:
        calls: list[str] = []

        def factory(policy: IALiveTransportPolicy) -> FakeTransport:
            self.assertEqual(policy.allowed_domains, ("archive.org",))
            self.assertEqual(policy.total_http_requests_max, 1)
            return FakeTransport(calls)

        provider = ArchiveOrgMetadataCandidateProvider(rows=3, transport_factory=factory)
        result = provider.search_metadata_candidates("audacity portable", limit=2)

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(result["total_http_requests"], 1)
        self.assertTrue(result["live_call_performed"])
        self.assertTrue(result["metadata_request_performed"])
        self.assertFalse(result["source_probe_executed"])
        self.assertFalse(result["download_performed"])
        self.assertFalse(result["upload_performed"])
        self.assertFalse(result["extraction_executed"])
        self.assertFalse(result["raw_response_committed"])
        self.assertFalse(result["accepted_truth"])
        self.assertTrue(result["review_required"])
        self.assertEqual(len(calls), 1)

        candidate = result["candidates"][0]
        self.assertEqual(candidate["candidate_status"], "needs_review")
        self.assertEqual(candidate["identifier"], "audacity_portable_fixture")
        self.assertTrue(candidate["source_locator"]["url"].startswith("https://archive.org/details/"))
        self.assertFalse(candidate["download_performed"])
        self.assertFalse(candidate["accepted_truth"])

        cached = provider.search_metadata_candidates("audacity portable", limit=2)
        self.assertTrue(cached["cache_hit"])
        self.assertEqual(cached["total_http_requests"], 0)
        self.assertFalse(cached["live_call_performed"])
        self.assertFalse(cached["metadata_request_performed"])
        self.assertEqual(len(calls), 1)


class FakeTransport:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def get_json(self, **kwargs: object) -> IALiveTransportResponse:
        url = str(kwargs["url"])
        self.calls.append(url)
        return IALiveTransportResponse(
            url=url,
            endpoint_class=str(kwargs["endpoint_class"]),
            status_code=200,
            elapsed_ms=7,
            response_byte_count=240,
            content_sha256="0" * 64,
            safe_headers={"content-type": "application/json"},
            body_text=(
                '{"response":{"numFound":1,"docs":[{"identifier":"audacity_portable_fixture",'
                '"title":"Audacity portable fixture","mediatype":"software",'
                '"collection":["open_source_software"],"creator":"fixture",'
                '"description":"Portable audio editor metadata candidate."}]}}'
            ),
        )


if __name__ == "__main__":
    unittest.main()
