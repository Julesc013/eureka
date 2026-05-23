from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

from tools.auditors.audit_generated_artifact_visibility import build_visibility_report


class GeneratedArtifactVisibilityAuditTestCase(unittest.TestCase):
    def test_classifies_allowed_generated_like_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "site/dist/index.html", "ok\n")
            write(root / "native/win/winforms/dist/README.md", "placeholder\n")
            write(root / "native/win/winforms/build/README.md", "placeholder\n")
            write(root / "examples/connectors/h1/coverage/example_coverage_preview_v0.json", "{}\n")
            git_add(root)

            report = build_visibility_report(root)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["tracked_site_dist_count"], 1)
        self.assertEqual(report["tracked_tmp_count"], 0)
        self.assertEqual(report["unexpected"]["dist"], [])
        self.assertEqual(report["unexpected"]["build"], [])
        self.assertEqual(report["unexpected"]["coverage"], [])

    def test_tmp_is_reported_for_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "tmp/output.json", "{}\n")
            git_add(root)

            report = build_visibility_report(root)

        self.assertEqual(report["status"], "needs_review")
        self.assertEqual(report["tracked_tmp_count"], 1)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git_add(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["git", "add", "."], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
