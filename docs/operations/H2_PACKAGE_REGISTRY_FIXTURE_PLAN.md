# H2 Package Registry Fixture Plan

H2 records package-registry policy packs after H0/H1 Source OS patterns.

Current status is policy-pack-only. The records may describe source families,
planned metadata endpoint classes, fixture requirements, output boundaries,
package identity candidate fields, scorecard previews, and coverage previews.

This does not approve live source access, source sync, package downloads,
source archive downloads, OCI layer pulls, package manager invocation, install,
execution, public index mutation, master index mutation, evidence acceptance,
candidate acceptance, or public truth creation.

Package registry metadata is source observation material. Package names,
versions, hashes, licenses, dependencies, maintainers, URLs, advisories, and
PURL-style fields are candidates that require review before downstream use.

The expected next phase is H2-BUNDLE-02 fixture runtimes and normalizers using
committed fixtures only. H2-BUNDLE-03 may later request approved metadata-only
live probes, but that is not enabled by this bundle.

Validation:

```powershell
python scripts/validate_h2_package_registry_policy_packs.py
python scripts/summarize_h2_package_registry_sources.py --check
python -m unittest tests.operations.test_h2_package_registry_policy_packs
python -m unittest tests.operations.test_h2_package_registry_summary
```
