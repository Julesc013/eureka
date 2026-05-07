# TRACK-A-10 View Model Policy Index v0

Track A-10 adds the governed view-model policy index and cross-contract
validator for the Track A representation and canonical view-model contract
family.

## What Was Added

- ViewModelPolicyIndex schema.
- Publication inventory index enumerating all Track A canonical view model
  families, policy inventories, schemas, docs, examples, validators, tests,
  route families, representation profiles, semantic parity policies, and
  no-claim boundaries.
- Compact public-safe policy-index example.
- Reference documentation and Track A validation operating guide.
- Focused index validator and aggregate Track A validator.
- Unit tests for the index and aggregate validator.
- Task-local audit and AIDE evidence.

## Why The Index Comes Before Renderer And Runtime Refactors

Renderer and runtime work needs a stable discovery layer. The index makes the
view-model family, route family, representation profile, semantic parity,
example, and validator relationship explicit before any implementation can
accidentally split route meaning or soften product-boundary no-claims.

## Cross-Contract Validator

`python scripts/validate_track_a_contracts.py` runs every Track A validator in
deterministic order and fails if any constituent validator fails. It does not
mutate files, regenerate site artifacts, call networks, call models, call
providers, or use external APIs.

## Future Support

The index gives future agents one place to discover the contracts needed for
renderer generation, static projection audits, snapshot and relay substrate,
native-card projections, and Track B handoff work. It also records the
deferred boundaries those future tracks must preserve.

## Deferred

- Static SearchPage projection audit for TRACK-A-11.
- Runtime renderer implementation.
- Runtime view-model binding.
- Snapshot/relay/native runtime substrate.
- Track B source/evidence/candidate/review workflow implementation.
- Hosted public alpha, which remains Track E/operator-gated.

## Validation Commands

- `git status --short`
- `git diff --check`
- `python -m json.tool control/inventory/publication/view_model_policy_index.json`
- `python -m json.tool control/audits/track-a-10-view-model-policy-index-v0/track_a_10_report.json`
- `python scripts/validate_representation_contracts.py`
- `python scripts/validate_semantic_renderer_parity.py`
- `python scripts/validate_route_view_representation_matrix.py`
- `python scripts/validate_search_page_view_model.py`
- `python scripts/validate_object_page_view_model.py`
- `python scripts/validate_source_page_view_model.py`
- `python scripts/validate_need_candidate_page_view_models.py`
- `python scripts/validate_pack_task_review_page_view_models.py`
- `python scripts/validate_download_evidence_absence_compare_view_models.py`
- `python scripts/validate_view_model_policy_index.py`
- `python scripts/validate_track_a_contracts.py`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval list`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- `py -3 .aide/scripts/aide_lite.py adapter validate`

See `validation.md` for observed results.

## No-Goals

- No Eureka product runtime changes.
- No hosted backend claim.
- No deployment, DNS, CNAME, or custom-domain changes.
- No public route activation.
- No live probes, source connectors, source sync runtime, node runtime,
  autonomous runtime, pack import runtime, hosted upload/submission runtime, or
  review/moderation runtime.
- No network, model, or provider calls.
- No downloads, installers, execution, uploads, accounts, or telemetry.
- No raw query telemetry claims.
- No master-index mutation.
- No native project creation.
- No rights-clearance, malware-safety, verified-installability,
  accepted-public-truth, exhaustive-global-search, or automatic-merge/
  deduplication/promotion claims.
- No broad docs rewrite.
- No generated site artifact mutation.
- No existing route runtime or public search semantic change.

## Next Task Recommendation

TRACK-A-11 - Static SearchPage view-model projection audit.
