# Query To Source Action Planner

QUERY-TO-SOURCE-ACTION-PLANNER-00 adds a deterministic planner between raw
public-search queries and review-only candidate source lanes.

The planner does not crawl the web. It turns a query into:

- an intent
- a domain pack
- source-family routes
- source query rewrites
- candidate suppressions
- candidate lane expectations
- source-action plans
- WorkUnits
- review handoff plans
- a public-safe explanation packet

## Runtime Boundary

The public-alpha Archive.org lane may use the planner's
`archive_org_metadata` rewrite for a bounded Archive.org metadata search. This
search covers Archive.org metadata through the approved metadata endpoint; it
does not download files, fetch arbitrary URLs, inspect item members, extract
archives, call model providers, create reviewed truth, or mutate indexes.

All results from that lane remain `needs_review` candidates.

## Intents

- `find_exact_artifact`
- `find_software`
- `find_driver_or_support_media`
- `find_frontier_resolution_media`
- `find_manual_or_document`
- `find_source_release_or_package`
- `identify_provenance`
- `broad_research_need`
- `ambiguous_query`

## Domain Packs

- `legacy_software`
- `driver_support_media`
- `frontier_resolution_media`
- `manuals_docs_scans`
- `package_source_release`
- `web_archive_trace`
- `general_archive_metadata`

## Current Source Routing

`internet_archive_metadata` is the only public-search source family that may
execute now, and only as metadata-only candidate search. Other source families
are plan-only until later operator-scoped work enables their adapters:

- `wayback_cdx_metadata`
- `github_releases_metadata`
- `software_heritage_metadata`
- `package_registry_metadata`
- `open_library_metadata`
- `wikidata_metadata`
- `manual_source_pack`

## Required Examples

The examples under `examples/query_plans/` pin the expected first-pass behavior:

- `New York 1993 D-Theater HD demo tape original source`
- `Windows 7-compatible portable utilities, not Windows 7 ISO`
- `StyleWriter 2500 Mac OS 8 driver`
- `DirectX SDK June 2010 offline installer`
- `best apps`

These examples are not accepted truth. They are routing expectations for
candidate discovery.

## Non-Claims

This planner does not claim production readiness, public launch readiness,
rights clearance, malware safety, compatibility truth, provenance truth, or
full global exhaustiveness. It is a candidate-discovery improvement for the
deferred public alpha.
