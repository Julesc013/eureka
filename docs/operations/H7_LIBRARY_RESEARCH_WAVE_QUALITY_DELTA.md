# H7 Library Research Wave Quality Delta

H7 review integration is an offline wave-level rehearsal for library, cultural, book, research, repository, dataset, and patent metadata sources.

It consumes committed fixture replay outputs and blocked or approved metadata-only live-probe reports. It creates candidate review seeds, source-cache and evidence previews, candidate promotion dry-run previews, coverage and scorecard preview updates, source-pack update previews, quality deltas, postmortems, and next-phase recommendations.

It does not enable live calls, OAI-PMH harvests, DOI/ISBN/library/research/patent API queries, full-text/PDF/book/article/dataset/patent/IIIF/media fetches, scraping, crawling, bypass, restricted-source access, source sync, public/master index mutation, or truth acceptance.

Bibliographic identity, research work identity, dataset identity, cultural object identity, patent identity, citation relation, and access/rights/availability outputs remain candidates or previews only. They are not bibliographic completeness, citation correctness, DOI/ISBN/DataCite truth, dataset validity, rights clearance, open-access truth, patent validity, full-text availability, malware safety, privacy safety, verified availability, or production coverage proof.

H7 routes to H8 when artifacts are coherent enough to begin policy-pack-only work for manuals, technical docs, datasheets, and standards. J1 risky actions, K semantic/AI, and L wider clients remain deferred unless their gates are explicitly opened.

Validation:

- `python scripts/validate_h7_library_research_review_quality_audit.py`
- `python scripts/integrate_h7_library_research_review.py --input-dir examples/connectors/h7_library_research/replay_results --check`
- `python scripts/summarize_h7_library_research_quality_delta.py --input-dir examples/connectors/h7_library_research/review_integration --check`
- `python scripts/audit_h7_library_research_wave.py --check`
