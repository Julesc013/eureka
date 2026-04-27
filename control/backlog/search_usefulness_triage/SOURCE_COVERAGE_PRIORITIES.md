# Source Coverage Priorities

Source coverage remains the largest usefulness pressure even after the first
fixture expansion. After Real Source Coverage Pack v0, Old-Platform Software
Planner Pack v0, Member-Level Synthetic Records v0, Result Lanes + User-Cost
Ranking v0, Compatibility Evidence Pack v0, Search Usefulness Audit Delta v0,
Old-Platform Source Coverage Expansion v0, More Source Coverage Expansion v1,
Article/Scan Fixture Pack v0, and Manual External Baseline Observation Pack
v0, Search Usefulness Audit v0 reports
`covered=5`, `partial=22`, `source_gap=26`, `capability_gap=9`, and
`unknown=2`. The current failure labels still include
`source_coverage_gap=49`, because many query fixtures intentionally keep their
future-work labels until a later delta pack reviews whether those labels should
be retired.

## Current Active Sources

Current active or fixture-backed source families:

1. synthetic fixtures
2. recorded GitHub Releases fixtures
3. recorded Internet Archive-like metadata/file-list fixtures
4. local bundle fixtures
5. article-scan recorded fixtures

These are enough for deterministic sanity checks, source registry validation,
Python-oracle goldens, a few covered queries, and initial source-backed
old-platform/member-discovery probes. They are not enough for broad
old-platform software, drivers, manuals, scans, support media, or dead-link
workflows.

## Placeholder/Future Sources

Current placeholder or future source families:

- Internet Archive
- Wayback/Memento
- Software Heritage
- local files

These must not be described as implemented connectors. They are planning
anchors. Real Source Coverage Pack v0 adds separate active fixture records for
recorded Internet Archive-like data and local bundle fixtures instead of
mutating placeholders into live sources.

## Priority Order

Status update: Old-Platform Source Coverage Expansion v0 is implemented. It
expanded recorded/committed source material for old Windows/Mac utilities,
latest-compatible release notes, driver/support media, and member-level local
bundles before any live source behavior is considered.

1. Source Coverage and Capability Model v0
2. Internet Archive recorded metadata + item-file fixtures (implemented as
   `internet-archive-recorded-fixtures`)
3. Local bundle fixture corpus (implemented as `local-bundle-fixtures`)
4. Wayback/Memento recorded fixture
5. Software Heritage recorded fixture
6. package ecosystem fixtures later
7. live source probes later

Status update: Source Coverage and Capability Model v0, Real Source Coverage
Pack v0, Old-Platform Software Planner Pack v0, Member-Level Synthetic Records
v0, Result Lanes + User-Cost Ranking v0, Compatibility Evidence Pack v0,
Search Usefulness Audit Delta v0, and Old-Platform Source Coverage Expansion
v0 are implemented, and Search Usefulness Audit Delta v1 has recorded the
movement. Hard Eval Satisfaction Pack v0 then moved five source-backed archive
hard tasks to partial. Old-Platform Result Refinement Pack v0 then satisfied
the driver support-CD member task and left four old-platform tasks partial with
explicit evidence/result-shape limits. More Source Coverage Expansion v1 then
added targeted tiny fixture evidence for those four old-platform hard partials,
and archive evals reported `capability_gap=1` and `satisfied=5`. Article/Scan
Fixture Pack v0 then added bounded synthetic article/page/scan fixture
evidence, and archive evals now report `satisfied=6`. Placeholder source
records remain placeholders. Manual External Baseline Observation Pack v0 then
defined manual-only external baseline systems, schema, instructions, and 192
pending observation slots. The next usefulness work should fill a small manual
observation batch before Rust parity or public-alpha rehearsal claims.

## Why Capability Depth Comes Before More Connectors

A source record should say what the source can support:

- discovery metadata
- item/file metadata
- release metadata
- compatibility evidence
- member manifests
- OCR snippets
- direct artifact representations
- dead-link replay evidence
- source snapshots

Without that model, adding connectors would create vague coverage claims. The next task should define source capabilities before adding recorded fixture families.

## Why Recorded Fixtures Come Before Live Crawling

Recorded fixtures are deterministic, inspectable, and testable. Live crawling would make tests unstable, blur provenance, and risk implying global recall. The current repo needs small source-backed truth before it needs breadth.

## Recommended Source Families Next

1. Old-platform release/catalog metadata for Windows 7, XP, 2000, 98, Mac OS 9, and PowerPC OS X.
2. Local support-media/bundle fixture corpus for member-level discovery.
3. Recorded Internet Archive metadata and item-file fixtures for manuals, scans, and file lists.
4. Recorded Wayback/Memento snapshots for dead vendor pages and release notes.
5. Recorded Software Heritage source snapshot fixtures for source-code queries.

## Tests To Add First

- source capability schema validation
- placeholder source honesty guard expansion
- recorded fixture no-network tests
- source capability to query-family mapping tests
- audit status-change justification tests

## Do Not Do

- do not add live crawling
- do not scrape Google or Internet Archive
- do not mark placeholders as implemented
- do not claim global source coverage
- do not make source breadth hide missing member or compatibility evidence
