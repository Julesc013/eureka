# Internet Archive Metadata Connector

IA-BUNDLE-01 adds the fixture-only foundation for an Internet Archive metadata
connector. It defines source policy, endpoint posture, operator gates,
normalization, source-cache preview mapping, and evidence-candidate preview
mapping.

The connector foundation is not a live connector. It does not call Internet
Archive, fetch files, scrape pages, crawl, perform public-query fanout, mutate
source cache, accept evidence, or update public/master indexes.

## Current Scope

- committed public-safe fixtures only
- metadata-only normalization
- source observation records only
- source-cache candidate previews only
- evidence candidate previews only
- review required before downstream truth use

## Why IA First

Internet Archive metadata is a useful first connector pattern because it can
exercise source policy, fixture replay, file-list metadata, provenance, and
review gates without needing downloads or public search behavior changes.

## Boundary

IA metadata may become source-cache previews, evidence candidate previews,
candidate records, review queue inputs, pack drafts, and quality-delta inputs.
It must not become accepted evidence, public truth, rights clearance, malware
safety, verified installability, public-index mutation, or master-index
mutation.

## Validation

- `python scripts/validate_ia_metadata_connector_foundation.py`
- `python scripts/normalize_ia_metadata_fixture.py --input examples/connectors/internet_archive/fixtures/software_item_metadata.json --check`
