# Search Miss Ledger Contract v0

Status: contract-only.

The v0 boundary is no runtime ledger writes.

This contract defines future search miss ledger entries. It has no runtime
ledger writes, no persistent ledger storage, no telemetry runtime, no public
query logging, and no mutation of query observations, shared result caches,
search needs, probe queues, candidate indexes, local indexes, or the master
index.

## Purpose

`contracts/query/search_miss_ledger_entry.v0.json` describes a privacy-filtered
record for failed, weak, ambiguous, blocked, or incomplete public searches. A
miss entry is not truth, not a search need, not a probe job, not a candidate
record, and not master-index truth.

## Miss Ledger Entry Model

Required sections:

- `query_ref`: normalized query reference, non-reversible query fingerprint,
  raw query retention default `none`, and privacy classification.
- `cache_ref`: optional reference to a future shared result cache entry, with
  no mutation performed in P61.
- `miss_classification`: miss type, severity, confidence, scoped absence flag,
  and `global_absence_claimed: false`.
- `miss_causes`: cause records such as missing public index hit, low-score
  result, source coverage gap, disabled live probe, or capability gap.
- `checked_scope` and `not_checked_scope`: what controlled indexes, source
  families, capabilities, and snapshots were or were not checked.
- `near_misses` and `weak_hits`: summary-only result references and reasons,
  never full raw result payloads.
- `result_summary` and `absence_summary`: hit state, gap/warning/limitation
  counts, scoped absence posture, and limitations.
- `suggested_next_steps`: future-only steps such as create search need, check
  source cache, add evidence pack, run manual observation, or refine query.
- `privacy`, `retention_policy`, and `aggregation_policy`: prohibited data,
  public aggregate posture, and future retention semantics only.
- `no_mutation_guarantees`: hard false fields for master index, local index,
  candidate index, search need creation, probe enqueueing, result cache
  mutation, query observation mutation, telemetry export, and external calls.

## Miss Classification

The miss classification taxonomy is governed by
`contracts/query/search_miss_classification.v0.json`.

Allowed miss types include `no_hits`, `weak_hits`, `near_miss_only`,
`blocked_by_policy`, `source_coverage_gap`, `capability_gap`,
`compatibility_evidence_gap`, `member_access_gap`, `representation_gap`,
`query_interpretation_gap`, `live_probe_disabled`,
`external_baseline_pending`, and `unknown`.

Every v0 miss classification must keep `global_absence_claimed` false. A miss
can be scoped absence only for the checked indexes, sources, capabilities, and
snapshot references.

## Cause, Scope, And Weak Results

Miss causes explain why the current controlled public search path did not
produce a strong result. They can identify source coverage gaps, placeholder
sources, disabled live probes, missing extraction/OCR/member enumeration,
missing compatibility evidence, exact-version gaps, ambiguous queries, or
policy blocks.

Checked scope records `public_index`, `local_index_only`, future candidate or
source-cache slots, checked source families, checked capabilities, and index
snapshot references. Live probes and external calls remain false.

Near-miss and weak-hit summaries contain only result references, title,
source id/family, reason or weakness, optional score, and limitations.

## Scoped Absence

Scoped absence means no verified result was found in the checked scope. It is
not a claim about every possible source or the whole world. The absence summary
must name what was checked, what was not checked, and why not-checked sources or
capabilities remain outside the claim.

## Privacy And Aggregation

Raw query retention default is `none`. Public-safe miss entries must not
contain IP address, account ID, email, phone number, API key, auth token,
password, private key, private path, private URL, private local result
identifier, user-uploaded filename without consent, or unsafe raw query text.

Public aggregate fields may include miss type, cause type, source family,
capability gap, query intent, platform, or artifact type only after privacy
filtering. Raw query aggregation and private identifier aggregation are false.

## Runtime Boundary

P61 does not wire public search routes to a miss ledger. The optional dry-run
helper prints a candidate miss entry to stdout only and writes no files.

Validate examples with:

```bash
python scripts/validate_search_miss_ledger_entry.py --all-examples
python scripts/validate_search_miss_ledger_entry.py --all-examples --json
```

Validate the whole contract pack with:

```bash
python scripts/validate_search_miss_ledger_contract.py
python scripts/validate_search_miss_ledger_contract.py --json
```
