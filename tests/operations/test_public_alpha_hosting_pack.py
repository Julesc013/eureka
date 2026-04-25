from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PACK_DIR = REPO_ROOT / "docs" / "operations" / "public_alpha_hosting_pack"
INVENTORY_PATH = REPO_ROOT / "control" / "inventory" / "public_alpha_routes.json"
GENERATOR_PATH = REPO_ROOT / "scripts" / "generate_public_alpha_hosting_pack.py"
PACK_FILES = {
    "README.md",
    "RUNBOOK.md",
    "ROUTE_SAFETY_SUMMARY.md",
    "SMOKE_EVIDENCE_TEMPLATE.md",
    "OPERATOR_SIGNOFF_TEMPLATE.md",
    "BLOCKERS.md",
    "hosting_pack_manifest.json",
}
MAJOR_BLOCKERS = (
    "no auth or accounts",
    "no eureka-provided https/tls posture",
    "no rate limiting or abuse controls",
    "no production logging or monitoring posture",
    "no process supervisor or deployment posture",
    "local-path semantics still require careful mode policy",
    "review-required routes remain unresolved",
    "no public data governance policy",
    "no takedown or abuse contact process",
    "no production source-sync policy",
    "no privacy review for any future memory sharing",
)


class PublicAlphaHostingPackTestCase(unittest.TestCase):
    def test_hosting_pack_files_exist(self) -> None:
        for name in PACK_FILES:
            self.assertTrue((PACK_DIR / name).exists(), name)

    def test_manifest_parses_and_references_pack_files(self) -> None:
        manifest = json.loads((PACK_DIR / "hosting_pack_manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["pack_id"], "public_alpha_hosting_pack")
        self.assertEqual(manifest["status"], "supervised_rehearsal_only")
        self.assertEqual(manifest["created_by_slice"], "public_alpha_hosting_pack_v0")
        self.assertTrue(set(manifest["includes"]) <= PACK_FILES)
        self.assertIn("python scripts/public_alpha_smoke.py", manifest["required_checks"])
        self.assertIn(
            "control/inventory/public_alpha_routes.json",
            manifest["source_artifacts"]["route_inventory"],
        )

    def test_runbook_references_real_commands_or_marks_gap(self) -> None:
        runbook = (PACK_DIR / "RUNBOOK.md").read_text(encoding="utf-8")

        self.assertIn("Known Command Gap", runbook)
        self.assertIn("python scripts/public_alpha_smoke.py", runbook)
        self.assertIn("python scripts/generate_public_alpha_hosting_pack.py --check", runbook)
        self.assertIn("python scripts/demo_web_workbench.py --mode public_alpha", runbook)

        for script in sorted(set(re.findall(r"python (scripts/[^\s]+\.py)", runbook))):
            self.assertTrue((REPO_ROOT / script).exists(), script)

    def test_blockers_document_contains_major_non_production_blockers(self) -> None:
        blockers = (PACK_DIR / "BLOCKERS.md").read_text(encoding="utf-8").lower()

        for blocker in MAJOR_BLOCKERS:
            self.assertIn(blocker, blockers)

    def test_signoff_template_has_required_checklist_items(self) -> None:
        signoff = (PACK_DIR / "OPERATOR_SIGNOFF_TEMPLATE.md").read_text(encoding="utf-8").lower()

        for item in (
            "repo synced",
            "worktree clean",
            "tests passed",
            "architecture checker passed",
            "smoke script passed",
            "public-alpha mode confirmed",
            "local-dev-only routes blocked",
            "route inventory reviewed",
            "blockers reviewed",
            "no production claim made",
            "rollback/stop procedure understood",
        ):
            self.assertIn(f"- [ ] {item}", signoff)
        self.assertIn("- name:", signoff)
        self.assertIn("- date:", signoff)

    def test_smoke_evidence_template_has_required_fields(self) -> None:
        evidence = (PACK_DIR / "SMOKE_EVIDENCE_TEMPLATE.md").read_text(encoding="utf-8").lower()

        for field in (
            "commit sha",
            "branch status",
            "working tree status",
            "test results",
            "smoke result summary",
            "route inventory",
            "safe route samples",
            "blocked route samples",
            "known failures",
            "operator decision",
        ):
            self.assertIn(field, evidence)
        self.assertNotIn("pass rehearsal: yes", evidence)

    def test_route_safety_summary_matches_inventory_counts(self) -> None:
        inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        summary = (PACK_DIR / "ROUTE_SAFETY_SUMMARY.md").read_text(encoding="utf-8")

        self.assertIn("control/inventory/public_alpha_routes.json", summary)
        self.assertIn("machine-readable source of truth", summary)
        counts: dict[str, int] = {}
        for route in inventory["routes"]:
            counts[str(route["classification"])] = counts.get(str(route["classification"]), 0) + 1

        self.assertIn(f"- total routes: {len(inventory['routes'])}", summary)
        for classification in inventory["classification_values"]:
            self.assertIn(f"- {classification}: {counts.get(classification, 0)}", summary)

    def test_generator_output_matches_checked_summary(self) -> None:
        module = _load_generator()
        inventory = module.load_inventory(INVENTORY_PATH)
        generated = module.format_route_safety_summary(inventory)
        current = (PACK_DIR / "ROUTE_SAFETY_SUMMARY.md").read_text(encoding="utf-8")

        self.assertEqual(generated, current)

    def test_pack_docs_do_not_claim_production_readiness(self) -> None:
        for path in PACK_DIR.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            for line_number, line in enumerate(text.splitlines(), start=1):
                lowered = line.lower()
                if "production-ready" not in lowered and "production ready" not in lowered:
                    continue
                self.assertTrue(
                    any(marker in lowered for marker in ("not", "no ", "does not", "do not", "blocked")),
                    f"{path}:{line_number}: {line}",
                )


def _load_generator():
    spec = importlib.util.spec_from_file_location("generate_public_alpha_hosting_pack", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("Unable to load hosting pack generator.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    unittest.main()
