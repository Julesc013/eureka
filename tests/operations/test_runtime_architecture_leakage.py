from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "audit_runtime_architecture_leakage.py"
VALIDATOR = ROOT / "scripts" / "validate_runtime_architecture_leakage.py"
POLICY = ROOT / "control" / "policies" / "runtime_architecture_leakage_policy.json"
ALLOWLIST = ROOT / "control" / "policies" / "runtime_architecture_leakage_allowlist.json"
REPORT = ROOT / "control" / "audits" / "r0-02-runtime-architecture-leakage-gate-v0" / "r0_02_report.json"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_runtime_architecture_leakage", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def minimal_policy() -> dict:
    return {
        "schema_version": "runtime_architecture_leakage_policy.v0",
        "policy_id": "runtime_architecture_leakage_policy",
        "status": "active",
        "enforcement_mode": "report_then_block_new",
        "production_paths": [
            "runtime/**",
            "surfaces/**",
            "site/**",
            "native/**",
            "crates/**",
            "contracts/**",
            "contracts/domain/**",
            "contracts/runtime/**",
            "contracts/api/**",
            "contracts/snapshot/**",
            "contracts/native/**",
        ],
        "control_paths": [
            ".aide/**",
            "control/audits/**",
            "control/inventory/**",
            "control/policies/**",
            "docs/operations/**",
            "examples/**",
            "tests/**",
            "scripts/audit_*.py",
            "scripts/validate_*.py",
        ],
        "test_fixture_paths": ["examples/**", "tests/**", "control/audits/**/generated/**"],
        "forbidden_terms": [
            "H0",
            "H1",
            "H2",
            "H3",
            "H4",
            "H5",
            "H6",
            "H7",
            "H8",
            "H9",
            "H10",
            "H11",
            "H12",
            "H13",
            "H14",
            "BUNDLE",
            "IA-BUNDLE",
            "F-BUNDLE",
            "G-BUNDLE",
            "MVP",
            "LOCAL-MVP",
            "AIDE",
            "prompt",
            "agent",
            "human_obs",
            "fixture_only",
            "preview_only",
            "truth_boundary",
            "product_boundary",
            "review_seed",
            "next_phase",
            "quality_delta",
            "integration_audit",
        ],
        "forbidden_regexes": [
            {
                "id": "phase_bundle_identifier",
                "pattern": "(?i)(?<![A-Za-z0-9])(?:h(?:[0-9]|1[0-4])|ia|f|g)[_-]?bundle(?:[_-]|$)",
            }
        ],
        "high_risk_terms": ["truth_boundary", "product_boundary", "review_seed"],
        "allowed_terms_by_path": [],
        "known_temporary_violations_policy": {},
        "failure_rules": {},
        "no_goals": [],
    }


def minimal_allowlist(entries=None) -> dict:
    return {
        "schema_version": "runtime_architecture_leakage_allowlist.v0",
        "allowlist_id": "runtime_architecture_leakage_allowlist",
        "entries": list(entries or []),
    }


def make_repo(root: Path, entries=None) -> None:
    write(root / "control/policies/runtime_architecture_leakage_policy.json", json.dumps(minimal_policy(), indent=2))
    write(root / "control/policies/runtime_architecture_leakage_allowlist.json", json.dumps(minimal_allowlist(entries), indent=2))


