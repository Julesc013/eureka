# Content, Resource, Source, and Eval Coverage Audit

## Reviewed Assets

- Source Registry v0 records under `control/inventory/sources/`
- archive-resolution eval packet under `evals/archive_resolution/`
- Search Usefulness Audit v0 query pack under `evals/search_usefulness/`
- Python oracle golden fixture pack under `tests/parity/golden/python_oracle/v0/`
- public-alpha route inventory under `control/inventory/public_alpha_routes.json`
- Rust migration and parity docs under `docs/architecture/` and
  `tests/parity/`

## Current Coverage

- Source records: 6
- Implemented local source families: synthetic fixtures and recorded GitHub
  Releases fixtures
- Placeholder source families: Internet Archive, Wayback/Memento, Software
  Heritage, local files
- Archive-resolution hard tasks: 6
- Search-usefulness queries: 64
- Public-alpha route inventory entries: 89

## Main Coverage Findings

1. Source coverage is the dominant limitation. The search-usefulness audit
   currently reports 43 `source_gap` queries and 13 `capability_gap` queries.
2. Latest-compatible release, legacy driver, manual/documentation,
   article-inside-scan, dead-link, and vague-identity queries need recorded
   fixture families before retrieval semantics can be judged fairly.
3. The current Local Index v0 indexes current bounded records well enough for
   local fixture sanity checks, but the indexed corpus is too small for broad
   archive-resolution usefulness.
4. External Google and Internet Archive observations remain pending manual
   evidence and must not be fabricated.
5. Python oracle goldens are healthy as a parity baseline, but only the Rust
   source-registry candidate has an implemented Rust behavior seam.

## Coverage Strengths

- The repo now has both hard small evals and a broader usefulness query pack.
- Capability gaps are represented directly rather than hidden.
- The source registry distinguishes placeholder source families from
  implemented fixture-backed families.
- Public-alpha route coverage is explicit enough to support supervised
  rehearsal checks.

## Coverage Risks

- Source expansion could accidentally become live crawling if not kept to
  recorded fixtures first.
- Planner expansion could claim semantic understanding without hard tests.
- Archive/member/article queries can look like search failures when they are
  actually decomposition, OCR, representation, or source-coverage gaps.

See `SOURCE_GAP_MATRIX.md` and `RESOURCE_BACKLOG.json` for actionable next
steps.

