# Generated Artifact Policy

Generated artifacts are allowed in the repository only when their ownership and update rules are explicit.

## Classes

- `canonical_generated`: committed generated data that is part of repo-local operation, such as `site/dist/data/public_index`.
- `deployment_generated`: generated deployable output. `site/dist` is in this class and is not a normal test output path.
- `audit_generated`: generated evidence under explicit `control/audits/**/generated` paths.
- `fixture_generated`: generated example or fixture checksums, such as demand dashboard example checksum manifests.
- `temp_test_generated`: temporary output created under a test temp directory.
- `historical_evidence`: committed evidence packs that can be refreshed only through their owning script.
- `source_input`: normal source material that is not treated as generated output.
- `unknown`: generated-looking output without a policy classification.

## Rules

Ordinary tests must write generated output to `tempfile.TemporaryDirectory` or another explicit temporary path. They must not mutate `site/dist`, `site/dist/data/public_index`, public rehearsal evidence, or committed fixture checksum manifests unless the test is specifically validating canonical regeneration.

Canonical regeneration is allowed only through a documented repo-local generator and must be followed by the owning validator. Regeneration must be scoped to the stale artifact and recorded in remediation evidence.

`site/dist` is a generated deployment artifact. It may be refreshed with `python site/build.py --clean --json`, then validated with `python site/validate.py`, `python scripts/generate_compatibility_surfaces.py --check`, and `python scripts/check_github_pages_static_artifact.py --path site/dist`.

Use `python scripts/check_generated_artifact_cleanliness.py --check --json` after tests to verify that generated roots stayed clean.
