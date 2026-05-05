# Search Result Explanation Runtime Plan

P106 plans a future bounded, read-only, public-safe explanation runtime for
Eureka public search results. It does not implement that runtime.

## Readiness

Current readiness is `ready_for_local_dry_run_runtime_after_operator_approval`.
Hosted staging remains blocked by unverified hosted deployment evidence.

## Gates

- Explanation contract: present in `contracts/search/`, with examples and
  validators.
- Public search/result-card gate: local `local_index_only` runtime and governed
  result cards exist.
- Public index/result envelope gate: `data/public_index/` has committed
  public-safe artifacts and result envelopes.
- Dependency gates: ranking, merge, identity, pages, source cache, evidence
  ledger, and extraction remain contract-only, planning-only, or dry-run-only as
  appropriate.
- Privacy/redaction/copy policy: no private query, path, URL, secret, IP,
  account, session, telemetry, or local fingerprint may appear.
- Model/AI/hidden-score boundary: no model calls, AI answers, hidden scores,
  hidden suppression, result suppression, telemetry, user profile, ad, or secret
  scoring signal.

## Future Runtime Shape

A future runtime may accept only a bounded public search result envelope and
public-safe result-card/index fields. It may assemble components for query
interpretation, match/recall, source coverage, evidence/provenance, identity,
ranking relationship, compatibility, gaps, action safety, rights/risk, and
limitations.

Outputs may later include structured API fields, static/lite/text summaries, and
escaped HTML. No output may fetch assets, expose hidden scores, or enable
download/install/execute controls.

## Failure Model

If explanation fails, public search must still work. If privacy checks fail,
omit or redact explanation. If ranking/source/evidence detail is missing, say so
without exposing scores or private data. An operator kill switch must disable
explanations.

## Validation

Run:

```powershell
python scripts/validate_search_result_explanation_runtime_plan.py
python scripts/validate_search_result_explanation_runtime_plan.py --json
```

These validators are stdlib-only and perform no network calls, model calls,
runtime explanation generation, public-search mutation, source/evidence reads,
telemetry, or mutation.

## Next Steps

Recommended next branch: `P107 Public Search Ranking Local Dry-Run Runtime v0
only after eval gate approval`.

