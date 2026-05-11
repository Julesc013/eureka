# AIDE Latest Task Packet

## PHASE

H8-BUNDLE-03 - Manuals/docs/standards approved metadata-only live probes. HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## GOAL

Add the H8 manuals, technical docs, datasheets, service manuals, schematics, install guides, compatibility notes, and standards bounded metadata-only live-probe framework.

## WHY

H8-BUNDLE-01 added policy-pack-only governance and H8-BUNDLE-02 proved fixture-only normalization. H8-BUNDLE-03 adds the fail-closed live boundary: offline preflight by default, blocked reports when approval is missing, exact-request policies for any future bounded metadata-only probe, and candidate/preview outputs only.

## CONTEXT_REFS

- `.aide/memory/project-state.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `control/audits/h8-bundle-01-manuals-docs-standards-policy-packs-v0/`
- `control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/`
- `control/audits/h8-bundle-03-manuals-docs-live-probes-v0/`
- `control/inventory/source_packs/h8_manuals_docs_standards_sources.json`
- `control/inventory/connectors/`
- `contracts/connectors/`
- `runtime/connectors/h8_manuals_docs_standards/`
- `examples/connectors/h8_manuals_docs_standards/`
- `scripts/run_h8_manuals_docs_live_probe.py`
- `scripts/validate_h8_manuals_docs_live_probe.py`
- `scripts/summarize_h8_manuals_docs_live_probe_outputs.py`
- `tests/connectors/test_h8_manuals_docs_live_probe.py`
- `tests/operations/test_h8_manuals_docs_live_probe_scripts.py`
- `AGENTS.md`

## ALLOWED_PATHS

- `.aide/context/`
- `.aide/queue/`
- `.aide/reports/`
- `contracts/connectors/h8_manuals_docs_live_probe_`
- `contracts/connectors/h8_manuals_docs_connector_health_summary.v0.json`
- `control/audits/h8-bundle-03-manuals-docs-live-probes-v0/`
- `control/inventory/connectors/h8_manuals_docs_live_probe_`
- `runtime/connectors/h8_manuals_docs_standards/live_probe_`
- `examples/connectors/h8_manuals_docs_standards/live_probe/`
- `examples/connectors/h8_manuals_docs_standards/live_probe_results/`
- `examples/connectors/h8_manuals_docs_standards/live_probe_outputs/`
- `docs/reference/H8_MANUALS_DOCS_LIVE_PROBE`
- `docs/reference/H8_MANUALS_DOCS_CONNECTOR_HEALTH_SUMMARY.md`
- `docs/architecture/H8_MANUALS_DOCS_LIVE_PROBE_MODEL.md`
- `docs/operations/H8_MANUALS_DOCS_LIVE_PROBE_`
- `scripts/run_h8_manuals_docs_live_probe.py`
- `scripts/validate_h8_manuals_docs_live_probe.py`
- `scripts/summarize_h8_manuals_docs_live_probe_outputs.py`
- `tests/connectors/test_h8_manuals_docs_live_probe.py`
- `tests/operations/test_h8_manuals_docs_live_probe_scripts.py`

## FORBIDDEN_PATHS

- Web build output roots.
- Public index and master index roots.
- Local private-state, cache, provider secret, credential, cookie, or account/session roots.
- Document, PDF, manual, datasheet, standard, schematic, OCR, media, archive, or download roots.
- Restricted-source mirrors or harvested source payload roots.
- AIDE-only broad product boundary patterns remain forbidden outside the explicit H8 live-probe task allowlist: `runtime/**`, `contracts/**`, `surfaces/**`, `site/**`, `native/**`, `crates/**`, `connectors/**`, `packaging/**`, `third_party/**`.

## IMPLEMENTATION

- Add H8 live-probe request/result/output-bundle and connector-health contracts.
- Add fail-closed global, per-source allowed-request, endpoint, rate, cache, kill-switch, output, path, review, truth, no-download/extract, and restricted-source policies.
- Add standard-library-only H8 live-probe common helpers and one source wrapper per H8 source.
- Add CLI, validator, summary script, request/result/output examples, docs, audit evidence, and tests.
- Keep all outputs as candidates/previews only.

## VALIDATION

- `git status --short`
- `git diff --check`
- JSON syntax checks for H8-BUNDLE-03 contracts, policies, and report.
- `python scripts/validate_h8_manuals_docs_live_probe.py`
- `python scripts/run_h8_manuals_docs_live_probe.py --source-id bitsavers_docs --request-key example_document_metadata --check`
- `python scripts/summarize_h8_manuals_docs_live_probe_outputs.py --input examples/connectors/h8_manuals_docs_standards/live_probe_results --check`
- H8 live-probe targeted unit tests.
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

- H8-BUNDLE-03 audit pack under `control/audits/h8-bundle-03-manuals-docs-live-probes-v0/`.
- H8 live-probe requests under `examples/connectors/h8_manuals_docs_standards/live_probe/`.
- H8 live-probe results under `examples/connectors/h8_manuals_docs_standards/live_probe_results/`.
- H8 live-probe output previews under `examples/connectors/h8_manuals_docs_standards/live_probe_outputs/`.
- H8-BUNDLE-04 routing evidence may be added under `.aide/queue/` after H8-BUNDLE-03 validation.

## NON_GOALS

- No broad documentation/manual/standards search, public-query fanout, source sync, scraping, crawling, browser automation, arbitrary URL fetch, or live call without exact committed approval.
- No API/catalog query unless an exact future policy approves bounded metadata-only preflight.
- No document, PDF, manual, datasheet, standard, schematic, OCR, media, archive, service manual, full-text, IIIF, or attachment fetch/download/extraction.
- No restricted/licensed source access, account/session use, access-control bypass, or repair/install/electrical action authorization.
- No evidence, candidate, document, relation, datasheet/device, standards, install, repair/safety, access-rights, source, pack, public, or master truth acceptance.
- Complete H8 live-probe framework without changing Eureka product behavior: no public search behavior changes, hosting, uploads, accounts, telemetry, public index mutation, or master index mutation.

## TOKEN_ESTIMATE

approx_tokens: 1700

## ACCEPTANCE

- H8 live-probe contracts, policies, runtime wrappers, scripts, examples, docs, audit pack, and tests exist.
- Default validation mode is offline and fail-closed.
- No source is live-enabled without committed approval.
- No source sync, broad query/fetch/download/extract/scrape/crawl/bypass behavior is enabled.
- H8 outputs remain candidates/previews only.
- No public/master index mutation occurs.
- No source/evidence/candidate/document/manual-artifact/datasheet/standard/install/repair/access-rights/public truth is accepted.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `LIVE_PROBES`, `H8_SCOPE`, `CHANGED`, `VALIDATION`, `RISKS`, and `NEXT TASK`.
