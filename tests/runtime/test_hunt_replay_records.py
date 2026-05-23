from __future__ import annotations

import unittest

from runtime.search.hunt import (
    BLOCKED_REPLAY_STEP_KINDS,
    ENABLED_REPLAY_STEP_KINDS,
    HuntReplayDiff,
    HuntReplayFixture,
    HuntReplayMode,
    HuntReplayRecord,
    HuntReplayResult,
    HuntReplayStep,
    validate_replay_fixture,
    validate_replay_result,
)


class HuntReplayRecordTests(unittest.TestCase):
    def test_replay_record_validates_required_fields_and_boundaries(self) -> None:
        fixture = HuntReplayFixture(
            replay_source="local_hunt_record",
            hunt_id="shs_test",
            query="sampleproject",
            instance_schema_version="1",
            index_snapshot_id="local-current",
            expected_steps=tuple(HuntReplayStep.new(kind) for kind in ENABLED_REPLAY_STEP_KINDS),
            blocked_steps=tuple(HuntReplayStep.new(kind, "blocked") for kind in BLOCKED_REPLAY_STEP_KINDS),
            expected_outputs={"hunt_created": True},
        )
        validate_replay_fixture(fixture)
        diff = HuntReplayDiff(
            status="matched",
            matched=True,
            differences=(),
            expected_summary=fixture.expected_outputs,
            actual_summary={"hunt_created": True},
        )
        record = HuntReplayRecord.new(fixture, actual_outputs={"hunt_created": True}, diff_summary=diff, status="pass")
        validate_replay_result(HuntReplayResult(mode=HuntReplayMode.REPLAY_LOCAL, fixture=fixture, record=record))
        payload = record.to_dict()

        self.assertTrue(payload["replay_id"].startswith("shrpl_"))
        self.assertEqual("shs_test", payload["hunt_id"])
        self.assertEqual(len(ENABLED_REPLAY_STEP_KINDS), len(payload["expected_steps"]))
        self.assertEqual(len(BLOCKED_REPLAY_STEP_KINDS), len(payload["blocked_steps"]))
        self.assertFalse(payload["source_probe_executed"])
        self.assertFalse(payload["extraction_executed"])
        self.assertFalse(payload["model_provider_used"])


if __name__ == "__main__":
    unittest.main()
