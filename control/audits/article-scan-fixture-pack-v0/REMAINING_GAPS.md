# Remaining Gaps

- The article fixture is synthetic and recorded. It is not real OCR output and
  is not a claim that Eureka can process arbitrary scans.
- There is no PDF parser, image parser, OCR engine, page-image ingestion, or
  live source acquisition.
- The source covers one tiny article/page/segment example only.
- Search Usefulness Audit still reports source coverage as the dominant failure
  mode, with `source_coverage_gap=49`.
- Compatibility, planner, representation, decomposition, member-access,
  identity, ranking, and surface gaps remain visible in the broader audit.
- External Google and Internet Archive baselines now have governed manual
  observation slots plus a prioritized Batch 0, but no observed external
  baseline records are committed.

Recommended next milestone: `Manual Observation Batch 0 Execution`.

Manual Observation Entry Helper v0 is now implemented as the Codex-only local
tooling step before execution. It lists Batch 0 slots, creates fillable pending
files, validates one file or all files, and reports progress without performing
observations, scraping, URL fetching, browser automation, or fabricated
baseline recording. The execution milestone still requires a human operator.

Rationale: archive-resolution hard evals are now all satisfied under current
strict fixture-backed checks, the manual observation protocol exists, and
Batch 0 now names the first 13-query/39-slot subset. The next useful step is
for a human operator to manually fill selected Batch 0 records without scraping
or fabricating baselines. If the team prefers implementation over measurement,
`More Source Coverage Expansion v2` is the strongest alternative because source
gaps remain dominant.
