# Normalization And Indexing Notes

The expansion adds one generic recorded fixture connector:

```text
runtime/connectors/source_expansion_recorded/
```

Runtime flow:

1. The connector loads committed fixture JSON.
2. Ingest/extract interfaces project fixture records into a generic extracted recorded-source shape.
3. Normalization creates `NormalizedResolutionRecord` objects with source family, representation, evidence, compatibility, optional member lineage, and action hints.
4. Source summary and compatibility evidence maps assign the new source inventory IDs.
5. Local Index v0 indexes normalized records, evidence strings, representation metadata, compatibility evidence, and member fields.
6. Public search result cards expose the records as `local_index_only` fixture-backed cards with blocked download/install/execute/upload actions.

No network path, live API adapter, crawler, scraper, binary payload, user path ingestion, or hosted backend behavior was added.

