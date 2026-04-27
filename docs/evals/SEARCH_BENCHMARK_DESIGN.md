# Search Benchmark Design

Eureka's current benchmark posture starts from the archive-resolution task
corpus under `evals/archive_resolution/`.

## Why This Exists

The benchmark exists to prevent future resolver work from outrunning measurable
product behavior.

Future work on:

- source registry
- resolution runs
- query planner
- ranking
- decomposition
- compatibility
- absence reasoning
- optional AI helpers

should improve or at least preserve benchmark behavior rather than rely on
vague architectural enthusiasm alone.

## Current Corpus

The current task set already covers hard-query families such as:

- platform software search
- vague software identity
- latest-compatible release search
- driver inside bundle
- article inside scan

## Future Metrics

The benchmark should eventually report metrics such as:

- exact-object accuracy
- exact-version accuracy
- false-positive rate
- false-safe rate
- user-cost reduction
- time-to-first-useful-result
- time-to-confidence
- extraction success
- absence-report quality
- lane coverage
- actionability

## Current Status

The eval suite now has two executable guardrails:

- Archive Resolution Eval Runner v0 loads the packet
- it runs Query Planner v0
- it builds or uses Local Index v0 when available
- it falls back to deterministic search when needed
- it records bounded absence reasoning for no-result cases
- Hard Eval Satisfaction Pack v0 maps source-backed member paths,
  representation locators, compatibility evidence, and source-family evidence
  into hard expected-result checks without weakening task definitions
- Old-Platform Result Refinement Pack v0 scores deterministic primary
  candidate shape, expected lanes, and bad-result avoidance for the current
  old-platform hard eval partials without adding production ranking
- More Source Coverage Expansion v1 adds source-backed evidence for the
  remaining old-platform hard partials
- Article/Scan Fixture Pack v0 adds one bounded synthetic article/page/scan
  fixture so the article-inside-scan hard task can be evaluated against
  article-segment, page-range, and OCR-like text evidence without real OCR
- it includes bounded result-lane and user-cost annotations where current
  result records expose them
- it emits stable JSON per-task and suite reports
- Search Usefulness Audit v0 loads a broader 64-query pack under
  `evals/search_usefulness/`
- it records Eureka observations through the same bounded planner/index/search
  path
- it marks Google, Internet Archive metadata search, and Internet Archive
  full-text/OCR search as `pending_manual_observation`
- it aggregates source, planner, index, decomposition, representation,
  compatibility, actionability, and UX failure labels into future-work targets

This is not a full relevance benchmark. It does not score production ranking,
fuzzy retrieval, vector or semantic search, LLM planning, crawling, live source
sync, or production search quality. Current lane/user-cost fields are bounded
Eureka observation details, not proof that final relevance ranking exists. The
current hard archive-resolution packet now reports `satisfied=6`, but that is
satisfaction against tiny fixture-backed checks only. It is not broad corpus
coverage, production ranking, live OCR, or external search comparison.

The usefulness audit is also not an automated Google or Internet Archive
comparison. External baseline observations are placeholders until a human
reviewer records them manually. This keeps the audit focused on reproducible
local Eureka behavior and prevents fabricated external wins or losses.
