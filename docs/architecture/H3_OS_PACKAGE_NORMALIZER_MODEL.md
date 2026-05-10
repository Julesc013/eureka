# H3 OS PACKAGE NORMALIZER MODEL

H3-BUNDLE-02 adds fixture-only OS package archive normalization for thirteen H3 sources. It reads committed synthetic fixtures and emits normalized OS package records, OS package identity candidates, OS/platform compatibility candidates, dependency/conflict/provides candidates, file/hash candidates, source-cache previews, evidence previews, and replay reports.

This is not a live connector runtime. It does not call networks, APIs, models, providers, browsers, or external sources. It does not fetch repository indexes, download packages, invoke package managers, install packages, execute packages, scrape, crawl, mutate source cache, mutate evidence ledgers, mutate review queues, mutate public/master indexes, or accept truth.

All identity, compatibility, dependency, file/hash, source-cache, and evidence outputs are candidates or previews requiring review. Package metadata does not prove installability. Compatibility metadata does not prove compatibility correctness. Dependency/conflict/provides metadata does not prove dependency correctness or environment solvability. License metadata does not prove rights clearance. Hash metadata does not prove malware safety.

Validation commands include `python scripts/validate_h3_os_package_archive_fixture_runtime.py`, `python scripts/replay_h3_os_package_fixtures.py --check`, `python scripts/summarize_h3_os_package_fixture_outputs.py --input examples/connectors/h3_os_package_archives --check`, and the H3 connector/operation unit tests.
