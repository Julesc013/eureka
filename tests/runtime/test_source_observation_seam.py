import json
import unittest

from scripts.demo_source_observation_seam import build_demo_result

from runtime.source_observation import (
    MetadataRequest,
    MetadataResponse,
    NormalizedObservation,
    ReviewStatus,
    SourceCapability,
    SourceId,
    SourceLocator,
    SourceRecord,
    build_evidence_candidate,
    build_review_item,
    build_source_observation,
    normalize_metadata_response,
)


class SourceObservationSeamTests(unittest.TestCase):
    def make_source_record(self) -> SourceRecord:
        return SourceRecord(
            source_id=SourceId("source.example.metadata"),
            source_family="package_registry",
            trust_lane="synthetic",
            label="Synthetic metadata",
            locators=(SourceLocator(kind="synthetic", value="package/demo"),),
            capabilities=(SourceCapability(name="metadata_observation", operations=("metadata_observation",)),),
            limitations=("synthetic payload only",),
        )

    def test_source_record_serializes_and_deserializes(self) -> None:
        record = self.make_source_record()
        self.assertEqual(SourceRecord.from_json(record.to_json()), record)
        payload = json.loads(record.to_json())
        self.assertEqual(payload["id"], "source.example.metadata")

    def test_metadata_request_serializes_and_deserializes(self) -> None:
        request = MetadataRequest.build(
            SourceId("source.example.metadata"),
            "package_metadata",
            "demo",
            created_at="2026-05-12T00:00:00Z",
        )
        self.assertEqual(MetadataRequest.from_json(request.to_json()), request)
        self.assertTrue(request.request_id.startswith("req_"))

    def test_metadata_response_fingerprints_explicit_payload(self) -> None:
        request = MetadataRequest.build(
            SourceId("source.example.metadata"),
            "package_metadata",
            "demo",
            created_at="2026-05-12T00:00:00Z",
        )
        response_a = MetadataResponse.build(request.request_id, request.source_id, "observed", {"name": "demo"})
        response_b = MetadataResponse.build(request.request_id, request.source_id, "observed", {"name": "demo"})
        self.assertEqual(response_a.fingerprint.value, response_b.fingerprint.value)
        self.assertTrue(response_a.response_id.startswith("res_"))

    def test_normalization_evidence_and_review_flow(self) -> None:
        record = self.make_source_record()
        request = MetadataRequest.build(
            record.source_id,
            "package_metadata",
            "demo",
            created_at="2026-05-12T00:00:00Z",
        )
        response = MetadataResponse.build(
            request.request_id,
            record.source_id,
            "observed",
            {"name": "demo", "version": "1.0.0"},
        )
        source_observation = build_source_observation(response, record, observed_fields={"name": "demo"})
        normalized = normalize_metadata_response(response, record)
        candidate = build_evidence_candidate(normalized)
        review_item = build_review_item(candidate)

        self.assertTrue(source_observation.observation_id.startswith("obs_"))
        self.assertIsInstance(normalized, NormalizedObservation)
        self.assertEqual(normalized.normalized_fields["name"], "demo")
        self.assertFalse(candidate.accepted)
        self.assertEqual(review_item.review_status, ReviewStatus.NEEDS_REVIEW)
        self.assertIsNone(review_item.decision)

    def test_demo_proves_flow_without_writes(self) -> None:
        result = build_demo_result()
        self.assertIn("source_observation", result)
        self.assertIn("normalized_observation", result)
        self.assertIn("evidence_candidate", result)
        self.assertIn("review_item", result)
        self.assertFalse(result["writes_enabled"]["durable_store"])
        self.assertFalse(result["writes_enabled"]["public_index"])


if __name__ == "__main__":
    unittest.main()
