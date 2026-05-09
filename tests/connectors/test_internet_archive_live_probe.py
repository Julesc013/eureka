import copy
import json
import re
import unittest
from pathlib import Path
from unittest import mock

from runtime.connectors.internet_archive.live_metadata_probe import (
    LiveProbeBlocked,
    build_live_probe_result,
    build_metadata_url,
    build_review_queue_seed_preview,
    detect_live_probe_product_boundary_violations,
    detect_live_probe_truth_boundary_violations,
    fetch_ia_metadata_once,
    load_policy_bundle,
    map_live_probe_to_source_cache_candidate,
    normalize_live_probe_result,
    preview_live_probe_evidence_candidates,
    validate_identifier_allowed,
    validate_live_probe_policy,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME = REPO_ROOT / "runtime/connectors/internet_archive/live_metadata_probe.py"
IDENTIFIER = "eureka-software-fixture"


class FakeResponse:
    status = 200
    headers = {"Content-Type": "application/json"}

    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload

    def geturl(self):
        return f"https://archive.org/metadata/{IDENTIFIER}"


def approved_bundle():
    bundle = copy.deepcopy(load_policy_bundle(REPO_ROOT))
    bundle["source_policy"]["live_access_approved"] = True
    bundle["source_policy"]["metadata_probe_approved"] = True
    bundle["endpoint_policy"]["current_allowed_endpoint_behavior"] = "approved_metadata_read_only"
    bundle["endpoint_policy"]["current_network_calls_allowed"] = True
    bundle["rate_limit_policy"]["proposed_user_agent"] = "EurekaTest/0.0 (metadata probe test)"
    bundle["rate_limit_policy"]["contact_email"] = "approved-omitted-by-test@example.invalid"
    bundle["rate_limit_policy"]["timeout_seconds"] = 5
    bundle["rate_limit_policy"]["max_requests_per_minute"] = 1
    bundle["rate_limit_policy"]["retry_policy"] = "no_retry"
    bundle["cache_policy"]["cache_ttl"] = "no_cache_for_test"
    bundle["kill_switch_policy"]["default_enabled"] = True
    bundle["live_probe_policy"]["live_probe_enabled"] = True
    bundle["live_probe_policy"]["approval_status"] = "approved"
    bundle["allowed_identifier_policy"]["approval_status"] = "approved"
    bundle["allowed_identifier_policy"]["approved_identifiers"] = [IDENTIFIER]
    return bundle


def metadata_payload():
    return {
        "metadata": {
            "identifier": IDENTIFIER,
            "title": "Eureka Software Fixture",
            "description": "Mocked IA metadata response.",
            "mediatype": "software",
            "collection": ["opensource"],
            "creator": ["Eureka Fixture Maintainers"],
            "date": "1999",
            "publicdate": "2026-01-01 00:00:00",
        },
        "files": [
            {"name": "README.txt", "format": "Text", "size": "128"},
        ],
    }


class InternetArchiveLiveProbeTest(unittest.TestCase):
    def test_policy_pending_blocks_live_call(self):
        bundle = load_policy_bundle(REPO_ROOT)
        self.assertFalse(validate_live_probe_policy(bundle)["approved"])
        with mock.patch("runtime.connectors.internet_archive.live_metadata_probe.urllib.request.urlopen") as urlopen:
            with self.assertRaises(LiveProbeBlocked):
                fetch_ia_metadata_once(IDENTIFIER, bundle)
            urlopen.assert_not_called()

    def test_identifier_not_in_allowlist_blocks_live_call(self):
        bundle = approved_bundle()
        result = validate_identifier_allowed("not-approved", bundle["allowed_identifier_policy"])
        self.assertFalse(result["approved"])

    def test_approved_identifier_preflight_passes(self):
        bundle = approved_bundle()
        self.assertTrue(validate_live_probe_policy(bundle)["approved"])
        self.assertTrue(validate_identifier_allowed(IDENTIFIER, bundle["allowed_identifier_policy"])["approved"])

    def test_url_builder_only_builds_metadata_endpoint(self):
        self.assertEqual(build_metadata_url(IDENTIFIER), f"https://archive.org/metadata/{IDENTIFIER}")
        self.assertNotIn("advancedsearch", build_metadata_url(IDENTIFIER))
        with self.assertRaises(ValueError):
            build_metadata_url("https://archive.org/details/nope")

    def test_forbidden_endpoint_action_is_rejected(self):
        bundle = approved_bundle()
        bundle["live_probe_policy"]["allowed_endpoint_templates"] = ["https://archive.org/advancedsearch.php"]
        self.assertFalse(validate_live_probe_policy(bundle)["approved"])

    def test_mocked_metadata_response_builds_live_probe_result(self):
        bundle = approved_bundle()
        with mock.patch(
            "runtime.connectors.internet_archive.live_metadata_probe.urllib.request.urlopen",
            return_value=FakeResponse(metadata_payload()),
        ) as urlopen:
            payload, metadata = fetch_ia_metadata_once(IDENTIFIER, bundle)
        urlopen.assert_called_once()
        result = build_live_probe_result(IDENTIFIER, payload, metadata, bundle)
        self.assertEqual(result["request_count"], 1)
        self.assertTrue(result["network_used"])
        self.assertFalse(result["truth_boundary"]["live_probe_result_is_truth"])

    def test_mocked_response_normalizes_through_foundation_normalizer(self):
        bundle = approved_bundle()
        result = build_live_probe_result(
            IDENTIFIER,
            metadata_payload(),
            {"status": 200, "final_url": build_metadata_url(IDENTIFIER), "response_sha256": "mock"},
            bundle,
        )
        normalized = normalize_live_probe_result(result, bundle["normalization_policy"])
        self.assertEqual(normalized["item_identifier"], IDENTIFIER)
        self.assertEqual(normalized["source_observation_origin"], "ia_bundle_02_live_probe")

    def test_source_cache_candidate_preview_is_not_accepted_source_truth(self):
        bundle = approved_bundle()
        result = build_live_probe_result(IDENTIFIER, metadata_payload(), {"status": 200, "final_url": build_metadata_url(IDENTIFIER)}, bundle)
        normalized = normalize_live_probe_result(result, bundle["normalization_policy"])
        candidate = map_live_probe_to_source_cache_candidate(normalized, bundle["source_cache_mapping_policy"])
        self.assertFalse(candidate["accepted_source_truth"])
        self.assertFalse(candidate["source_cache_runtime_mutated"])

    def test_evidence_candidate_preview_is_not_accepted_evidence(self):
        bundle = approved_bundle()
        result = build_live_probe_result(IDENTIFIER, metadata_payload(), {"status": 200, "final_url": build_metadata_url(IDENTIFIER)}, bundle)
        normalized = normalize_live_probe_result(result, bundle["normalization_policy"])
        preview = preview_live_probe_evidence_candidates(normalized, bundle["evidence_mapping_policy"])
        self.assertFalse(preview["accepted_evidence"])
        self.assertFalse(preview["evidence_ledger_runtime_mutated"])

    def test_review_queue_seed_is_not_a_review_decision(self):
        bundle = approved_bundle()
        result = build_live_probe_result(IDENTIFIER, metadata_payload(), {"status": 200, "final_url": build_metadata_url(IDENTIFIER)}, bundle)
        normalized = normalize_live_probe_result(result, bundle["normalization_policy"])
        candidate = map_live_probe_to_source_cache_candidate(normalized, bundle["source_cache_mapping_policy"])
        evidence = preview_live_probe_evidence_candidates(normalized, bundle["evidence_mapping_policy"])
        seed = build_review_queue_seed_preview(result, candidate, evidence, bundle["review_policy"])
        self.assertFalse(seed["review_seed_is_review_decision"])
        self.assertFalse(seed["review_queue_runtime_mutated"])

    def test_file_download_attempt_is_rejected(self):
        result = build_live_probe_result(IDENTIFIER, metadata_payload(), {"status": 200}, approved_bundle())
        result["product_boundary"]["enabled_downloads"] = True
        self.assertTrue(detect_live_probe_product_boundary_violations(result, None))

    def test_public_index_mutation_claim_is_rejected(self):
        result = build_live_probe_result(IDENTIFIER, metadata_payload(), {"status": 200}, approved_bundle())
        result["truth_boundary"]["public_index_mutated"] = True
        self.assertTrue(detect_live_probe_truth_boundary_violations(result, None))

    def test_master_index_mutation_claim_is_rejected(self):
        result = build_live_probe_result(IDENTIFIER, metadata_payload(), {"status": 200}, approved_bundle())
        result["truth_boundary"]["master_index_mutated"] = True
        self.assertTrue(detect_live_probe_truth_boundary_violations(result, None))

    def test_rights_malware_installability_claims_are_rejected(self):
        for key in ("rights_clearance_claimed", "malware_safety_claimed", "verified_installability_claimed"):
            with self.subTest(key=key):
                result = build_live_probe_result(IDENTIFIER, metadata_payload(), {"status": 200}, approved_bundle())
                result["truth_boundary"][key] = True
                self.assertTrue(detect_live_probe_truth_boundary_violations(result, None))

    def test_runtime_does_not_call_model_provider(self):
        text = RUNTIME.read_text(encoding="utf-8")
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))


if __name__ == "__main__":
    unittest.main()
