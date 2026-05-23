import json
import unittest

from runtime.source.observation.internet_archive_live_probe import (
    load_live_probe_policy,
    run_live_metadata_probe,
)
from runtime.source.observation.internet_archive_live_transport import IALiveTransportResponse


class FakeTransport:
    def __init__(self, _policy):
        self.request_count = 0

    def get_json(self, **kwargs):
        self.request_count += 1
        if not kwargs.get("kill_switch_enabled"):
            raise RuntimeError("kill switch disabled")
        endpoint = kwargs["endpoint_class"]
        if endpoint == "metadata_search_small":
            body = {
                "response": {
                    "docs": [
                        {
                            "identifier": "sampleproject",
                            "title": "Sample Project",
                            "mediatype": "texts",
                            "collection": ["opensource"],
                        }
                    ]
                }
            }
        else:
            body = {
                "metadata": {
                    "identifier": "sampleproject",
                    "title": "Sample Project",
                    "mediatype": "texts",
                    "collection": ["opensource"],
                },
                "files": [{"name": "sampleproject_meta.xml", "format": "Metadata", "size": "10"}],
            }
        encoded = json.dumps(body)
        return IALiveTransportResponse(
            url=kwargs["url"],
            endpoint_class=endpoint,
            status_code=200,
            elapsed_ms=1,
            response_byte_count=len(encoded),
            content_sha256="0" * 64,
            safe_headers={"content-type": "application/json"},
            body_text=encoded,
        )


class RateLimitedTransport:
    def __init__(self, _policy):
        self.request_count = 0

    def get_json(self, **kwargs):
        self.request_count += 1
        return IALiveTransportResponse(
            url=kwargs["url"],
            endpoint_class=kwargs["endpoint_class"],
            status_code=429,
            elapsed_ms=1,
            response_byte_count=2,
            content_sha256="1" * 64,
            safe_headers={"retry-after": "60"},
            body_text="{}",
            rate_limited=True,
            retry_after_seconds=60,
        )


class IALiveMetadataProbeTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_live_probe_policy()

    def test_approve_live_required_for_network_mode(self):
        with self.assertRaises(RuntimeError):
            run_live_metadata_probe(self.policy, approve_live=False, dry_run=False)

    def test_dry_run_performs_no_network(self):
        def forbidden_factory(_policy):
            raise AssertionError("dry-run must not create transport")

        report = run_live_metadata_probe(self.policy, dry_run=True, transport_factory=forbidden_factory)
        self.assertTrue(report["dry_run"])
        self.assertEqual(0, report["redacted_summary"]["total_http_requests"])
        self.assertFalse(report["boundary_report"]["live_source_call_performed"])

    def test_policy_caps_are_enforced(self):
        with self.assertRaises(ValueError):
            run_live_metadata_probe(self.policy, approve_live=True, rows=2, transport_factory=FakeTransport)
        with self.assertRaises(ValueError):
            run_live_metadata_probe(self.policy, approve_live=True, max_requests=3, transport_factory=FakeTransport)

    def test_live_probe_generates_redacted_preview_only(self):
        report = run_live_metadata_probe(
            self.policy,
            approve_live=True,
            client_label="EurekaLocalPilot/0.1 (metadata-only; contact: local-operator)",
            contact="local-operator",
            transport_factory=FakeTransport,
        )
        summary = report["redacted_summary"]
        boundary = report["boundary_report"]
        self.assertEqual("succeeded", summary["probe_status"])
        self.assertEqual(2, summary["total_http_requests"])
        self.assertEqual(
            "https://archive.org/metadata/<redacted-identifier>?<redacted-query>",
            summary["http_responses"][1]["url"],
        )
        self.assertEqual(
            "https://archive.org/metadata/<redacted-identifier>?<redacted-query>",
            report["request_plan"][1]["url"],
        )
        self.assertEqual(2, len(report["normalized_preview"]))
        for record in report["normalized_preview"]:
            self.assertNotIn("item_identifier", record)
            self.assertTrue(record["review_required"])
            self.assertFalse(record["accepted_truth"])
            self.assertFalse(record["source_cache_write_performed"])
            self.assertFalse(record["evidence_ledger_write_performed"])
            self.assertFalse(record["index_mutation_performed"])
        self.assertTrue(boundary["live_source_call_performed"])
        self.assertTrue(boundary["source_probe_executed"])
        self.assertFalse(boundary["download_performed"])
        self.assertFalse(boundary["source_cache_write_performed"])

    def test_rate_limit_becomes_backoff_preview(self):
        report = run_live_metadata_probe(
            self.policy,
            approve_live=True,
            client_label="EurekaLocalPilot/0.1 (metadata-only; contact: local-operator)",
            contact="local-operator",
            transport_factory=RateLimitedTransport,
        )
        self.assertEqual("rate_limited", report["redacted_summary"]["probe_status"])
        self.assertEqual(1, report["redacted_summary"]["total_http_requests"])
        self.assertEqual("retry_after", report["normalized_preview"][0]["observation_kind"])


if __name__ == "__main__":
    unittest.main()
