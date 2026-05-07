# Static SearchPage View-Model Projection Audit

TRACK-A-11 records how the current committed static SearchPage-related
publication artifacts line up with the Track A `SearchPageView` contract.

The audit is read-only. It inspects committed static artifacts and governance
inventories, but it does not regenerate `site/dist`, refactor renderers, alter
public routes, or enable hosted search.

## Audited Artifacts

- `site/dist/search.html`
- `site/dist/lite/search.html`
- `site/dist/text/search.txt`
- `site/dist/files/search.README.txt`
- `site/dist/data/search_handoff.json`

## Commands

Run a human-readable audit:

```text
python scripts/audit_static_searchpage_projection.py
```

Run the boundary check:

```text
python scripts/audit_static_searchpage_projection.py --check
```

Refresh an explicit audit report:

```text
python scripts/audit_static_searchpage_projection.py --json-output control/audits/track-a-11-static-searchpage-view-model-projection-v0/projection_audit_report.json
```

## Interpretation

`status: warn` is acceptable when warnings are noncritical mapping gaps, such as
current artifacts not yet being generated from a canonical `SearchPageView`
fixture. `--check` fails only for critical product-boundary claims such as
hosted backend activation, live probes, downloads, uploads, accounts, telemetry,
rights clearance, malware safety, exhaustive global search, or automatic
promotion.

## Deferred Refactor

The recommended next task is `TRACK-A-12 - Static SearchPage projection fixture
and generator plan`. That work should create a canonical fixture, project it
into the static representations, compare generated output against current
artifacts, and preserve no-JS/static behavior without changing route identity.
