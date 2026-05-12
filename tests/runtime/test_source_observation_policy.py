import unittest

from runtime.source_observation import (
    PolicyDecisionStatus,
    SourceId,
    SourceObservationValidationError,
    SourcePolicy,
    SourceRecord,
    evaluate_source_policy,
)


class SourceObservationPolicyTests(unittest.TestCase):
    def test_source_id_validates_stable_ids(self) -> None:
        self.assertEqual(str(SourceId("source.example.metadata")), "source.example.metadata")

    def test_invalid_source_id_fails(self) -> None:
        with self.assertRaises(SourceObservationValidationError):
            SourceId("Bad Source")

    def test_source_policy_blocks_forbidden_operation(self) -> None:
        record = SourceRecord(
            source_id=SourceId("source.example.metadata"),
            source_family="package_registry",
            trust_lane="synthetic",
            label="Synthetic metadata",
        )
        decision = evaluate_source_policy(record, "live_network_request")
        self.assertEqual(decision.status, PolicyDecisionStatus.BLOCKED)
        self.assertIn("blocked", decision.reason)

    def test_source_policy_allows_metadata_observation_when_configured(self) -> None:
        record = SourceRecord(
            source_id=SourceId("source.example.metadata"),
            source_family="package_registry",
            trust_lane="synthetic",
            label="Synthetic metadata",
        )
        policy = SourcePolicy(allowed_operations=("metadata_observation",))
        decision = evaluate_source_policy(record, "metadata_observation", {"policy": policy})
        self.assertEqual(decision.status, PolicyDecisionStatus.ALLOWED)
        self.assertEqual(decision.requested_operation, "metadata_observation")
        self.assertEqual(decision.source_id, "source.example.metadata")

    def test_policy_decision_has_explicit_status_and_reason(self) -> None:
        record = SourceRecord(
            source_id=SourceId("source.example.metadata"),
            source_family="package_registry",
            trust_lane="synthetic",
            label="Synthetic metadata",
        )
        decision = evaluate_source_policy(record, "unknown_operation")
        payload = decision.to_dict()
        self.assertEqual(payload["status"], "not_evaluable")
        self.assertTrue(payload["reason"])


if __name__ == "__main__":
    unittest.main()
