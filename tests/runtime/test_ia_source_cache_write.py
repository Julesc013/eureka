import tempfile
import unittest
from pathlib import Path

from runtime.source.cache import SourceCacheStore
from runtime.source.observation.internet_archive_source_cache import (
    build_ia_source_cache_records,
    load_fixture_normalized_records,
    load_ia_source_cache_policy,
    load_live_preview_records,
    write_ia_source_cache_records,
)


ROOT = Path(__file__).resolve().parents[2]


class IASourceCacheWriteTests(unittest.TestCase):
    def test_dry_run_does_not_mutate_store(self):
        policy = load_ia_source_cache_policy(ROOT / "control/policies/ia_source_cache_policy.json")
        records = build_ia_source_cache_records(load_fixture_normalized_records(ROOT / "examples/internet_archive_metadata")[:1], policy)
        with SourceCacheStore.open(":memory:") as store:
            store.init()
            result = write_ia_source_cache_records(store, records, dry_run=True)
            self.assertFalse(result["write_applied"])
            self.assertEqual(0, store.summarize().cache_entry_count)

    def test_apply_writes_fixture_and_live_preview_to_temp_store(self):
        policy = load_ia_source_cache_policy(ROOT / "control/policies/ia_source_cache_policy.json")
        inputs = load_fixture_normalized_records(ROOT / "examples/internet_archive_metadata")[:1]
        inputs.extend(load_live_preview_records(ROOT / "control/inventory/ia_02_tls_continue_normalized_preview.json")[:1])
        records = build_ia_source_cache_records(inputs, policy, live_probe_id="test")
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "source_cache.sqlite"
            with SourceCacheStore.open(db) as store:
                result = write_ia_source_cache_records(store, records, dry_run=False)
                self.assertTrue(result["write_applied"])
                self.assertEqual(2, result["summary"]["cache_entry_count"])
                self.assertEqual("pass", result["integrity"]["status"])


if __name__ == "__main__":
    unittest.main()
