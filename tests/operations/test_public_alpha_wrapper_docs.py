import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class PublicAlphaWrapperDocsTest(unittest.TestCase):
    def test_wrapper_doc_records_safe_non_deployment_posture(self) -> None:
        text = read_text("docs/operations/PUBLIC_ALPHA_WRAPPER.md").lower()

        self.assertIn("live_alpha_01 production public-alpha wrapper", text)
        self.assertIn("this is not deployment", text)
        self.assertIn("live source probes: disabled", text)
        self.assertIn("live internet archive access: disabled", text)
        self.assertIn("caller-provided local paths: disabled", text)
        self.assertIn("deployment approval: false", text)
        self.assertIn("production readiness: false", text)
        self.assertIn("nonlocal bind", text)
        self.assertIn("deployment config pack", text)

    def test_public_alpha_docs_link_to_wrapper_without_claiming_deployment(self) -> None:
        docs = [
            "docs/operations/PUBLIC_ALPHA_SAFE_MODE.md",
            "docs/operations/PUBLIC_ALPHA_READINESS_REVIEW.md",
            "docs/operations/PUBLIC_ALPHA_OPERATOR_CHECKLIST.md",
            "docs/operations/public_alpha_hosting_pack/README.md",
            "docs/operations/public_alpha_rehearsal_evidence_v0/README.md",
            "docs/roadmap/PUBLIC_ALPHA.md",
        ]
        for path in docs:
            text = read_text(path).lower()
            compact = " ".join(text.split())
            self.assertTrue(
                "public alpha wrapper" in compact or "public-alpha wrapper" in compact,
                path,
            )
            self.assertTrue(
                "no deployment" in compact
                or "does no deployment" in compact
                or "performs no deployment" in compact,
                path,
            )
            self.assertIn("live probes", compact, path)

    def test_static_site_mentions_wrapper_and_preserves_caveats(self) -> None:
        for path in [
            "site/dist/status.html",
            "site/dist/roadmap.html",
            "site/dist/limitations.html",
        ]:
            text = read_text(path).lower()
            self.assertIn("public-alpha wrapper", text, path)
            self.assertIn("not production", text, path)
            self.assertIn("no live source probes", text, path)
            self.assertIn("external baselines pending/manual", text, path)


if __name__ == "__main__":
    unittest.main()
