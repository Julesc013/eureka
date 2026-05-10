# H7 Library Research Live Probe Model

H7 library, cultural, book, research, repository, dataset, and patent live probes are bounded metadata observations. They are not source sync, harvest jobs, broad search, downloads, scraping, crawling, rights review, legal review, availability proof, or production coverage proof.

Default operation is offline preflight. A live source call requires `--live` and committed source-specific approval for the exact request key, metadata class, rate posture, cache posture, kill switch, auth posture, and output path. The committed H7-BUNDLE-03 policies contain no operator approval, so examples and CLI checks emit blocked or fixture-equivalent preview outputs with `network_used: false`.

Allowed outputs are live-probe result envelopes, normalized metadata records, bibliographic/research/dataset/cultural/patent/citation/access candidates, source-cache previews, evidence previews, review seed previews, connector health summaries, and summaries. All remain candidates or previews.

Forbidden behavior includes OAI-PMH harvests, bulk API sync, DOI/ISBN/library/research/patent queries without exact approval, full-text/PDF/book/article/dataset/patent/IIIF/media downloads, scraping, crawling, browser automation, restricted-source access, bypass, source cache writes, evidence ledger writes, review queue writes, public index mutation, master index mutation, and truth acceptance.

Validation:

```bash
python scripts/validate_h7_library_research_live_probe.py
python scripts/run_h7_library_research_live_probe.py --source-id openalex --request-key example_work_metadata --check
python scripts/summarize_h7_library_research_live_probe_outputs.py --input examples/connectors/h7_library_research/live_probe_results --check
```
