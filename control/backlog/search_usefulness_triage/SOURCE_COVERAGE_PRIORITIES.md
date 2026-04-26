# Source Coverage Priorities

Source coverage dominates current usefulness failures. Search Usefulness Audit v0 reports `source_coverage_gap=49`, and 43 of 64 queries currently land in `source_gap`.

## Current Active Sources

Current active or fixture-backed source families:

1. synthetic fixtures
2. recorded GitHub Releases fixtures

These are enough for deterministic sanity checks, source registry validation, Python-oracle goldens, and a few covered queries. They are not enough for old-platform software, drivers, manuals, scans, support media, or dead-link workflows.

## Placeholder/Future Sources

Current placeholder or future source families:

- Internet Archive
- Wayback/Memento
- Software Heritage
- local files

These must not be described as implemented connectors. They are planning anchors until a later milestone promotes recorded fixture behavior with tests.

## Priority Order

1. Source Coverage and Capability Model v0
2. Internet Archive recorded metadata + item-file fixtures
3. Local bundle fixture corpus
4. Wayback/Memento recorded fixture
5. Software Heritage recorded fixture
6. package ecosystem fixtures later
7. live source probes later

Status update: Source Coverage and Capability Model v0 is implemented as
bounded registry metadata and public projection. The next source work should be
Real Source Coverage Pack v0, starting with recorded Internet Archive
metadata/item-file fixtures and a local bundle fixture corpus. Placeholder
source records remain placeholders.

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
