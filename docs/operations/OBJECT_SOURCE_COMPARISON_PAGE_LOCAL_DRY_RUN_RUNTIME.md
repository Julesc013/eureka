# Object/Source/Comparison Page Local Dry-Run Runtime

P103 implements a local dry-run runtime for approved object, source, comparison,
and page preview examples. It is not public runtime and it adds no routes.

## Purpose

The dry-run proves repo-local page examples can be loaded, classified, rendered
into deterministic text/HTML/JSON previews, and summarized without reading
authoritative source/evidence stores or changing public search.

## Local Dry-Run Scope

Implemented:

- Local page record loader.
- Object/source/comparison classifier.
- Text, escaped HTML, and JSON preview renderer.
- Dry-run JSON report builder.
- CLI and validator.
- Synthetic P103 examples and tests.

Not implemented:

- No public routes.
- No hosted runtime.
- No API routes.
- No public search integration.
- No page database or persistent page store.
- No source cache reads or writes.
- No evidence ledger reads or writes.
- No candidate promotion.
- No index mutation.
- No mutation of source, evidence, candidate, public, local, runtime, or master records.

## Approved Input Model

Approved roots:

- `examples/object_pages`
- `examples/source_pages`
- `examples/comparison_pages`
- `examples/page_runtime_dry_run`

The CLI supports `--all-examples`, explicit `--example-root` under approved
roots, `--strict`, `--json`, `--render-preview`, and `--output` for an approved
audit or temp destination.

Forbidden inputs include arbitrary local paths, private absolute paths, URLs,
live source identifiers, connector parameters, source-cache paths,
evidence-ledger paths, database paths, uploaded files, and credentials.

## Output Report Model

The report includes page counts, page summaries, classification counts, preview
outputs, warnings, bounded errors, mutation summary, and hard booleans. The mode
is always `local_dry_run`.

All hosted/public route, public search, live source, source-cache/evidence read,
mutation, telemetry, credential, download, upload, install, and execution flags
remain false.

## Classification Model

The classifier records:

- Page kind.
- Page status.
- Lane.
- Privacy status.
- Public-safety status.
- Action status.
- Conflict/gap status.

Unsupported or unsafe page shape is invalid; unknowns are preserved and do not
become truth claims.

## Rendering Model

Text previews are old-client safe. HTML previews escape all dynamic text, use no
JavaScript, require no external assets, and include no forms or live controls.
JSON previews are deterministic public-safe summaries.

Rendering includes candidate/provisional labels, conflicts, gaps, limitations,
disabled action posture, and caveats that there is no truth, rights clearance,
malware safety, source trust, or installability claim.

## Privacy And Safety

The dry-run rejects or flags private paths, URLs, secret-like fields, raw payload
fields, raw private query data, IP/account/session/user identifiers, and unsafe
action claims. It does not publish anything.

## Action/Rights/Risk

Downloads disabled. Uploads disabled. Installs disabled. Execution disabled.
Package managers, emulators, and VMs disabled. Allowed actions are inspect,
compare, cite, and view metadata only.

## Source/Evidence/Candidate Boundary

The runtime may render synthetic refs already present in examples. It does not
read source cache, read evidence ledger, create candidates, promote candidates,
accept evidence as truth, or mutate source/evidence/candidate/index state.

## Public Search Boundary

Public search does not call the page dry-run runtime. Public search routes,
result cards, responses, and ordering are unchanged. Page links remain disabled
until a later approved runtime integration.

## Hosted Runtime Boundary

No hosted page runtime is enabled. No backend configuration or deployment is
changed by P103.

## CLI Usage

```bash
python scripts/run_page_dry_run.py --all-examples --json
python scripts/run_page_dry_run.py --all-examples --render-preview --json
```

## Validator Usage

```bash
python scripts/validate_page_dry_run_report.py
python scripts/validate_page_dry_run_report.py --json
```

## Examples

P103 adds synthetic public-safe examples under `examples/page_runtime_dry_run`
for object, source, comparison, conflict/gap, and action-safety previews. The
dry-run also validates existing P79-P81 page examples.

## Limitations

Dry-run rendering is not public runtime, not hosted runtime, not a truth system,
not a source/evidence store, and not a candidate promotion path.

## Next Steps

Proceed to P104 Pack Import Local Dry-Run Runtime v0 only after approval.
Human/operator parallel work remains hosted wrapper deployment, backend URL and
edge/rate-limit configuration, static verification, Manual Observation Batch 0
execution, and hosted page runtime policy review.
