# Source Coverage Status

| Source area | Evidence | Classification | Notes |
|---|---|---|---|
| Source registry | `control/inventory/sources/*.source.json` | `implemented_runtime` | 15 records load and project through local runtime surfaces. |
| Synthetic/local fixtures | 2 active fixture sources | `fixture_only` | Synthetic and local bundle fixtures. |
| Recorded fixture sources | 9 active recorded-fixture sources | `fixture_only` | IA, GitHub Releases, article scan, Wayback/Memento, Software Heritage, SourceForge, package registry, manuals, review descriptions. |
| Placeholder sources | 3 placeholders | `contract_only` | IA, Wayback/Memento, Software Heritage placeholders remain non-live. |
| Local private future | 1 local-files placeholder | `deferred` | No arbitrary local ingestion. |
| Live source support | all 15 records report live support false | `deferred` | No live connector execution. |
| Source cache/evidence ledger | live probe policy describes future ledger | `contract_only` | No runtime ledger. |
| Connector health | disabled source policy only | `contract_only` | No quota/health dashboard. |

Important remaining source families are IA metadata, Wayback/CDX/Memento,
GitHub Releases live metadata, PyPI, npm, Software Heritage, Wikidata/Open
Library, retro archive sites, manuals/docs, and reviews/forums/source clues.
