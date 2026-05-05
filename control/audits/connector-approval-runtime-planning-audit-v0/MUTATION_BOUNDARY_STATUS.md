# Mutation Boundary Status

For every first-wave connector, current mutation status is disabled:

| connector_id | source_cache_mutated | evidence_ledger_mutated | candidate_index_mutated | public_index_mutated | local_index_mutated | runtime_index_mutated | master_index_mutated |
| --- | --- | --- | --- | --- | --- | --- | --- |
| internet_archive_metadata | false | false | false | false | false | false | false |
| wayback_cdx_memento | false | false | false | false | false | false | false |
| github_releases | false | false | false | false | false | false | false |
| pypi_metadata | false | false | false | false | false | false | false |
| npm_metadata | false | false | false | false | false | false | false |
| software_heritage | false | false | false | false | false | false | false |

No connector currently mutates source cache, evidence ledger, candidate index,
public index, local index, runtime index, or master index.
