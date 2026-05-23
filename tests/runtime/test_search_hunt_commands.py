from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from runtime.search.hunt import SearchHuntError, SearchHuntSession, SearchHuntStore


class SearchHuntCommandTests(unittest.TestCase):
    def test_pause_resume_cancel_commands_record_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with SearchHuntStore.open(Path(tmp) / "search_hunt.sqlite") as store:
                store.init()
                hunt = store.create_session(SearchHuntSession.new("sampleproject"))
                pause = store.apply_command(hunt.id, "pause", reason="operator pause")
                resume = store.apply_command(hunt.id, "resume", reason="operator resume")
                cancel = store.apply_command(hunt.id, "cancel", reason="operator cancel")

                self.assertEqual("paused", pause.command.resulting_state)
                self.assertEqual("running", resume.command.resulting_state)
                self.assertEqual("cancelled", cancel.command.resulting_state)
                self.assertEqual("cancelled", store.get_session(hunt.id).state.value)
                self.assertEqual(["pause", "resume", "cancel"], [item.command_type for item in store.list_commands(hunt.id)])

    def test_block_and_fail_require_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with SearchHuntStore.open(Path(tmp) / "search_hunt.sqlite") as store:
                store.init()
                block_hunt = store.create_session(SearchHuntSession.new("block sample"))
                fail_hunt = store.create_session(SearchHuntSession.new("fail sample"))
                store.transition_session(fail_hunt.id, "running", "prepare")

                with self.assertRaises(SearchHuntError):
                    store.apply_command(block_hunt.id, "block")
                with self.assertRaises(SearchHuntError):
                    store.apply_command(fail_hunt.id, "fail")

                self.assertEqual("blocked", store.apply_command(block_hunt.id, "block", reason="policy").command.resulting_state)
                self.assertEqual("failed", store.apply_command(fail_hunt.id, "fail", reason="runtime error").command.resulting_state)

    def test_wait_commands_and_invalid_commands_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with SearchHuntStore.open(Path(tmp) / "search_hunt.sqlite") as store:
                store.init()
                user_hunt = store.create_session(SearchHuntSession.new("user wait"))
                policy_hunt = store.create_session(SearchHuntSession.new("policy wait"))
                store.transition_session(user_hunt.id, "running", "prepare")
                store.transition_session(policy_hunt.id, "running", "prepare")

                self.assertEqual("waiting_for_user", store.apply_command(user_hunt.id, "wait_for_user", reason="needs input").command.resulting_state)
                self.assertEqual("waiting_for_policy", store.apply_command(policy_hunt.id, "wait_for_policy", reason="needs policy").command.resulting_state)
                with self.assertRaises((SearchHuntError, ValueError)):
                    store.apply_command(user_hunt.id, "not_a_command")

    def test_terminal_command_is_idempotent_where_practical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with SearchHuntStore.open(Path(tmp) / "search_hunt.sqlite") as store:
                store.init()
                hunt = store.create_session(SearchHuntSession.new("terminal sample"))
                first = store.apply_command(hunt.id, "cancel", reason="done")
                second = store.apply_command(hunt.id, "cancel", reason="again")

                self.assertEqual("cancelled", first.command.resulting_state)
                self.assertEqual("cancelled", second.command.resulting_state)
                self.assertEqual(2, len(store.list_commands(hunt.id)))


if __name__ == "__main__":
    unittest.main()
