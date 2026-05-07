from __future__ import annotations

import io
from pathlib import Path
import tempfile
import unittest

from scripts.preview_eureka_changelog import main, parse_commit_message, render_changelog_preview


REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE = REPO_ROOT / "examples/commit_messages/valid_structured_commit.txt"


class EurekaChangelogPreviewTest(unittest.TestCase):
    def test_changelog_preview_groups_sample_commit_changes(self) -> None:
        message = SAMPLE.read_text(encoding="utf-8")
        preview = render_changelog_preview([parse_commit_message(message)])

        self.assertIn("## Added", preview)
        self.assertIn("Structured commit sample", preview)
        self.assertIn("## Tests", preview)
        self.assertIn("## Internal", preview)

    def test_preview_cli_reads_message_file(self) -> None:
        output = io.StringIO()

        exit_code = main(["--message-file", str(SAMPLE)], stdout=output)

        self.assertEqual(exit_code, 0)
        self.assertIn("# Eureka Changelog Preview", output.getvalue())

    def test_preview_does_not_mutate_files_by_default(self) -> None:
        before = SAMPLE.read_text(encoding="utf-8")
        output = io.StringIO()

        main(["--message-file", str(SAMPLE)], stdout=output)

        self.assertEqual(SAMPLE.read_text(encoding="utf-8"), before)

    def test_preview_output_path_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "preview.md"

            exit_code = main(["--message-file", str(SAMPLE), "--output", str(output_path)], stdout=io.StringIO())

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.is_file())
            self.assertIn("## Added", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
