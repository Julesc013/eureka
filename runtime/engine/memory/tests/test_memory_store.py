from __future__ import annotations

import tempfile
import unittest

from runtime.engine.interfaces.public import ResolutionMemoryCatalogRequest
from runtime.engine.interfaces.service import ResolutionMemoryNotFoundError
from runtime.engine.memory.memory_store import LocalResolutionMemoryStore
from runtime.engine.memory.tests.test_support import build_successful_resolution_memory


class LocalResolutionMemoryStoreTestCase(unittest.TestCase):
    def test_save_load_and_filter_memories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = LocalResolutionMemoryStore(temp_dir)
            first = store.save_memory(build_successful_resolution_memory("memory-successful-resolution-0001"))
            second = store.save_memory(
                build_successful_resolution_memory(
                    "memory-successful-search-0002",
                    memory_kind="successful_search",
                    source_run_id="run-deterministic-search-0002",
                    task_kind="deterministic_search",
                )
            )

            loaded = store.get_memory(first.memory_id)
            all_memories = store.list_memories()
            filtered_by_kind = store.list_memories(
                ResolutionMemoryCatalogRequest.from_parts(memory_kind="successful_search"),
            )
            filtered_by_source = store.list_memories(
                ResolutionMemoryCatalogRequest.from_parts(checked_source_id="synthetic-fixtures"),
            )

        self.assertEqual(loaded.memory_id, first.memory_id)
        self.assertEqual(len(all_memories), 2)
        self.assertEqual([memory.memory_id for memory in filtered_by_kind], [second.memory_id])
        self.assertEqual(len(filtered_by_source), 2)

    def test_unknown_memory_raises_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = LocalResolutionMemoryStore(temp_dir)
            with self.assertRaises(ResolutionMemoryNotFoundError):
                store.get_memory("memory-missing-0001")


if __name__ == "__main__":
    unittest.main()
