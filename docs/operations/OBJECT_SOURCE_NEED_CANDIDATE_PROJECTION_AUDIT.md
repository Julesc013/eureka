# Object Source Need Candidate Projection Audit

TRACK-A-14 records how current static, demo, and public-data artifacts relate to
the canonical `ObjectPageView`, `SourcePageView`, `NeedPageView`, and
`CandidatePageView` contracts.

The audit is read-only. It inspects committed artifacts under `site/dist` and
governance inventories, but it does not regenerate the static site, refactor
renderers, activate public routes, enable hosted behavior, or change search
semantics.

## Audited Areas

- Object-like result demos under `site/dist/demo/`.
- Source summary pages and data under `site/dist/sources.html`,
  `site/dist/lite/sources.html`, `site/dist/text/sources.txt`, and
  `site/dist/data/source_summary.json`.
- File-tree seed metadata under `site/dist/files/` where it references public
  data summaries.
- Need-like absence demo content under `site/dist/demo/absence-example.html`.
- Candidate-like comparison/demo data under `site/dist/demo/` and
  `site/dist/demo/data/demo_snapshots.json`.
- Missing future canonical route examples for objects, sources, needs, and
  candidates, recorded as missing rather than created.

## Commands

Run the human-readable audit:

```text
python scripts/audit_object_source_need_candidate_projection.py
```

Run the product-boundary check:

```text
python scripts/audit_object_source_need_candidate_projection.py --check
```

Refresh the explicit audit report:

```text
python scripts/audit_object_source_need_candidate_projection.py --json-output control/audits/track-a-14-object-source-need-candidate-projection-v0/projection_audit_report.json
```

## Interpretation

`status: warn` is expected while current artifacts are only static/demo/public
data and are not generated from canonical view-model fixtures. `--check` fails
only for critical product-boundary claims such as hosted backend activation,
live probes, source connectors, downloads, uploads, accounts, telemetry,
rights clearance, malware safety, exhaustive global search, automatic
promotion, or public truth from candidates/source observations/evidence
candidates/AI drafts.

## Deferred Work

The audit recommends a later fixture and dry-run plan for object, source, need,
and candidate projections after the Track A renderer parity work is ready. That
future work should create canonical fixtures, project each fixture into governed
representations, compare output to current static/demo content, and preserve
all current no-live/no-hosted/no-download boundaries.
