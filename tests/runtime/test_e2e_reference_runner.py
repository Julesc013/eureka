from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runtime.resolution_run import (
    E2EReferenceRunner,
    LocalRunBundleStore,
    RunnerBudget,
    RunnerConfig,
    replay_run_bundle,
    run_e2e_reference_run,
    validate_run_bundle,
)
from runtime.resolution_run.errors import ResolutionRunValidationError
from runtime.resolution_run.event_log import validate_event_hash_chain


class E2EReferenceRunnerTests(unittest.TestCase):
    def test_synthetic_run_writes_durable_bundle_and_preserves_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_e2e_reference_run(
                "old blue FTP client for XP",
                out_root=temp_dir,
                write_bundle=True,
            )
            run_dir = Path(result["run_dir"])

            self.assertEqual("completed", result["run"]["state"])
            self.assertEqual(2, result["workunit_schedule"]["workunit_count"])
            self.assertTrue((run_dir / "run_manifest.json").is_file())
            self.assertTrue((run_dir / "events.jsonl").is_file())
            self.assertFalse(result["boundaries"]["network_provider_calls"])
            self.assertFalse(result["boundaries"]["reviewed_record_created"])
            self.assertFalse(result["boundaries"]["public_index_mutation"])

            manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(run_dir.name, manifest["run_dir"])
            self.assertFalse(Path(manifest["run_dir"]).is_absolute())
            self.assertEqual("completed", manifest["current_state"])
            self.assertFalse(manifest["accepted_truth"])

    def test_event_log_has_monotonic_sequence_and_valid_hash_chain(self) -> None:
        result = run_e2e_reference_run("sampleproject")
        events = result["events"]
        self.assertEqual(list(range(len(events))), [event["sequence"] for event in events])
        self.assertEqual([], validate_event_hash_chain(events))
        self.assertTrue(events[-1]["event_hash"])

    def test_replay_validates_bundle_without_provider_calls(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_e2e_reference_run("sampleproject", out_root=temp_dir, write_bundle=True)
            validation = validate_run_bundle(result["run_dir"], strict=True)
            replay = replay_run_bundle(result["run_dir"], strict=True)

            self.assertEqual("valid", validation["status"])
            self.assertEqual("replay_verified", replay["status"])
            self.assertFalse(replay["provider_network_calls"])
            self.assertFalse(replay["accepted_truth_created"])
            self.assertTrue((Path(result["run_dir"]) / "replay_report.json").is_file())

    def test_corrupt_event_hash_fails_strict_replay(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_e2e_reference_run("sampleproject", out_root=temp_dir, write_bundle=True)
            events_path = Path(result["run_dir"]) / "events.jsonl"
            lines = events_path.read_text(encoding="utf-8").splitlines()
            first = json.loads(lines[0])
            first["payload"]["query"] = "tampered"
            lines[0] = json.dumps(first, sort_keys=True)
            events_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

            validation = validate_run_bundle(result["run_dir"], strict=True)
            replay = replay_run_bundle(result["run_dir"], strict=True)

            self.assertEqual("invalid", validation["status"])
            self.assertEqual("replay_corrupt", replay["status"])

    def test_live_shadow_fails_closed_without_network(self) -> None:
        result = run_e2e_reference_run("sampleproject", mode="live-shadow")
        self.assertEqual("policy_blocked", result["run"]["state"])
        self.assertTrue(result["boundaries"]["policy_blocked"])
        self.assertFalse(result["boundaries"]["network_provider_calls"])
        self.assertFalse(result["boundaries"]["live_ia_call_performed"])

    def test_pause_resume_cancel_state_guards(self) -> None:
        runner = E2EReferenceRunner()
        run = runner.create("sampleproject")
        run["state"] = "running"
        paused = runner.pause(run)
        self.assertEqual("paused", paused["state"])
        resumed = runner.resume(paused)
        self.assertEqual("running", resumed["state"])
        cancelled = runner.cancel(resumed)
        self.assertEqual("cancelled", cancelled["state"])
        with self.assertRaises(ResolutionRunValidationError):
            runner.pause(cancelled)
        with self.assertRaises(ResolutionRunValidationError):
            runner.resume(run)

    def test_retry_partial_failure_and_fail_fast_are_explicit(self) -> None:
        retry = run_e2e_reference_run("sampleproject", fixture="retry_then_success")
        partial = run_e2e_reference_run("sampleproject", fixture="partial_success")
        failed = run_e2e_reference_run(
            "sampleproject",
            fixture="terminal_failure",
            budget=RunnerBudget(failure_policy="fail_fast"),
        )

        self.assertEqual("completed", retry["run"]["state"])
        self.assertGreater(retry["partial_failure_count"], 0)
        self.assertIn("workunit_retry_scheduled", {event["event_type"] for event in retry["events"]})
        self.assertEqual("completed_with_partial_failure", partial["run"]["terminal_posture"])
        self.assertEqual("failed", failed["run"]["state"])

    def test_workunit_and_event_budgets_are_enforced(self) -> None:
        workunit_limited = run_e2e_reference_run(
            "sampleproject",
            budget=RunnerBudget(max_workunits=1),
        )
        event_limited = run_e2e_reference_run(
            "sampleproject",
            budget=RunnerBudget(max_events=4),
        )

        self.assertEqual(1, workunit_limited["workunit_schedule"]["workunit_count"])
        self.assertIn("budget_refused", {event["event_type"] for event in workunit_limited["events"]})
        self.assertEqual("failed", event_limited["run"]["state"])

    def test_timeout_budget_fails_without_sleeping(self) -> None:
        result = run_e2e_reference_run(
            "sampleproject",
            budget=RunnerBudget(max_elapsed_seconds=0),
        )

        self.assertEqual("failed", result["run"]["state"])
        self.assertIn("timeout_reached", {event["event_type"] for event in result["events"]})

    def test_bundle_writer_rejects_path_traversal_run_ids(self) -> None:
        store = LocalRunBundleStore(tempfile.mkdtemp())
        result = {
            "run": {"run_id": "../escape", "query": "x", "state": "created"},
            "workunit_schedule": {},
            "lane_snapshot": {},
            "boundaries": {},
        }
        with self.assertRaises(ResolutionRunValidationError):
            store.write_bundle(result, [])


if __name__ == "__main__":
    unittest.main()
