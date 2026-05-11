# H8 Manuals Docs Live Probe Result


H8 manuals/docs/standards live probes are controlled metadata observations. They are not broad search, source sync, document downloads, scraping, crawling, OCR, standards-document access, datasheet access, repair guidance, install guidance, rights clearance, or public truth acceptance.

Current status is fail-closed. The default CLI mode is offline preflight. A future live call requires `--live` and committed source-specific approval for the exact source, request key, endpoint/metadata class, rate limit, timeout, retry policy, cache/no-cache decision, kill switch, output path, review policy, truth policy, no-download/extract policy, and restricted-source posture.

Allowed outputs are live-probe results, normalized metadata records, identity/relation/access/safety candidates, source-cache previews, evidence previews, review seed previews, connector health summaries, coverage/scorecard update previews, and blocked reports. These outputs remain candidate-only and preview-only.

Forbidden behavior includes document/PDF/manual/datasheet/standards/schematic/service-manual downloads, full-text/OCR extraction, IIIF/media fetches, scraping, crawling, browser automation, access-control bypass, restricted/licensed source access, public query fanout, source sync, public/master index mutation, and accepted source/evidence/candidate/document/relation/datasheet/standard/install/repair/access-rights/public truth.

Validation commands include `python scripts/validate_h8_manuals_docs_live_probe.py`, `python scripts/run_h8_manuals_docs_live_probe.py --source-id bitsavers_docs --request-key example_document_metadata --check`, and `python scripts/summarize_h8_manuals_docs_live_probe_outputs.py --input examples/connectors/h8_manuals_docs_standards/live_probe_results --check`.
