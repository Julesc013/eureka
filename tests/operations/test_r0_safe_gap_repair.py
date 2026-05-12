from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "repair_r0_safe_gaps.py"


def load_module():
    spec = importlib.util.spec_from_file_location("repair_r0_safe_gaps", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def make_repo(root: Path) -> None:
    write_json(root / "control/inventory/r0_remaining_blockers.json", {"blockers": []})
    write_json(root / "control/inventory/r0_warning_disposition.json", {"warnings": []})


class R0SafeGapRepairTests(unittest.TestCase):
    def test_safe_repair_defaults_to_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_repo(repo)
            proc = subprocess.run([sys.executable, str(SCRIPT), "--repo-root", str(repo), "--json"], cwd=ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual("dry_run", payload["mode"])

    def test_safe_repair_refuses_unsafe_runtime_rewrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_json(repo / "control/inventory/r0_remaining_blockers.json", {"blockers": [{"blocker_id": "B", "area": "contract_taxonomy", "finding": "rewrite contracts"}]})
            write_json(repo / "control/inventory/r0_warning_disposition.json", {"warnings": []})
            module = load_module()
            result = module.build_repair_result(repo, apply=True)
            self.assertEqual(1, result["unsafe_gaps_detected"])
            self.assertEqual(1, result["unsafe_gaps_child_tasked"])
            self.assertEqual(0, result["safe_gaps_fixed"])

    def test_safe_repair_refuses_forbidden_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_repo(repo)
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--apply", "--output", str(repo / "runtime/out.json")],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, proc.returncode)
            self.assertIn("refusing forbidden output root", proc.stdout + proc.stderr)

    def test_apply_never_mutates_branch_or_indexes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_repo(repo)
            module = load_module()
            result = module.build_repair_result(repo, apply=True)
            self.assertFalse(result["branch_mutation_performed"])
            self.assertFalse(result["site_dist_mutated"])
            self.assertFalse(result["master_index_mutated"])
            self.assertFalse(result["network_used"])


if __name__ == "__main__":
    unittest.main()
