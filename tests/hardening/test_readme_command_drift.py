import unittest

from tests.hardening.helpers import (
    fenced_command_blocks,
    repo_path,
    run_python,
    script_paths_from_commands,
    unresolved_local_markdown_links,
)


SAFE_README_COMMANDS = [
    ["scripts/demo_cli_workbench.py", "query-plan", "Windows 7 apps"],
    ["scripts/demo_cli_workbench.py", "sources"],
    ["scripts/run_archive_resolution_evals.py", "--task", "windows_7_apps"],
    ["scripts/generate_python_oracle_golden.py", "--check"],
    ["scripts/public_alpha_smoke.py"],
]


class ReadmeCommandDriftTest(unittest.TestCase):
    def test_readme_local_links_resolve(self):
        self.assertTrue(repo_path("README.md").exists())
        self.assertEqual(unresolved_local_markdown_links("README.md"), [])

    def test_readme_script_references_exist(self):
        commands = fenced_command_blocks("README.md")
        script_paths = script_paths_from_commands(commands)
        self.assertTrue(script_paths)
        missing = [path for path in script_paths if not repo_path(path).exists()]
        self.assertEqual(missing, [])

    def test_safe_representative_readme_commands_run(self):
        for command in SAFE_README_COMMANDS:
            with self.subTest(command=" ".join(command)):
                completed = run_python(command, timeout=120)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertTrue(completed.stdout.strip())


if __name__ == "__main__":
    unittest.main()
