import unittest

from tests.hardening.helpers import repo_path, unresolved_local_markdown_links


DOCS_TO_SCAN = [
    "README.md",
    "docs/ROADMAP.md",
    "docs/BOOTSTRAP_STATUS.md",
    "docs/ARCHITECTURE.md",
    "docs/operations/TEST_AND_EVAL_LANES.md",
    "docs/operations/public_alpha_hosting_pack/README.md",
    "tests/parity/README.md",
    "control/audits/README.md",
]


class DocsLinkDriftTest(unittest.TestCase):
    def test_major_docs_exist(self):
        missing = [path for path in DOCS_TO_SCAN if not repo_path(path).exists()]
        self.assertEqual(missing, [])

    def test_major_docs_local_links_resolve(self):
        broken = []
        for path in DOCS_TO_SCAN:
            broken.extend(unresolved_local_markdown_links(path))
        self.assertEqual(broken, [])


if __name__ == "__main__":
    unittest.main()
