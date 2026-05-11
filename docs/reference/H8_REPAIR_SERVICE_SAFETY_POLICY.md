# H8 Repair Service Safety Policy

H8 defines policy-pack-only source families for manuals, technical documentation, datasheets, service manuals, schematics, install guides, compatibility notes, and standards metadata.

These sources are metadata and evidence-candidate sources, not public truth. Technical-document identity, manual-artifact relations, datasheet/device identity, standards/specification identity, install requirements, repair/service/safety notes, and access-rights metadata all require review before any persistence or public use.

Current boundaries: no live calls, API/catalog queries, document fetches, PDF/manual/datasheet/standards downloads, full-text/OCR extraction, IIIF/media fetches, scraping, crawling, browser automation, bypass, restricted-source access, source sync, public/master index mutation, action execution, rights clearance, compatibility/installability/repair/electrical-safety claims, or production readiness claims.

H8 reuses H0-H7 Source OS patterns: policy packs come first, fixture replay comes next, and any future metadata-only live probes must pass explicit approval gates. H8-BUNDLE-02 is expected to add fixture-only normalizers; H8-BUNDLE-03 is expected to add approval-gated metadata-only live-probe envelopes.

Validation commands include `python scripts/validate_h8_manuals_docs_standards_policy_packs.py`, `python scripts/summarize_h8_manuals_docs_standards_sources.py --check`, targeted H8 unit tests, full unittest discovery, and `python scripts/check_architecture_boundaries.py`.
