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
- External Google and Internet Archive baselines remain pending manual
  observation.

Recommended next milestone: `Manual External Baseline Observation Pack v0`.

Rationale: archive-resolution hard evals are now all satisfied under current
strict fixture-backed checks. The next useful step is to record manual external
observations for comparison without scraping or fabricating baselines. If the
team prefers implementation over measurement, `More Source Coverage Expansion
v2` is the strongest alternative because source gaps remain dominant.

