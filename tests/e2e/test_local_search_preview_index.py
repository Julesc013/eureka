from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from runtime.index.preview import build_preview_index
from runtime.local.local_search import LocalSearchOptions, LocalSearchService


ROOT = Path(__file__).resolve().parents[2]


class LocalSearchPreviewIndexTests(unittest.TestCase):
    def test_local_search_uses_preview_index_without_fallback_or_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate_manifest = _write_candidate_delta(Path(temp_dir))
            build = build_preview_index(out_root=Path(temp_dir) / "preview", candidate_delta=candidate_manifest)
            before = Path(build["current_path"]).read_text(encoding="utf-8")
            response = LocalSearchService().search(
                "WinFTP XP client",
                LocalSearchOptions(index="preview", index_path=build["current_path"], metadata_fallback="none"),
            )
            after = Path(build["current_path"]).read_text(encoding="utf-8")

        self.assertEqual("candidate", response["status"])
        self.assertEqual("preview_index", response["source_path"])
        self.assertTrue(response["index_results_used"])
        self.assertFalse(response["fallback_used"])
        self.assertFalse(response["network_used"])
        self.assertFalse(response["accepted_truth_created"])
        self.assertFalse(response["reviewed_index_mutated"])
        self.assertEqual(before, after)
        card = response["results"][0]
        self.assertEqual("candidate_only", card["authority"])
        self.assertTrue(card["preview_record_id"])
        self.assertIn("human review before promotion", card["missing"])

    def test_eureka_search_cli_can_read_preview_index(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate_manifest = _write_candidate_delta(Path(temp_dir))
            build = build_preview_index(out_root=Path(temp_dir) / "preview", candidate_delta=candidate_manifest)
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_search.py",
                    "WinFTP XP client",
                    "--index",
                    "preview",
                    "--index-path",
                    build["current_path"],
                    "--metadata-fallback",
                    "none",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("preview_index", payload["source_path"])
        self.assertEqual("candidate", payload["status"])
        self.assertFalse(payload["fallback_used"])
        self.assertFalse(payload["public_index_mutated"])


def _write_candidate_delta(root: Path) -> str:
    candidate_dir = root / "candidate"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    manifest = candidate_dir / "candidate_index_delta_manifest.json"
    records = candidate_dir / "candidate_index_delta.jsonl"
    manifest.write_text(json.dumps({"candidate_file": records.name}, sort_keys=True), encoding="utf-8")
    records.write_text(
        json.dumps(
            {
                "candidate_id": "candidate:ia_metadata:test-winftp",
                "source_family": "ia_metadata",
                "source_observation_refs": ["source-observation:ia_metadata:test-001"],
                "query_seed_refs": ["WinFTP XP client"],
                "provider_mode_refs": ["live"],
                "normalized_title": "WinFTP XP candidate",
                "normalized_type_hints": ["ftp_client"],
                "review_state": "unreviewed",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return str(manifest)


if __name__ == "__main__":
    unittest.main()
