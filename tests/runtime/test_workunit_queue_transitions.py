from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from runtime.workunit_queue import WorkUnit, WorkUnitQueueStore, WorkUnitTransitionError, WorkUnitValidationError


class WorkUnitQueueTransitionTests(unittest.TestCase):
    def test_valid_transitions_pass_and_history_is_recorded(self) -> None:
        with store() as queue:
            item = queue.create_workunit(WorkUnit.new("search_need", "Transition sample"))
            queue.transition_workunit(item.id, "running", "start")
            queue.complete_workunit(item.id, "done")
            loaded = queue.get_workunit(item.id)
            self.assertEqual("complete", loaded.state.value)
            transitions = queue.list_transitions(item.id)
            self.assertEqual(["queued", "running", "complete"], [entry.to_state.value for entry in transitions])

    def test_invalid_transition_fails_closed(self) -> None:
        with store() as queue:
            item = queue.create_workunit(WorkUnit.new("search_need", "Invalid sample"))
            with self.assertRaises(WorkUnitTransitionError):
                queue.complete_workunit(item.id, "cannot complete queued")
            self.assertEqual("queued", queue.get_workunit(item.id).state.value)

    def test_pause_resume_cancel_block_complete_fail_helpers(self) -> None:
        with store() as queue:
            paused = queue.create_workunit(WorkUnit.new("source_probe", "Pause sample"))
            self.assertEqual("paused", queue.pause_workunit(paused.id, "pause").state.value)
            self.assertEqual("queued", queue.resume_workunit(paused.id, "resume").state.value)
            self.assertEqual("cancelled", queue.cancel_workunit(paused.id, "cancel").state.value)

            blocked = queue.create_workunit(WorkUnit.new("evidence_review", "Block sample"))
            self.assertEqual("blocked", queue.block_workunit(blocked.id, "blocked").state.value)
            self.assertEqual("queued", queue.resume_workunit(blocked.id, "resume").state.value)

            complete = queue.create_workunit(WorkUnit.new("regression_test", "Complete sample"))
            queue.transition_workunit(complete.id, "running", "start")
            self.assertEqual("complete", queue.complete_workunit(complete.id, "done").state.value)

            failed = queue.create_workunit(WorkUnit.new("extraction_task", "Fail sample"))
            queue.transition_workunit(failed.id, "running", "start")
            self.assertEqual("failed", queue.fail_workunit(failed.id, "failed").state.value)

    def test_block_and_fail_require_reason(self) -> None:
        with store() as queue:
            item = queue.create_workunit(WorkUnit.new("search_need", "Reason sample"))
            with self.assertRaises(WorkUnitValidationError):
                queue.block_workunit(item.id, "")
            queue.transition_workunit(item.id, "running", "start")
            with self.assertRaises(WorkUnitValidationError):
                queue.fail_workunit(item.id, "")

    def test_terminal_transition_is_idempotent(self) -> None:
        with store() as queue:
            item = queue.create_workunit(WorkUnit.new("search_need", "Terminal sample"))
            queue.transition_workunit(item.id, "running", "start")
            queue.complete_workunit(item.id, "done")
            before = len(queue.list_transitions(item.id))
            queue.complete_workunit(item.id, "repeat")
            after = len(queue.list_transitions(item.id))
            self.assertEqual(before, after)


def store() -> WorkUnitQueueStore:
    tmp = tempfile.TemporaryDirectory()
    path = Path(tmp.name) / "workunit_queue.sqlite"
    queue = WorkUnitQueueStore.open(path)
    queue.init()
    original_close = queue.close

    def close_with_tmp() -> None:
        original_close()
        tmp.cleanup()

    queue.close = close_with_tmp  # type: ignore[method-assign]
    return queue


if __name__ == "__main__":
    unittest.main()
