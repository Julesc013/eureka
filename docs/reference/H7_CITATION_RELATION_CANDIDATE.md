# H7 Citation Relation Candidate


H7-BUNDLE-02 is fixture-runtime work for 30 library, cultural, book, research, repository, dataset, and patent metadata sources.

It reads committed synthetic fixtures, normalizes metadata shape, and emits candidate-only previews for bibliographic identity, research work identity, dataset identity, cultural object identity, patent identity, citation relations, access/rights/availability, source-cache mapping, and evidence mapping.

It does not perform live source calls, API queries, OAI-PMH harvesting, DOI/ISBN/patent queries, full-text fetches, PDF/book/article/dataset/patent downloads, IIIF/media fetches, scraping, crawling, browser automation, bypass, restricted-source access, source sync, or index mutation.

Every output remains a candidate or preview. It is not accepted source truth, accepted evidence, accepted candidate truth, bibliographic truth, research work truth, dataset truth, cultural object truth, patent truth, citation truth, access-rights truth, rights clearance, open-access truth, privacy safety, malware safety, verified availability, or production readiness.


    ## Model

    The runtime keeps the H7-BUNDLE-01 policy-pack boundary intact. Source-specific modules delegate to a shared normalizer, while helper modules build candidate previews with explicit false truth and product boundaries.

    ## Outputs

    The allowed outputs are normalized library/research records, identity/relation/access candidates, source-cache candidate previews, evidence candidate previews, connector output envelopes, replay results, scorecard preview updates, and coverage preview updates.


## No-Goals

- No live probes, source sync, public-query fanout, harvesting, API queries, downloads, scraping, crawling, bypass, restricted-source access, source cache writes, evidence ledger writes, public index mutation, or master index mutation.
- No claim of completeness, correctness, legal status, rights clearance, open-access truth, availability, safety, authenticity, or production coverage.



## Validation

- `python scripts/validate_h7_library_research_fixture_runtime.py`
- `python scripts/normalize_h7_library_research_fixture.py --source-id openalex --input examples/connectors/h7_library_research/fixtures/openalex/identity_record.json --check`
- `python scripts/replay_h7_library_research_fixtures.py --check`
- `python scripts/summarize_h7_library_research_fixture_outputs.py --input examples/connectors/h7_library_research --check`
