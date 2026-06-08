import io
import unittest
from unittest.mock import patch

from runtime.source.observation.internet_archive_live_transport import (
    IALiveTransport,
    IALiveTransportPolicy,
)


class FakeResponse:
    def __init__(self, body=b'{"ok": true}', status=200, headers=None):
        self._body = body
        self._status = status
        self.headers = headers or {"content-type": "application/json"}

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False

    def read(self):
        return self._body

    def getcode(self):
        return self._status


def policy(max_requests=2):
    return IALiveTransportPolicy(
        allowed_domains=("archive.org",),
        total_http_requests_max=max_requests,
        timeout_seconds_max=10,
        retry_attempts_max=1,
        honor_retry_after=True,
    )


class IALiveTransportTests(unittest.TestCase):
    def test_kill_switch_blocks_before_network(self):
        transport = IALiveTransport(policy())
        with patch("urllib.request.urlopen") as urlopen:
            with self.assertRaises(RuntimeError):
                transport.get_json(
                    url="https://archive.org/advancedsearch.php?q=sampleproject",
                    endpoint_class="metadata_search_small",
                    client_label="EurekaLocalPilot/0.1 (metadata-only; contact: local-operator)",
                    contact="local-operator",
                    timeout_seconds=10,
                    kill_switch_enabled=False,
                )
            urlopen.assert_not_called()

    def test_client_label_required(self):
        transport = IALiveTransport(policy())
        with self.assertRaises(RuntimeError):
            transport.get_json(
                url="https://archive.org/advancedsearch.php?q=sampleproject",
                endpoint_class="metadata_search_small",
                client_label="Python-urllib/3",
                contact="local-operator",
                timeout_seconds=10,
                kill_switch_enabled=True,
            )

    def test_domain_allowlist_enforced(self):
        transport = IALiveTransport(policy())
        with self.assertRaises(RuntimeError):
            transport.get_json(
                url="https://example.com/advancedsearch.php?q=sampleproject",
                endpoint_class="metadata_search_small",
                client_label="EurekaLocalPilot/0.1 (metadata-only; contact: local-operator)",
                contact="local-operator",
                timeout_seconds=10,
                kill_switch_enabled=True,
            )

    def test_request_cap_enforced(self):
        transport = IALiveTransport(policy(max_requests=1))
        with patch("urllib.request.urlopen", return_value=FakeResponse()):
            transport.get_json(
                url="https://archive.org/advancedsearch.php?q=sampleproject",
                endpoint_class="metadata_search_small",
                client_label="EurekaLocalPilot/0.1 (metadata-only; contact: local-operator)",
                contact="local-operator",
                timeout_seconds=10,
                kill_switch_enabled=True,
            )
            with self.assertRaises(RuntimeError):
                transport.get_json(
                    url="https://archive.org/metadata/sampleproject",
                    endpoint_class="item_metadata_read",
                    client_label="EurekaLocalPilot/0.1 (metadata-only; contact: local-operator)",
                    contact="local-operator",
                    timeout_seconds=10,
                    kill_switch_enabled=True,
                )

    def test_retry_after_is_reported(self):
        import urllib.error

        transport = IALiveTransport(policy())
        error = urllib.error.HTTPError(
            url="https://archive.org/advancedsearch.php?q=sampleproject",
            code=429,
            msg="Too Many Requests",
            hdrs={"Retry-After": "60"},
            fp=io.BytesIO(b'{"error": "rate limited"}'),
        )
        with patch("urllib.request.urlopen", side_effect=error):
            response = transport.get_json(
                url="https://archive.org/advancedsearch.php?q=sampleproject",
                endpoint_class="metadata_search_small",
                client_label="EurekaLocalPilot/0.1 (metadata-only; contact: local-operator)",
                contact="local-operator",
                timeout_seconds=10,
                kill_switch_enabled=True,
            )
        self.assertTrue(response.rate_limited)
        self.assertEqual(60, response.retry_after_seconds)

    def test_metadata_identifier_is_redacted_from_response_metadata_url(self):
        transport = IALiveTransport(policy())
        with patch("urllib.request.urlopen", return_value=FakeResponse()):
            response = transport.get_json(
                url="https://archive.org/metadata/sampleproject",
                endpoint_class="item_metadata_read",
                client_label="EurekaLocalPilot/0.1 (metadata-only; contact: local-operator)",
                contact="local-operator",
                timeout_seconds=10,
                kill_switch_enabled=True,
            )
        self.assertEqual(
            "https://archive.org/metadata/<redacted-identifier>?<redacted-query>",
            response.metadata()["url"],
        )

    def test_tls_failure_degrades_without_alternate_shell_path(self):
        import urllib.error

        transport = IALiveTransport(policy())
        error = urllib.error.URLError("certificate verify failed")
        with patch("urllib.request.urlopen", side_effect=error):
            response = transport.get_json(
                url="https://archive.org/advancedsearch.php?q=sampleproject",
                endpoint_class="metadata_search_small",
                client_label="EurekaLocalPilot/0.1 (metadata-only; contact: local-operator)",
                contact="local-operator",
                timeout_seconds=10,
                kill_switch_enabled=True,
            )
        self.assertEqual(0, response.status_code)
        self.assertEqual("ssl_certificate_verify_failed", response.transport_error)
        self.assertEqual("", response.body_text)


if __name__ == "__main__":
    unittest.main()
