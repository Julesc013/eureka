# H2 Package Fixture Replay

H2-BUNDLE-02 converts offline replay commands and validation outputs.

This is fixture-runtime work only. It reads committed JSON fixtures,
normalizes package metadata, and emits package identity, dependency,
file/hash, source-cache, evidence, and replay-result candidates.

It does not approve live registry access, source sync, downloads,
package-manager invocation, installs, execution, public search
behavior changes, public-index mutation, master-index mutation, or
source/evidence/candidate/public truth acceptance.

The supported H2 sources are Maven Central, NuGet, crates.io,
RubyGems, CPAN, CRAN, conda-forge, and OCI registry metadata. Each
source keeps missing optional fields as limitations rather than
invented data.

Validation:

```text
python scripts/validate_h2_package_registry_fixture_runtime.py
python scripts/normalize_h2_package_fixture.py --source-id crates_io --input examples/connectors/h2_package_registries/fixtures/crates_io/typical_record.json --check
python scripts/replay_h2_package_fixtures.py --check
python scripts/summarize_h2_package_fixture_outputs.py --input examples/connectors/h2_package_registries --check
```

