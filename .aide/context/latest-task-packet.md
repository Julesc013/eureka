# AIDE Latest Task Packet

## PHASE

H8-BUNDLE-02 - Manuals/docs/standards fixture runtimes and normalizers. HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## GOAL

Add fixture-only manuals, technical documentation, datasheets, service manuals, schematics, install guides, compatibility notes, and standards normalizers and replayable connector outputs for H8.

## WHY

H8-BUNDLE-01 added policy-pack-only source governance for manuals/docs/standards sources. H8-BUNDLE-02 proves committed synthetic/repo-local fixture parsing, normalization, candidate mapping, replay output, and boundary enforcement without enabling live source access.

## CONTEXT_REFS

- `.aide/memory/project-state.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `control/audits/h8-bundle-01-manuals-docs-standards-policy-packs-v0/`
- `control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/`
- `control/inventory/source_packs/h8_manuals_docs_standards_sources.json`
- `control/inventory/connectors/`
- `contracts/connectors/`
- `runtime/connectors/h8_manuals_docs_standards/`
- `examples/connectors/h8_manuals_docs_standards/`
- `scripts/normalize_h8_manuals_docs_fixture.py`
- `scripts/replay_h8_manuals_docs_fixtures.py`
- `scripts/summarize_h8_manuals_docs_fixture_outputs.py`
- `scripts/validate_h8_manuals_docs_standards_fixture_runtime.py`
- `tests/connectors/`
- `tests/operations/`
- `AGENTS.md`

## ALLOWED_PATHS

- `.aide/context/`
- `.aide/queue/`
- `.aide/reports/`
- `contracts/connectors/h8_`
- `control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/`
- `control/inventory/connectors/h8_`
- `runtime/connectors/h8_manuals_docs_standards/`
- `examples/connectors/h8_manuals_docs_standards/`
- `docs/reference/H8_`
- `docs/architecture/H8_`
- `docs/operations/H8_MANUALS_DOCS_`
- `scripts/normalize_h8_manuals_docs_fixture.py`
- `scripts/replay_h8_manuals_docs_fixtures.py`
- `scripts/summarize_h8_manuals_docs_fixture_outputs.py`
- `scripts/validate_h8_manuals_docs_standards_fixture_runtime.py`
- `tests/connectors/test_h8_`
- `tests/operations/test_h8_manuals_docs_fixture_scripts.py`

## FORBIDDEN_PATHS

- Web build output roots.
- Public index and master index roots.
- Local private-state, cache, provider secret, credential, cookie, or account/session roots.
- Document, PDF, manual, datasheet, standard, schematic, OCR, media, archive, or download roots.
- Restricted-source mirrors or harvested source payload roots.
- AIDE-only broad product boundary patterns remain forbidden outside the explicit H8 task allowlist: `runtime/**`, `contracts/**`, `surfaces/**`, `site/**`, `native/**`, `crates/**`, `connectors/**`, `packaging/**`, `third_party/**`.

## IMPLEMENTATION

- Add H8 fixture, normalized record, candidate, and replay-result contracts.
- Add standard-library-only H8 fixture loader, common normalizer, candidate builders, replay helper, and one source wrapper per H8 source.
- Add explicit fixture runtime, normalization, mapping, output, path, truth, source-cache, evidence, and no-download/extract policies.
- Add synthetic public-safe fixtures for all 18 sources with minimal, identity, relation, datasheet, standard, install, repair/safety, access-rights, and policy-blocked cases.
- Add normalized examples, replay result examples, candidate examples, docs, audit evidence, CLI scripts, validator, and tests.
- Keep all outputs as candidates/previews only.

## VALIDATION

- `git status --short`
- `git diff --check`
- JSON syntax checks for H8-BUNDLE-02 contracts, policies, and report.
- `python scripts/validate_h8_manuals_docs_standards_fixture_runtime.py`
- `python scripts/normalize_h8_manuals_docs_fixture.py --source-id bitsavers_docs --input examples/connectors/h8_manuals_docs_standards/fixtures/bitsavers_docs/document_identity_record.json --check`
- `python scripts/replay_h8_manuals_docs_fixtures.py --check`
- `python scripts/summarize_h8_manuals_docs_fixture_outputs.py --input examples/connectors/h8_manuals_docs_standards --check`
- H8 targeted unit tests.
- Existing H8/H7/H6/H5/H4/H3/H2/H1/H0/core validators when present.
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- `py -3 .aide/scripts/aide_lite.py adapter validate`

## EVIDENCE

- H8-BUNDLE-02 audit pack under `control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/`.
- H8 fixtures under `examples/connectors/h8_manuals_docs_standards/fixtures/`.
- H8 normalized examples under `examples/connectors/h8_manuals_docs_standards/normalized/`.
- H8 replay results under `examples/connectors/h8_manuals_docs_standards/replay_results/`.
- H8 candidate examples under `examples/connectors/h8_manuals_docs_standards/identity/`.
- H8-BUNDLE-03 routing evidence may be added under `.aide/queue/` after H8-BUNDLE-02 validation.

## NON_GOALS

- No live source calls, external calls, network calls, API/catalog queries, source sync, live probes, scraping, crawling, or browser automation.
- No document, PDF, manual, datasheet, standard, schematic, OCR, media, archive, or attachment fetch/download/extraction.
- No restricted/licensed source access, account/session use, access-control bypass, or repair/install/electrical action authorization.
- No evidence, candidate, document, relation, datasheet/device, standards, install, repair/safety, access-rights, source, pack, public, or master truth acceptance.
- Complete H8 fixture runtime without changing Eureka product behavior: no public search behavior changes, hosting, uploads, accounts, telemetry, public index mutation, or master index mutation.

## TOKEN_ESTIMATE

approx_tokens: 1600

## ACCEPTANCE

- H8 fixture contracts, policies, normalizers, scripts, examples, docs, audit pack, and tests exist.
- Required fixtures, normalized outputs, replay outputs, and candidate examples exist for all H8 sources.
- Validators and tests pass.
- No live/source-sync/query/fetch/download/extract/scrape/crawl/bypass behavior is enabled.
- No public/master index mutation occurs.
- No source/evidence/candidate/document/manual-artifact/datasheet/standard/install/repair/access-rights/public truth is accepted.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED`, `VALIDATION`, `H8_SCOPE`, `RISKS`, and `NEXT TASK`.
