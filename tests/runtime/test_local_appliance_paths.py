import tempfile
import unittest
from pathlib import Path

from runtime.local_appliance.errors import LocalInstancePathError
from runtime.local_appliance.paths import (
    describe_instance_layout,
    resolve_default_instance_root,
    resolve_instance_root,
    resolve_instances_root,
    resolve_workspace_root,
)


class LocalAppliancePathsTests(unittest.TestCase):
    def test_preferred_default_is_sibling_instances_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "eureka"
            expected = Path(tmp) / "instances" / "default"
            self.assertEqual(expected.resolve(), resolve_default_instance_root(repo))
            self.assertEqual(expected.resolve(), resolve_instance_root(None, repo))

    def test_explicit_instance_path_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "eureka"
            explicit = Path(tmp) / "instances" / "smoke"
            self.assertEqual(explicit.resolve(), resolve_instance_root(explicit, repo))

    def test_legacy_sibling_is_accepted_when_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "eureka"
            legacy = Path(tmp) / "eureka-instance"
            root = resolve_instance_root(legacy, repo)
            self.assertEqual(legacy.resolve(), root)
            layout = describe_instance_layout(repo, root)
            self.assertEqual("legacy_sibling", layout["layout_class"])

    def test_repo_nested_instance_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "eureka"
            with self.assertRaises(LocalInstancePathError):
                resolve_instance_root(repo / "eureka-instance", repo)

    def test_clean_machine_temp_checkout_instance_is_accepted(self):
        with tempfile.TemporaryDirectory(prefix="eureka-clean-machine-") as tmp:
            repo = Path(tmp) / "checkout"
            repo.mkdir()
            instance = repo / "eureka-instance"
            root = resolve_instance_root(instance, repo)
            self.assertEqual(instance.resolve(), root)
            layout = describe_instance_layout(repo, root)
            self.assertEqual("clean_machine_temp_checkout", layout["layout_class"])

    def test_resolver_performs_no_filesystem_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "eureka"
            default = resolve_instance_root(None, repo)
            self.assertFalse(default.exists())
            self.assertFalse(resolve_instances_root(resolve_workspace_root(repo)).exists())


if __name__ == "__main__":
    unittest.main()
