# Probe Queue Contract v0

Status: contract-only in P63.

Probe queue items are future work requests derived from privacy-filtered search
needs, miss summaries, result-cache summaries, or query observations. They are
not probe execution, not a runtime worker, not connector execution, not source
cache or evidence ledger mutation, not candidate-index mutation, not
master-index truth, and not telemetry.

P63 defines schema, examples, validation, docs, and audit evidence only. It
adds no runtime probe queue, no persistent queue, no telemetry, no public query
logging, no execution, no source calls, no live probes, no source cache
mutation, no evidence ledger mutation, no candidate-index mutation, no
local-index mutation, and no master-index mutation.

## Record Shape

`contracts/query/probe_queue_item.v0.json` requires:

- `probe_identity`: non-reversible `sha256` fingerprint, public-safe canonical
  probe label, and normalized probe terms.
- `probe_kind`: kind taxonomy, future execution class, future live-network
  requirement, and approval/operator/human gates.
- `source_policy`: source policy kind, allowed/prohibited source families,
  disabled live-probe flag, and source/rights review requirements.
- `input_refs`: references to query observations, shared result cache entries,
  search miss ledger entries, search need records, and future reviewed inputs.
- `target`: public-safe target kind and optional product/source/evidence hints.
- `priority` and `scheduling`: example/future priority and scheduling policy;
  no real schedule is created.
- `expected_outputs`: future-only output kinds and destination policies.
- `safety_requirements`: required download/install/execute/upload/path/token/URL
  prohibitions plus future rate-limit, timeout, backoff, and circuit-breaker
  requirements where a future live-network probe would be needed.
- `privacy`, `retention_policy`, `aggregation_policy`, `limitations`,
  `no_execution_guarantees`, and `no_mutation_guarantees`.

## Probe Kind Taxonomy

P63 defines these probe kinds:

- `manual_observation`
- `source_cache_refresh`
- `source_metadata_probe`
- `source_identifier_probe`
- `wayback_availability_probe`
- `package_metadata_probe`
- `repository_release_probe`
- `deep_container_extraction`
- `member_enumeration`
- `OCR_or_scan_extraction`
- `compatibility_evidence_request`
- `source_pack_request`
- `evidence_pack_request`
- `index_pack_request`
- `query_parser_improvement_request`
- `unknown`

Execution classes are future-only: `human_operated_future`,
`scheduled_worker_future`, `approval_gated_live_probe_future`,
`local_offline_extraction_future`, `connector_runtime_future`, and
`no_execution_v0`.

If `live_network_required_future` is true, `approval_required` must be true.
The P63 examples keep `source_policy.live_probe_enabled` false.

## Source Policy And Approval

Allowed source policy kinds are `no_source_call`, `manual_only`,
`fixture_only`, `source_cache_only_future`,
`live_metadata_probe_after_approval`,
`local_offline_extraction_after_approval`, and `unknown`.

Future live-network probe work requires source policy review, operator setup,
rate limits, timeout, retry backoff, circuit breaker controls, and cache before
public reuse. P63 performs none of that work.

## Expected Output Model

Expected output kinds are future-only planning categories such as
`manual_observation`, `source_cache_record`, `evidence_record_candidate`,
`candidate_index_record`, `absence_evidence`, `source_pack_request`,
`evidence_pack_request`, `extraction_report`, and `query_parser_issue`.

Output destination policies are `no_output_v0`, `source_cache_future`,
`evidence_ledger_future`, `candidate_index_future`, `manual_report_future`, or
`contribution_candidate_future`. These names describe future review paths and do
not mutate any store in P63.

## Candidate Index Relationship

P64 adds a candidate index contract-only layer for provisional review records.
Probe queue items may later point toward candidate review through future-only
expected output labels, but P63 does not create candidate index records, does
not execute probes, and does not mutate source cache, evidence ledger, public
search, or the master index.

## Privacy

Raw query retention default is `none`. Public-safe probe queue items must not
contain raw private queries, IP addresses, account IDs, private paths, sensitive
tokens, private URLs, user identifiers, local result IDs, executable payloads,
or raw copyrighted payload dumps.

Aggregate publication is future-only and must exclude raw queries and private
identifiers.

## Runtime Boundary

The optional dry-run helper emits JSON to stdout only. Public search routes do
not write probe queue items. Future runtime integration requires separate
privacy/poisoning guards, source policy, approval evidence, rate limits,
timeouts, circuit breakers, source cache/evidence ledger contracts, candidate
contracts, and no-mutation review.

## P65 Candidate Promotion Policy Relationship

P65 adds Candidate Promotion Policy v0 as contract-only governance. Candidate promotion policy is not promotion runtime; candidate confidence is not truth; automatic promotion is forbidden; destructive merge is forbidden; future promotion assessment requires evidence, provenance, source policy, privacy, rights, risk, conflict, human, policy, and operator gates. No candidate, source, evidence, public index, local index, or master-index state is mutated.
