from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "generate_static_resolver_demos.py"
PUBLIC_SITE = REPO_ROOT / "site/dist"
REQUIRED_FILES = {
    "demo/index.html",
    "demo/query-plan-windows-7-apps.html",
    "demo/result-member-driver-inside-support-cd.html",
    "demo/result-firefox-xp.html",
    "demo/result-article-scan.html",
    "demo/absence-example.html",
    "demo/comparison-example.html",
    "demo/source-example.html",
    "demo/eval-summary.html",
    "demo/README.txt",
    "demo/data/demo_snapshots.json",
}


class _LinkAndScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.script_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "script":
            self.script_count += 1
        for key, value in attrs:
            if key.lower() in {"href", "src"} and value:
                self.links.append(value)


class GenerateStaticResolverDemosScriptTest(unittest.TestCase):
    def test_generator_json_outputs_parseable_summary(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertFalse(payload["contains_live_backend"])
        self.assertFalse(payload["contains_live_probes"])
        self.assertFalse(payload["contains_external_observations"])
        self.assertGreaterEqual(payload["demo_count"], 8)
        self.assertEqual(set(payload["files"]), REQUIRED_FILES)

    def test_generator_check_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("check_mode: true", completed.stdout)

    def test_build_to_temp_output_produces_static_demo_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "site/dist"
            data = output / "data"
            data.mkdir(parents=True)
            for path in (PUBLIC_SITE / "data").glob("*.json"):
                (data / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-root",
                    str(output),
                    "--data-root",
                    str(data),
                    "--update",
                    "--json",
                ],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "valid")
            for relative in REQUIRED_FILES:
                with self.subTest(relative=relative):
                    self.assertTrue((output / relative).exists())

    def test_generated_demo_pages_are_no_js_and_relative_linked(self) -> None:
        for relative in REQUIRED_FILES:
            if not relative.endswith(".html"):
                continue
            path = PUBLIC_SITE / relative
            parser = _LinkAndScriptParser()
            parser.feed(path.read_text(encoding="utf-8"))
            with self.subTest(relative=relative):
                self.assertEqual(parser.script_count, 0)
                for link in parser.links:
                    self.assertFalse(link.startswith("/"), link)
                    self.assertFalse(link.startswith("https://julesc013.github.io/"), link)


if __name__ == "__main__":
    unittest.main()