class RuntimeArchitectureLeakageTests(unittest.TestCase):
    def run_script(self, repo: Path, *args: str):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--repo-root", str(repo), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_policy_json_validates(self):
        payload = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertEqual("runtime_architecture_leakage_policy.v0", payload["schema_version"])
        self.assertIn("runtime/**", payload["production_paths"])
        self.assertIn("H1", payload["forbidden_terms"])
        self.assertIn("truth_boundary", payload["forbidden_terms"])

    def test_allowlist_json_validates(self):
        payload = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
        self.assertEqual("runtime_architecture_leakage_allowlist.v0", payload["schema_version"])
        self.assertIsInstance(payload["entries"], list)
        self.assertTrue(payload["entries"])
        self.assertNotIn("never", {entry.get("expires_after_task") for entry in payload["entries"][:100]})

    def test_detects_h1_in_runtime_path_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_repo(repo)
            write(repo / "runtime/connectors/h1_metadata_wave/__init__.py", "H1_SOURCE_IDS = []\n")
            proc = self.run_script(repo, "--check", "--json")
            self.assertNotEqual(0, proc.returncode)
            payload = json.loads(proc.stdout)
            terms = {item["term"] for item in payload["findings"]}
            self.assertIn("H1", terms)

    def test_allows_h1_in_control_audits_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_repo(repo)
            write(repo / "control/audits/h1-audit/report.md", "H1 is allowed in audit evidence.\n")
            proc = self.run_script(repo, "--check", "--json")
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(0, payload["summary"]["new_violation_count"])

    def test_detects_truth_boundary_in_production_like_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_repo(repo)
            write(repo / "runtime/source_policy.py", "truth_boundary = 'bad runtime vocabulary'\n")
            proc = self.run_script(repo, "--check", "--json")
            self.assertNotEqual(0, proc.returncode)
            payload = json.loads(proc.stdout)
            finding = next(item for item in payload["findings"] if item["term"] == "truth_boundary")
            self.assertEqual("high", finding["severity"])
            self.assertIn("recommended_replacement", finding)

    def test_allows_truth_boundary_in_tests_or_validators(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_repo(repo)
            write(repo / "tests/operations/test_truth_boundary_fixture.py", "assert 'truth_boundary'\n")
            write(repo / "scripts/validate_truth_boundary.py", "TERM = 'truth_boundary'\n")
            proc = self.run_script(repo, "--check", "--json")
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(0, payload["summary"]["new_violation_count"])

    def test_detects_bundle_in_production_function_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_repo(repo)
            write(repo / "runtime/source_policy.py", "def build_h14_bundle_result():\n    return {}\n")
            proc = self.run_script(repo, "--check", "--json")
            self.assertNotEqual(0, proc.returncode)
            payload = json.loads(proc.stdout)
            terms = {item["term"] for item in payload["findings"]}
            self.assertIn("BUNDLE", terms)

    def test_ignores_safe_domain_words(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_repo(repo)
            write(repo / "runtime/http_headers.py", "USER_AGENT_HEADER = 'User-Agent'\n")
            proc = self.run_script(repo, "--check", "--json")
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(0, payload["summary"]["new_violation_count"])
            self.assertGreaterEqual(payload["summary"]["false_positive_candidate_count"], 1)

    def test_ignores_html_heading_tags_and_domain_bundle_words(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_repo(repo)
            write(
                repo / "site/dist/index.html",
                "<h1>Eureka</h1>\n<h2>Status</h2>\n<p>Local bundle fixture record.</p>\n",
            )
            proc = self.run_script(repo, "--check", "--json")
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(0, payload["summary"]["new_violation_count"])
            self.assertGreaterEqual(payload["summary"]["false_positive_candidate_count"], 3)

    def test_reports_path_line_severity_and_recommendation(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_repo(repo)
            write(repo / "runtime/source_policy.py", "\ntruth_boundary = True\n")
            proc = self.run_script(repo, "--check", "--json")
            payload = json.loads(proc.stdout)
            finding = next(item for item in payload["findings"] if item["term"] == "truth_boundary")
            self.assertEqual("runtime/source_policy.py", finding["path"])
            self.assertEqual(2, finding["line"])
            self.assertEqual("high", finding["severity"])
            self.assertIn("Replace truth_boundary", finding["recommended_replacement"])

    def test_respects_temporary_allowlist(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_repo(repo)
            target = repo / "runtime/connectors/h1_metadata_wave/__init__.py"
            write(target, "H1_SOURCE_IDS = []\n")
            module = load_audit_module()
            policy = minimal_policy()
            audit = module.build_leakage_audit(repo, policy, minimal_allowlist())
            entries = []
            for finding in [item for item in audit["findings"] if item["term"] == "H1"]:
                entries.append(
                    {
                        "path": finding["path"],
                        "term": finding["term"],
                        "line": finding["line"],
                        "column": finding["column"],
                        "context_sha256": finding["context_sha256"],
                        "reason": "existing test violation",
                        "expires_after_task": "R0-04",
                        "owner": "repo",
                        "replacement": "source_observation",
                        "severity_after_expiry": "blocker",
                    }
                )
            write(repo / "control/policies/runtime_architecture_leakage_allowlist.json", json.dumps(minimal_allowlist(entries), indent=2))
            proc = self.run_script(repo, "--check", "--json")
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(0, payload["summary"]["new_violation_count"])
            self.assertGreaterEqual(payload["summary"]["known_allowlisted_violation_count"], 1)

    def test_expired_allowlist_fails_enforce_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_repo(repo)
            write(repo / "runtime/source_policy.py", "truth_boundary = True\n")
            module = load_audit_module()
            audit = module.build_leakage_audit(repo, minimal_policy(), minimal_allowlist())
            finding = next(item for item in audit["findings"] if item["term"] == "truth_boundary")
            entry = {
                "path": finding["path"],
                "term": finding["term"],
                "line": finding["line"],
                "column": finding["column"],
                "context_sha256": finding["context_sha256"],
                "reason": "expired test violation",
                "expires_after_task": "R0-01",
                "owner": "repo",
                "replacement": "evidence_acceptance_policy",
                "severity_after_expiry": "high",
            }
            write(repo / "control/policies/runtime_architecture_leakage_allowlist.json", json.dumps(minimal_allowlist([entry]), indent=2))
            proc = self.run_script(repo, "--enforce", "--json")
            self.assertNotEqual(0, proc.returncode)
            payload = json.loads(proc.stdout)
            self.assertEqual(1, payload["summary"]["expired_allowlist_count"])

    def test_writes_no_files_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_repo(repo)
            write(repo / "runtime/source_policy.py", "truth_boundary = True\n")
            before = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())
            self.run_script(repo, "--check")
            after = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())
            self.assertEqual(before, after)

    def test_writes_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            make_repo(repo)
            write(repo / "runtime/source_policy.py", "truth_boundary = True\n")
            out_json = Path(tmp) / "report.json"
            out_md = Path(tmp) / "summary.md"
            proc = self.run_script(repo, "--output", str(out_json), "--summary-output", str(out_md), "--json")
            self.assertNotEqual(0, proc.returncode)
            self.assertTrue(out_json.is_file())
            self.assertTrue(out_md.is_file())
            self.assertEqual("runtime_architecture_leakage_gate_report.v0", json.loads(out_json.read_text(encoding="utf-8"))["schema_version"])

    def test_refuses_forbidden_output_roots(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_repo(repo)
            proc = self.run_script(repo, "--output", str(repo / "runtime/report.json"))
            self.assertNotEqual(0, proc.returncode)
            self.assertIn("refusing forbidden output root", proc.stdout + proc.stderr)

    def test_validator_passes_current_repo_or_reports_only_known_allowlisted(self):
        proc = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)

    def test_validator_and_audit_do_not_call_network_or_provider(self):
        for path in (SCRIPT, VALIDATOR):
            text = path.read_text(encoding="utf-8")
            for marker in ("url" + "open(", "requests" + ".", "httpx" + ".", "openai" + ".", "anthropic" + "."):
                self.assertNotIn(marker, text)

    def test_validator_and_audit_do_not_import_runtime_modules(self):
        for path in (SCRIPT, VALIDATOR):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertNotIn("runtime", {alias.name.split(".")[0] for alias in node.names})
                elif isinstance(node, ast.ImportFrom):
                    self.assertNotEqual("runtime", (node.module or "").split(".")[0])

    def test_r0_report_blocks_f0_and_dev_to_main(self):
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertIs(payload["f0_should_remain_blocked"], True)
        self.assertIs(payload["dev_to_main_should_remain_blocked"], True)
        self.assertEqual("R0-03 — Contract taxonomy refactor", payload["recommended_next_task"])


if __name__ == "__main__":
    unittest.main()
