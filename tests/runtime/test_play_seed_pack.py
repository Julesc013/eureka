import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from validate_play_seed_pack import (  # noqa: E402
    COMPATIBILITY_QUERY,
    EXTRACTION_QUERY,
    HARD_SOURCE_ROUTING_QUERY,
    KNOWN_ABSENCE_QUERY,
    KNOWN_HIT_QUERY,
    MEDIA_QUERY,
    blocked_workunits,
    demo_absence,
    demo_search,
    load_play_pack,
    validate_play_seed_pack,
)


class PlaySeedPackTests(unittest.TestCase):
    def setUp(self):
        self.pack = load_play_pack([])

    def test_demo_query_pack_validates(self):
        result = validate_play_seed_pack(run_script_smokes=False)
        self.assertEqual("pass", result["status"], result)

    def test_known_hit_is_present(self):
        results = demo_search(self.pack, KNOWN_HIT_QUERY)
        self.assertTrue(results)
        self.assertEqual("play.reviewed.sampleproject.v0", results[0]["record_id"])

    def test_known_absence_is_present(self):
        absence = demo_absence(self.pack, KNOWN_ABSENCE_QUERY)
        self.assertIsNotNone(absence)
        self.assertEqual(0, absence["result_count"])
        self.assertEqual("play_demo_corpus_only", absence["absence_scope"])

    def test_unresolved_media_query_is_need_not_reviewed_record(self):
        reviewed_text = " ".join(record["searchable_text"] for record in self.pack["reviewed_records"]["records"])
        self.assertNotIn("d-theater", reviewed_text.lower())
        needs = [item for item in self.pack["search_needs"]["search_needs"] if item["query"] == MEDIA_QUERY]
        self.assertEqual(1, len(needs))
        self.assertFalse(needs[0]["verified_result_created"])

    def test_unresolved_extraction_query_is_need_and_blocked_workunit(self):
        needs = [item for item in self.pack["search_needs"]["search_needs"] if item["query"] == EXTRACTION_QUERY]
        self.assertEqual(1, len(needs))
        self.assertFalse(needs[0]["verified_result_created"])
        blocked = blocked_workunits(self.pack, kind="extraction_task")
        self.assertTrue(blocked)
        self.assertFalse(blocked[0]["payload"]["extraction_execution_enabled"])

    def test_hard_source_and_compatibility_queries_are_needs(self):
        queries = {item["query"]: item for item in self.pack["search_needs"]["search_needs"]}
        self.assertIn(HARD_SOURCE_ROUTING_QUERY, queries)
        self.assertIn(COMPATIBILITY_QUERY, queries)
        self.assertFalse(queries[HARD_SOURCE_ROUTING_QUERY]["verified_result_created"])
        self.assertFalse(queries[COMPATIBILITY_QUERY]["verified_result_created"])

    def test_blocked_future_action_workunits_remain_blocked(self):
        self.assertTrue(blocked_workunits(self.pack, kind="source_probe"))
        self.assertTrue(blocked_workunits(self.pack, kind="extraction_task"))
        self.assertTrue(blocked_workunits(self.pack, kind="agent_task"))

    def test_no_local_instance_state_is_committed(self):
        completed = subprocess.run(
            ["git", "ls-files", "--", "eureka-instance", "instances"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode)
        self.assertEqual("", completed.stdout.strip())


if __name__ == "__main__":
    unittest.main()
