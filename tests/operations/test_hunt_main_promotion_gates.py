import copy
import tempfile
import unittest
from pathlib import Path

from scripts.audit_hunt_main_promotion import build_promotion_records
from scripts.hunt_queue_progress import current_recommended_task_id, post_hunt_current_allowed
from scripts.validate_hunt_main_promotion import validate_branch_plan, validate_gates, validate_result


ROOT = Path(__file__).resolve().parents[2]


class HuntMainPromotionGateTests(unittest.TestCase):
    def test_all_current_blocking_gates_pass(self):
        records = build_promotion_records(ROOT)
        errors = []
        validate_gates(records["gate_matrix"], errors)
        self.assertEqual([], errors)

    def test_gate_matrix_fails_if_full_discovery_or_generated_cleanliness_fails(self):
        for gate_id in ("full_unittest_discovery_pass", "generated_artifact_cleanliness_pass"):
            records = build_promotion_records(ROOT)
            gate = next(row for row in records["gate_matrix"]["gates"] if row["gate_id"] == gate_id)
            gate["actual"] = False
            gate["status"] = "fail"
            errors = []
            validate_gates(records["gate_matrix"], errors)
            self.assertIn(f"promotion gate failed: {gate_id}", errors)

    def test_branch_plan_rejects_force_push_or_history_rewrite(self):
        for field in ("force_push_allowed", "history_rewrite_allowed", "rebase_allowed", "squash_allowed"):
            records = build_promotion_records(ROOT)
            plan = copy.deepcopy(records["branch_plan"])
            plan[field] = True
            errors = []
            validate_branch_plan(plan, errors)
            self.assertTrue(any(field in error for error in errors), field)

    def test_result_rejects_force_push_and_history_rewrite_performed(self):
        for field in ("force_push_performed", "history_rewrite_performed"):
            records = build_promotion_records(ROOT)
            payload = copy.deepcopy(records["result"])
            payload[field] = True
            errors = []
            validate_result(payload, errors)
            self.assertIn(f"result {field} must be false", errors)

    def test_post_hunt_queue_accepts_decorated_syn_task_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = root / ".aide/queue/index.yaml"
            queue.parent.mkdir(parents=True)
            queue.write_text(
                "current_recommended_task: SYN-00 - Synthetic Query Foundry planning over Local Appliance\n"
                "entries:\n"
                "  - id: HUNT-12\n"
                "    status: completed\n"
                "  - id: SYN-00\n"
                "    status: ready\n",
                encoding="utf-8",
            )
            self.assertEqual("SYN-00", current_recommended_task_id(root))
            self.assertTrue(post_hunt_current_allowed(root))

    def test_post_hunt_queue_accepts_source_snapshot_wait_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = root / ".aide/queue/index.yaml"
            queue.parent.mkdir(parents=True)
            queue.write_text(
                "current_recommended_task: SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01 - Close source/snapshot validation debt\n"
                "completed:\n"
                "  - SOURCE-ACTION-KERNEL-00\n"
                "  - SOURCE-WAVE-00\n"
                "  - SNAPSHOT-RELAY-00\n"
                "  - CI-FULL-DISCOVERY-HARNESS-00\n"
                "waiting:\n"
                "  - SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01\n",
                encoding="utf-8",
            )
            self.assertEqual("SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01", current_recommended_task_id(root))
            self.assertTrue(post_hunt_current_allowed(root))

    def test_post_hunt_queue_accepts_later_validator_repair_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = root / ".aide/queue/index.yaml"
            queue.parent.mkdir(parents=True)
            queue.write_text(
                "current_recommended_task: HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-03 - Repair stale validator expectations\n"
                "completed:\n"
                "  - HUNT-12\n"
                "  - SOURCE-ACTION-KERNEL-00\n"
                "  - SOURCE-WAVE-00\n"
                "  - SNAPSHOT-RELAY-00\n"
                "  - CI-FULL-DISCOVERY-HARNESS-00\n",
                encoding="utf-8",
            )
            self.assertEqual("HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-03", current_recommended_task_id(root))
            self.assertTrue(post_hunt_current_allowed(root))

    def test_post_hunt_queue_accepts_external_artifact_wait_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = root / ".aide/queue/index.yaml"
            queue.parent.mkdir(parents=True)
            queue.write_text(
                "current_recommended_task: WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE - External evidence required\n"
                "completed:\n"
                "  - SOURCE-ACTION-KERNEL-00\n"
                "  - SOURCE-WAVE-00\n"
                "  - SNAPSHOT-RELAY-00\n"
                "  - CI-FULL-DISCOVERY-HARNESS-00\n",
                encoding="utf-8",
            )
            self.assertEqual("WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE", current_recommended_task_id(root))
            self.assertTrue(post_hunt_current_allowed(root))

    def test_post_hunt_queue_accepts_ia_metadata_provider_smoke_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = root / ".aide/queue/index.yaml"
            queue.parent.mkdir(parents=True)
            queue.write_text(
                "current_recommended_task: IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00 - Bounded IA metadata provider smoke\n"
                "completed:\n"
                "  - SOURCE-ACTION-KERNEL-00\n"
                "  - SOURCE-WAVE-00\n"
                "  - SNAPSHOT-RELAY-00\n"
                "  - CI-FULL-DISCOVERY-HARNESS-00\n",
                encoding="utf-8",
            )
            self.assertEqual("IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00", current_recommended_task_id(root))
            self.assertTrue(post_hunt_current_allowed(root))

    def test_post_hunt_queue_accepts_current_repair_and_rerun_chain(self):
        for task_id in (
            "HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-08",
            "EXTERNAL-FULL-DISCOVERY-RERUN-09",
            "SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-09",
            "WAITING_FOR_USER_HARDWARE_DETAILS",
        ):
            with self.subTest(task_id=task_id), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                queue = root / ".aide/queue/index.yaml"
                queue.parent.mkdir(parents=True)
                queue.write_text(
                    f"current_recommended_task: {task_id} - governed successor\n"
                    "completed:\n"
                    "  - SOURCE-ACTION-KERNEL-00\n"
                    "  - SOURCE-WAVE-00\n"
                    "  - SNAPSHOT-RELAY-00\n"
                    "  - CI-FULL-DISCOVERY-HARNESS-00\n",
                    encoding="utf-8",
                )
                self.assertEqual(task_id, current_recommended_task_id(root))
                self.assertTrue(post_hunt_current_allowed(root))

    def test_post_hunt_queue_rejects_launch_readiness_and_promotion_without_gate(self):
        for task_id in (
            "PUBLIC-ALPHA-LAUNCH-00",
            "PUBLIC-ALPHA-READINESS-00",
            "DEV-TO-MAIN-PROMOTION-REVIEW-05",
        ):
            with self.subTest(task_id=task_id), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                queue = root / ".aide/queue/index.yaml"
                queue.parent.mkdir(parents=True)
                queue.write_text(
                    f"current_recommended_task: {task_id} - gated task\n"
                    "completed:\n"
                    "  - SOURCE-ACTION-KERNEL-00\n"
                    "  - SOURCE-WAVE-00\n"
                    "  - SNAPSHOT-RELAY-00\n"
                    "  - CI-FULL-DISCOVERY-HARNESS-00\n",
                    encoding="utf-8",
                )
                self.assertEqual(task_id, current_recommended_task_id(root))
                self.assertFalse(post_hunt_current_allowed(root))

    def test_post_hunt_queue_rejects_arbitrary_future_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = root / ".aide/queue/index.yaml"
            queue.parent.mkdir(parents=True)
            queue.write_text(
                "current_recommended_task: FUTURE-RANDOM-LAUNCH-00 - not authorized\n"
                "completed:\n"
                "  - SOURCE-ACTION-KERNEL-00\n"
                "  - SOURCE-WAVE-00\n"
                "  - SNAPSHOT-RELAY-00\n"
                "  - CI-FULL-DISCOVERY-HARNESS-00\n",
                encoding="utf-8",
            )
            self.assertEqual("FUTURE-RANDOM-LAUNCH-00", current_recommended_task_id(root))
            self.assertFalse(post_hunt_current_allowed(root))


if __name__ == "__main__":
    unittest.main()
