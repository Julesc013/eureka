# Search Need Record Contract v0

Status: contract-only in P62.

Search need records are the future durable unit for unresolved public search
needs: people are looking for a thing, but current public_index/local_index_only
evidence is weak, missing, ambiguous, or incomplete. A search need record is not
a result, not a miss ledger entry, not a probe job, not a candidate-index
record, not accepted source evidence, not a demand dashboard row, and not
master-index truth.

P62 defines schema, examples, validation, docs, and audit evidence only. It
adds no runtime need store, no persistent search need storage, no telemetry, no
public query logging, no demand-count runtime, no probe enqueueing, no
candidate-index mutation, no result-cache mutation, no miss-ledger mutation, no
local-index mutation, and no master-index mutation.

P63 adds the probe queue contract as contract-only future planning. Search need
records may be referenced by future probe queue items, but P63 does not make
search needs create queue records, execute probes, mutate source cache, mutate
evidence ledger, mutate candidate index, or call external sources.

## Record Shape

`contracts/query/search_need_record.v0.json` requires:

- `need_identity`: non-reversible `sha256` fingerprint, canonical public-safe
  label, normalized need terms, disambiguation terms, equivalence keys, and
  aliases.
- `target_object`: object kind, product/platform/artifact fields, and a desired
  action that may record disabled download/install intent without enabling
  those actions.
- `originating_inputs`: references to query observations, miss ledger entries,
  shared result cache entries, and future manual/source/evidence inputs. They
  are references only.
- `aggregate_summary`: occurrence and distinct-count fields for future
  aggregation. P62 examples use `single_example` and do not claim public demand.
- `source_and_capability_gaps`: source coverage, compatibility evidence,
  member access, representation, source-cache, OCR, deep extraction, and other
  gaps.
- `checked_scope` and `not_checked_scope`: the evidence boundary that keeps
  search needs scoped to checked indexes, sources, capabilities, and snapshots.
- `evidence_and_result_context`: summary references only, not accepted truth.
- `suggested_next_steps`: future-only steps such as manual observation,
  reviewed packs, approved probes, or candidate review.
- `priority`: example/future priority classes with `demand_count_claimed:
  false` in P62.
- `privacy`, `retention_policy`, `aggregation_policy`, `limitations`, and
  `no_mutation_guarantees`.

## Need Identity

The need fingerprint model is non-reversible:

- `algorithm`: `sha256`
- `normalized_basis`: public-safe canonical label and target/gap terms
- `value`: lowercase SHA-256 hex
- `reversible`: `false`
- `salt_policy`: `unsalted_public_aggregate`,
  `deployment_secret_salted_future`, or `local_private_salted_future`

Fingerprints must not include raw private query text, IP addresses, account
identifiers, private paths, sensitive tokens, private URLs, or local result IDs.

## Target Object Model

Allowed object kinds include `software`, `software_version`, `driver`,
`manual_or_documentation`, `source_code_release`, `package_metadata`,
`web_capture`, `article_or_scan_segment`, `file_inside_container`,
`compatibility_evidence`, `source_identity`, and `unknown`.

Allowed desired actions include `inspect`, `compare`, `cite`, `preserve`,
`locate_download_disabled`, `install_intent_detected_but_disabled`,
`emulate_intent_detected_but_disabled`, and `unknown`. The disabled action
values are descriptive only and do not enable download, install, execute, or
emulation behavior.

## Aggregation Model

Search needs may later aggregate privacy-filtered misses, weak hits, near
misses, and unresolved intents. P62 does not aggregate runtime data. Example
records keep:

- `occurrence_count`: `1`
- `demand_classification`: `single_example`
- `priority.demand_count_claimed`: `false`

Future aggregation must keep raw query aggregation disabled and private
identifier aggregation disabled.

## Source And Capability Gap Model

Gap types include `source_coverage_gap`, `capability_gap`,
`compatibility_evidence_gap`, `member_access_gap`, `representation_gap`,
`query_interpretation_gap`, `live_probe_disabled`,
`external_baseline_pending`, `deep_extraction_missing`, `OCR_missing`,
`source_cache_missing`, and `unknown`.

Suggested resolutions are future-only and do not perform work in P62.

## Privacy

Raw query retention default is `none`. Public-safe records must not contain raw
private queries, IP addresses, account IDs, private paths, sensitive tokens,
private URLs, user identifiers, local result IDs, executable payloads, or raw
copyrighted payload dumps.

Search need records are scoped and reviewable. They are not proof outside the
checked public-index, source-family, capability, and snapshot scope.

## Runtime Boundary

P62 does not wire public search routes to write search need records. The
optional dry-run helper emits JSON to stdout only. Future runtime integration
requires a separate privacy and poisoning guard, storage contract, operator
policy, and no-mutation review.

Probe queue integration remains future-only and approval-gated. A search need
record is still not a probe job, not evidence, not a candidate record, and not
master-index truth.

## Candidate Index Relationship

P64 defines the candidate index contract as a future provisional record layer.
Search needs may later guide candidate creation through reviewed probe,
manual-observation, pack, or source-cache outputs, but P62 records still do not
create candidates, promote candidates, mutate source cache, mutate evidence
ledger, inject candidates into public search, or mutate the master index.
