import unittest

from runtime.index.public import PublicIndexStore
from runtime.source.observation.internet_archive_reviewed_index import (
    build_ia_reviewed_absence_packet,
    build_ia_reviewed_object_packet,
    build_ia_reviewed_records_from_promotion_previews,
    load_default_ia_promotion_previews,
    load_ia_reviewed_index_policy,
    rebuild_ia_reviewed_local_index,
    search_ia_reviewed_local_index,
)


class IAReviewedSearchPacketTests(unittest.TestCase):
    def test_search_object_and_absence_packets_work(self):
        policy = load_ia_reviewed_index_policy()
        records = build_ia_reviewed_records_from_promotion_previews(load_default_ia_promotion_previews(), policy)
        with PublicIndexStore.open(":memory:") as store:
            rebuild_ia_reviewed_local_index(store, records, dry_run=False)
            search_results = search_ia_reviewed_local_index(store, "sampleproject")
            self.assertTrue(search_results)
            self.assertTrue(all(result["reviewed_local_index_record"] for result in search_results))
            object_packet = build_ia_reviewed_object_packet(store, records[0]["reviewed_record_id"])
            self.assertTrue(object_packet["found"])
            absence_packet = build_ia_reviewed_absence_packet(store, "definitely-not-present-ia-07")
            self.assertTrue(absence_packet["absence_confirmed"])
            self.assertFalse(absence_packet["master_index_record"])


if __name__ == "__main__":
    unittest.main()
