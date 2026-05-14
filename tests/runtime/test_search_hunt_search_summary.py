from __future__ import annotations

import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest

from runtime.public_index import PublicIndexRecord, PublicIndexStore
from runtime.search_hunt import build_local_absence_summary, build_reviewed_index_search_summary


class SearchHuntSummaryTests(unittest.TestCase):
    def test_reviewed_index_search_summary_uses_local_index_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = SimpleNamespace(public_index=prepared_public_index(Path(tmp) / "public_index.sqlite"))
            try:
                summary = build_reviewed_index_search_summary(runtime, "sampleproject")
                self.assertTrue(summary["reviewed_index_only"])
                self.assertFalse(summary["source_probe_executed"])
                self.assertFalse(summary["workunit_creation_performed"])
                self.assertEqual(1, summary["result_count"])
            finally:
                runtime.public_index.close()

    def test_absence_summary_labels_local_current_index_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = SimpleNamespace(public_index=prepared_public_index(Path(tmp) / "public_index.sqlite"))
            try:
                summary = build_local_absence_summary(runtime, "not-present")
                self.assertTrue(summary["local_current_index_absence_only"])
                self.assertIn("source_probes", summary["unchecked_layers"])
                self.assertIn("WorkUnits", summary["unchecked_layers"])
                self.assertFalse(summary["source_probe_executed"])
            finally:
                runtime.public_index.close()


def prepared_public_index(path: Path) -> PublicIndexStore:
    store = PublicIndexStore.open(path)
    store.init()
    store.write_record(
        PublicIndexRecord(
            record_id="pir_search_hunt_sample",
            source_id="source.local.search_hunt",
            source_cache_entry_id="sce_search_hunt_sample",
            evidence_id="evc_search_hunt_sample",
            review_item_id="rvi_search_hunt_sample",
            review_decision_id="rvd_search_hunt_sample",
            title="sampleproject",
            description="Synthetic reviewed record for Search Hunt tests",
            normalized_fields={"name": "sampleproject"},
            searchable_text="sampleproject synthetic reviewed local record",
            source_family="fixture_metadata",
            trust_lane="synthetic_reviewed",
        )
    )
    return store


if __name__ == "__main__":
    unittest.main()
