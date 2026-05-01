# Local Quarantine/Staging Model

Local Quarantine/Staging Model v0 defines the future local/private area that
may sit after validate-only pack import reports and before any inspection,
local index candidate mode, contribution export, or master-index review path.
It is planning and governance only.

No staging runtime exists. No staged state is created. No `.eureka-local/`
directory is created. The model does not import packs, does not stage packs,
does not index packs, does not upload, does not mutate public search, does not
mutate the runtime source registry, and does not mutate the master index.

## Meaning

Local quarantine/staging means a future user/operator explicitly chooses to
record validated pack metadata and its Pack Import Report v0 into a private,
user-controlled local root for later inspection. Staged records remain claims,
candidates, summaries, or diagnostics.

It does not mean:

- copying arbitrary user directories
- trusting pack records as canonical truth
- merging into the canonical source registry
- changing local public search
- mutating a local index
- submitting to a hosted or master index
- accepting contributions
- fetching URLs or live sources
- loading executable plugins
- storing raw SQLite/cache databases
- exporting private data by default

## Future Roots

Future roots must be user controlled and private by default. Acceptable future
root classes are:

- user-configured cache root
- application-local data root
- repo-local ignored development root

The suggested development-only root is `.eureka-local/`. It is ignored in
`.gitignore` together with `.eureka-cache/`, `.eureka-staging/`, and
`.eureka-reports/`, but this milestone does not create those directories.

Staging Report Path Contract v0 now defines where future validate-only reports,
future staging reports, and future local staging manifests may be written. It
sets stdout as the default report output, requires explicit output paths for
file writes, requires redaction of private local paths, and forbids local
private reports under public/generated/runtime/canonical source roots.

Local Staging Manifest Format v0 now defines the future manifest envelope for
staged local/private candidates. It records validate-only report references,
staged pack references, staged entity candidates, counts, provenance,
privacy/rights/risk posture, hard no-mutation guarantees, and future
reset/delete/export policy. It is contract/example/validation only; no staging
runtime exists and it does not create staged state, copy pack contents, mutate
public search, mutate a local index, mutate the runtime source registry, or
mutate the master index.

Forbidden roots include `site/dist`, `site/`, public data, `external`,
`runtime`, canonical `control/inventory` source files, `evals`,
`snapshots/examples`, `crates`, and `docs`.

## Staged Metadata

Future staged metadata may include:

- staged pack reference
- staged validation report
- staged source candidate
- staged evidence candidate
- staged index summary
- staged contribution candidate
- staged AI output candidate
- staged issue
- staged decision note

Future staged metadata must link to pack ID, pack version, pack checksum,
validate-only import report ID, validator tool IDs, and any referenced
source/evidence/index/contribution packs. User account identity is not required
in v0.

## Privacy, Rights, And Risk

The default visibility is `local_private`. `public_safe` is allowed only after
validation and review posture are recorded. Rights uncertainty remains
`review_required`. Private paths, credentials, executable payloads, raw
databases, raw caches, and long copyrighted text dumps require rejection or
quarantine.

Staging success is not canonical truth, rights clearance, malware safety,
public-search eligibility, or master-index acceptance. Telemetry is off by
default.

## Search And Index Impact

Current local public search is unaffected. Staged packs do not appear in search
by default. Staged records do not alter the runtime source registry. A future
`local_index_candidate_future` mode needs its own milestone and must preserve
staged provenance while remaining local/private unless separately reviewed.

Hosted public search and GitHub Pages static output are unaffected.

## Native, Relay, Snapshot, And AI Boundaries

Future native clients may offer a private local staging UI, but staged data is
not exposed through relay surfaces by default. Snapshots exclude staged private
data by default. Any public-safe export requires validation and review.

Typed AI outputs may be staged later only as typed, review-required candidates.
They do not become evidence, contribution records, search ranking input, or
master-index claims by staging alone.

## Future Operations

Before runtime staging exists, future plans must define how to list staged
packs, inspect staged metadata, delete one staged pack, clear all staged state,
export a staging report only, and export a public-safe contribution candidate
in a future review-gated path.

## Deferred

Still future: staged pack inspector, local quarantine/staging tool, staged
delete/reset tool, local index candidate planning, contribution queue
candidate export, native staging UI planning, hosted submission, and any
staging runtime.
