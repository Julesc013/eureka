import unittest

from runtime.index.public import PublicIndexStore
from tests.runtime.test_public_index_store import make_record


class PublicIndexSearchAbsenceTests(unittest.TestCase):
    def test_search_returns_expected_record(self):
        with PublicIndexStore.open(":memory:") as store:
            store.init()
            store.write_record(make_record())
            results = store.search("demo project")
            self.assertEqual("pir_0123456789abcdef", results[0].record_id)

    def test_search_limit_works(self):
        with PublicIndexStore.open(":memory:") as store:
            store.init()
            store.write_record(make_record("pir_1111111111111111"))
            store.write_record(make_record("pir_2222222222222222"))
            self.assertEqual(1, len(store.search("demo", limit=1)))

    def test_absence_report_returns_checked_sources_and_limitations(self):
        with PublicIndexStore.open(":memory:") as store:
            store.init()
            store.write_record(make_record())
            report = store.absence_report("not present")
            self.assertEqual(0, report.result_count)
            self.assertIn("source.example.metadata", report.checked_sources)
            self.assertTrue(report.limitations)


if __name__ == "__main__":
    unittest.main()
