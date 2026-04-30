# Search Usefulness Delta v2

Search Usefulness Delta v2 measures the effect of Search Usefulness Source Expansion v2.

This audit is reporting/governance only. It does not add retrieval behavior, source loaders, live probes, external observations, real binaries, downloads, installers, uploads, hosted search, or production search claims.

Baseline provenance:

- baseline source: `control/audits/search-usefulness-source-expansion-v2/source_expansion_v2_report.json`
- baseline source type: `machine_derived_from_committed_p32_report`
- per-query baseline source: selected-target movement from the P32 report plus current audit expected-status fields
- failure-mode baseline source: unavailable for exact P32 before/after comparison

Current outcome:

- covered: 5
- partial: 40
- source_gap: 10
- capability_gap: 7
- unknown: 2

Recommended next milestone:

1. Source Pack Contract v0
2. Evidence Pack Contract v0
3. Index Pack Contract v0

