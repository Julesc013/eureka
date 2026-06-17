"""Lightweight checks for public-facing documentation."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _local_markdown_links(markdown: str) -> list[str]:
    links: list[str] = []
    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", markdown):
        target = match.group(1).split("#", 1)[0].strip()
        if not target:
            continue
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            continue
        links.append(target)
    return links


def _python_script_refs(markdown: str) -> list[str]:
    return sorted(set(re.findall(r"python\s+(scripts[\\/][A-Za-z0-9_.-]+\.py)", markdown)))


class PublicDocsTests(unittest.TestCase):
    def test_readme_has_public_front_door_sections(self) -> None:
        readme = _read("README.md")
        required_headings = [
            "## Why Eureka Exists",
            "## Status At A Glance",
            "## What Eureka Is And Is Not",
            "## Current Capabilities",
            "## Quick Start",
            "## Example Use Cases",
            "## How It Works",
            "## Architecture Map",
            "## Documentation Map",
            "## Public Alpha Posture",
            "## Development Workflow",
            "## Roadmap",
            "## Contributing, Security, And Conduct",
            "## License",
        ]
        for heading in required_headings:
            with self.subTest(heading=heading):
                self.assertIn(heading, readme)

    def test_public_doc_links_exist(self) -> None:
        for doc_path in ("README.md", "docs/README.md", "docs/STATUS.md"):
            markdown = _read(doc_path)
            base = (REPO_ROOT / doc_path).parent
            for link in _local_markdown_links(markdown):
                with self.subTest(doc=doc_path, link=link):
                    target = (base / link).resolve()
                    try:
                        target.relative_to(REPO_ROOT)
                    except ValueError:
                        self.fail(f"{doc_path} links outside repo: {link}")
                    self.assertTrue(target.exists(), f"{doc_path} broken link: {link}")

    def test_readme_script_commands_reference_existing_wrappers(self) -> None:
        readme = _read("README.md")
        refs = _python_script_refs(readme)
        self.assertTrue(refs, "README should document at least one script command")
        for script in refs:
            with self.subTest(script=script):
                self.assertTrue((REPO_ROOT / script).is_file(), script)

    def test_readme_avoids_positive_launch_and_production_claims(self) -> None:
        readme = _read("README.md").lower()
        prohibited_positive_claims = [
            "is production-ready",
            "production-ready service",
            "is publicly launched",
            "open internet ready",
            "hosted production service",
        ]
        for claim in prohibited_positive_claims:
            with self.subTest(claim=claim):
                self.assertNotIn(claim, readme)

        required_negative_claims = [
            "not deployed",
            "not publicly launched",
            "does not claim production readiness",
        ]
        for claim in required_negative_claims:
            with self.subTest(claim=claim):
                self.assertIn(claim, readme)

    def test_license_posture_is_restricted_and_not_open_source(self) -> None:
        readme = _read("README.md").lower()
        license_text = _read("LICENSE.md").lower()
        summary = _read("LICENSE-SUMMARY.md").lower()

        required_readme_claims = [
            "source-available",
            "not open-source software",
            "restricted source-viewing license",
        ]
        for claim in required_readme_claims:
            with self.subTest(claim=claim):
                self.assertIn(claim, readme)

        required_license_claims = [
            "licenseref-eureka-rsvl-0.1",
            "non-open-source",
            "no redistribution",
            "no public service hosting",
            "contribution exception",
            "third-party materials",
        ]
        for claim in required_license_claims:
            with self.subTest(claim=claim):
                self.assertIn(claim, license_text)

        self.assertIn("not the license", summary)


if __name__ == "__main__":
    unittest.main()
