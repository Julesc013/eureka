# Track A Validation

Track A validation proves that Eureka's representation contracts, semantic
parity policies, route/view/representation matrix, canonical view-model
policies, examples, and policy index are internally consistent before renderer
or runtime refactors begin.

## Primary Command

```powershell
python scripts/validate_track_a_contracts.py
```

This command runs the Track A validators in deterministic order:

- `scripts/validate_representation_contracts.py`
- `scripts/validate_semantic_renderer_parity.py`
- `scripts/validate_route_view_representation_matrix.py`
- `scripts/validate_search_page_view_model.py`
- `scripts/validate_object_page_view_model.py`
- `scripts/validate_source_page_view_model.py`
- `scripts/validate_need_candidate_page_view_models.py`
- `scripts/validate_pack_task_review_page_view_models.py`
- `scripts/validate_download_evidence_absence_compare_view_models.py`
- `scripts/validate_view_model_policy_index.py`

It returns nonzero if any constituent validator fails. It does not mutate
files, regenerate site artifacts, call networks, call models, call providers,
or use external APIs.

## Focused Index Command

```powershell
python scripts/validate_view_model_policy_index.py
```

This validates `control/inventory/publication/view_model_policy_index.json`
and the compact example index under `examples/view_models/policy_index/`.

## Static SearchPage Projection Audit

```powershell
python scripts/audit_static_searchpage_projection.py --check
```

This read-only audit checks current static SearchPage-related publication
artifacts against `SearchPageView` semantics without regenerating `site/dist`.

## What This Protects

- Every canonical Track A view model has a schema, policy inventory, examples,
  documentation, validator, and tests.
- Referenced route families exist in the route/view/representation matrix.
- Referenced representation profiles exist in the representation inventory.
- Referenced semantic parity policies exist.
- Examples remain public-safe and validate through their focused validators.
- Future/deferred concepts remain future/deferred and are not presented as
  active runtime.

## No-Goals

Track A validation does not start runtime services, generate site output,
enable hosted behavior, activate public routes, perform live probes, call
source connectors, import packs, run review/moderation workflows, create native
projects, download files, upload files, mutate the master index, or change
public search semantics.

## When To Run

Run the primary command before renderer refactors, view-model runtime binding,
snapshot/relay/native projection work, or Track B candidate/source/evidence
workflow work. For a full repo lane, also run:

```powershell
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```
