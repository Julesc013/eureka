from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse
import unittest

from runtime.source.observation.archive_org_public_metadata import ArchiveOrgMetadataCandidateProvider
from runtime.source.observation.internet_archive_live_transport import IALiveTransportResponse


class RecordingTransport:
    instances: list["RecordingTransport"] = []

    def __init__(self, _policy) -> None:
        self.urls: list[str] = []
        RecordingTransport.instances.append(self)

    def get_json(self, **kwargs):
        self.urls.append(kwargs["url"])
        payload = {
            "response": {
                "docs": [
                    {
                        "identifier": "windows_7_iso_fixture",
                        "title": "Windows 7 ISO install media",
                        "mediatype": "software",
                        "description": "Operating system image fixture",
                    },
                    {
                        "identifier": "portable_utility_fixture",
                        "title": "Windows 7 Portable Utility Pack",
                        "mediatype": "software",
                        "description": "Portable checksum and text utilities.",
                    },
                ]
            }
        }
        encoded = json.dumps(payload)
        return IALiveTransportResponse(
            url=kwargs["url"],
            endpoint_class=kwargs["endpoint_class"],
            status_code=200,
            elapsed_ms=1,
            response_byte_count=len(encoded),
            content_sha256="0" * 64,
            safe_headers={"content-type": "application/json"},
            body_text=encoded,
        )


class ArchiveOrgCandidatePlanningTests(unittest.TestCase):
    def setUp(self) -> None:
        RecordingTransport.instances = []

    def test_provider_uses_query_plan_rewrite_and_suppresses_candidates(self) -> None:
        provider = ArchiveOrgMetadataCandidateProvider(rows=5, transport_factory=RecordingTransport)

        result = provider.search_metadata_candidates(
            "Windows 7-compatible portable utilities, not Windows 7 ISO",
            limit=5,
        )

        self.assertEqual("succeeded", result["status"])
        self.assertEqual(1, result["candidate_count"])
        self.assertEqual(1, result["suppressed_candidate_count"])
        self.assertEqual(
            ["suppress_os_images_for_software_queries"],
            result["candidate_suppressions_applied"],
        )
        self.assertEqual("find_software", result["query_plan"]["intent"])
        self.assertEqual("legacy_software", result["query_plan"]["domain_pack"])
        url_query = parse_qs(urlparse(RecordingTransport.instances[0].urls[0]).query)
        source_query = url_query["q"][0]
        self.assertIn("portable", source_query.casefold())
        self.assertIn("-iso", source_query.casefold())

    def test_candidates_carry_plan_ref_but_not_truth(self) -> None:
        provider = ArchiveOrgMetadataCandidateProvider(rows=5, transport_factory=RecordingTransport)

        result = provider.search_metadata_candidates("Windows 7-compatible portable utilities, not Windows 7 ISO")

        candidate = result["candidates"][0]
        self.assertEqual(result["query_plan"]["plan_id"], candidate["query_plan_ref"])
        self.assertEqual("find_software", candidate["query_intent"])
        self.assertFalse(candidate["accepted_truth"])
        self.assertTrue(candidate["review_required"])
        self.assertFalse(candidate["download_performed"])
        self.assertFalse(candidate["extraction_executed"])


if __name__ == "__main__":
    unittest.main()
