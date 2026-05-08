# Local Source Cache Model

The local source cache model is a future staging model for source observations.
It sits after candidate discovery and before evidence ledger conversion. The
current repository state remains planning-only.

## Model Layers

`source lead or candidate`
: A provisional pointer from SearchNeed, candidate store, WorkUnit dry-run, node
policy evaluation, or manual review.

`source cache draft`
: A future local source observation or normalized metadata record. It is not
accepted evidence and cannot mutate the master index.

`evidence candidate bridge`
: A later reviewed conversion from source-cache output into evidence candidate
shape. This bridge is not implemented by B-13.

`accepted evidence`
: Out of scope for B-13 and blocked until future evidence ledger runtime and
review policy exist.

## Record Shape

Future records should preserve source identity, locator, source policy posture,
metadata summary, provenance, freshness, fixity, privacy posture, rights/risk
posture, limitations, review gates, and truth/product boundary booleans.

Required current truth boundary:

- `source_cache_record_is_public_truth: false`
- `source_cache_record_is_accepted_evidence: false`
- `source_cache_record_can_mutate_master_index: false`
- `source_cache_record_can_claim_rights_clearance: false`
- `source_cache_record_can_claim_malware_safety: false`
- `source_cache_record_can_claim_verified_installability: false`
- `human_review_required_for_downstream_use: true`

## Source Access

Current access is fixture, repo-local, or manual-human only. Metadata probes,
API use, static dumps, and archive/dump access are future modes and require a
source policy decision, operator approval, User-Agent/contact policy, rate and
timeout limits, retry/backoff, cache TTL, kill switch, terms/robots review,
privacy/risk review, and downstream evidence review.

## Storage Boundary

Future private roots are documented by policy but not created by this task.
This prevents planning records from silently becoming local source-cache state.

Planning evidence belongs in audit/readiness docs and policy inventories. It
does not belong in `runtime/`, `contracts/`, generated site assets, publication
inventory, or master-index-related roots.

## Rollout

The rollout phases are:

- `phase_0_planning_only`
- `phase_1_fixture_only_runtime_future`
- `phase_2_source_policy_evaluator_future`
- `phase_3_approved_metadata_probe_future`
- `phase_4_source_cache_to_evidence_bridge_future`
- `phase_5_reviewed_public_index_bridge_future`

B-13 only authorizes phase 0. Later phases require separate reviewed tasks.
