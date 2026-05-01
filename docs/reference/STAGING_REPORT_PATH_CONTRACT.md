# Staging Report Path Contract

Staging Report Path Contract v0 defines where future validate-only import
reports, local staging reports, and local staging manifests may be written. It
is planning and governance only.

No report path runtime exists. No staging runtime exists. This contract does
not create local report directories, does not create `.eureka-local/` state,
does not import packs, does not stage packs, does not index packs, does not
upload, does not mutate public search, and does not mutate the master index.

## Default Output

The default output mode is `stdout`. A tool that produces a Pack Import Report
v0 or future staging report should print to stdout unless the user or operator
supplies an explicit output path.

File writes require an explicit `--output`-style argument. Parent directories
must already exist by default. Tools must not create hidden local state,
staging roots, quarantine roots, or cache roots as a side effect of validation.

## Allowed Committed Report Roots

Committed report-like files are allowed only when they are synthetic,
audit-safe, or hand-authored:

- `control/audits/*` for audit-safe milestone evidence
- `examples/import_reports/` for synthetic examples
- `docs/` for hand-authored documentation only
- `tests/fixtures/` for synthetic test fixtures if a later test needs them

Committed reports must not contain private local paths, user cache roots,
credentials, private staged pack contents, raw databases, raw caches, or
private user data.

## Forbidden Roots

Future report or staging tools must not write local/private reports into:

- `site/`
- `site/dist/`
- `external/`
- `runtime/`
- `surfaces/`
- `control/inventory/`
- `contracts/`
- `docs/` except hand-authored docs
- `snapshots/examples/`
- `evals/`
- `crates/`
- `.github/`
- `.aide/` except deliberate repo-operating metadata
- any canonical runtime source tree

These paths either publish public artifacts, hold source/runtime behavior, hold
canonical governance records, or are committed examples. They must not become
private local report or staging roots.

## Future Local Roots

Future local/private report roots may include:

- `.eureka-local/reports/`
- `.eureka-local/staging/`
- `.eureka-local/quarantine/`
- `.eureka-local/import-reports/`
- `.eureka-reports/`
- an application-local-data root for native clients
- a user-configured cache or staging root outside the repository
- a temp directory for tests

If a local root is inside the repository, it must be ignored by git. This
milestone documents these roots but creates none of them.

## Filename Policy

Report filenames should be filesystem-safe and should avoid private
information. Future tools should use components such as sanitized pack ID,
short SHA-256 checksum, mode, timestamp, or run ID.

Recommended future pattern:

```text
import-report__<pack_id_sanitized>__<short_sha256>__<mode>.json
```

Filenames must not include raw local paths, raw user query text, full source
URLs, credentials, secrets, or path separators inherited from pack IDs. Machine
reports use `.json`; future human summaries may use `.txt` or `.md`.

## Redaction Policy

Public or committed reports must redact absolute local paths, home
directories, drive letters, usernames where possible, credentials, API keys,
passwords, tokens, and private keys. Pack-root-relative paths are preferred.

Explicit local/private reports may include local paths only when the report is
classified `local_private`. They must never be copied into committed examples,
`site/dist`, public snapshots, relay views, contribution candidates, or master
index review records without review and redaction.

## Validate-Only Tool Relationship

Validate-Only Pack Import Tool v0 already defaults to stdout, writes a report
file only when `--output` is supplied, and requires the output parent to exist.
This contract governs future changes to that behavior and requires forbidden
repo roots to remain blocked for report output.

The validate-only tool remains validation/reporting only. Report success is not
import, staging, rights clearance, malware safety, canonical truth, public
search eligibility, or master-index acceptance.

Local Staging Manifest Format v0 now defines the future manifest envelope that
could be written only by a later explicit local staging tool. The manifest
schema and example are contract/example/validation only. No staging runtime
exists, no staged state is created, and the manifest format has no public
search, local index, runtime source registry, upload, relay, snapshot, or
master index impact.

## Surface Impact

Native clients may later choose app-local private report roots. Relay surfaces
must not expose private reports or local paths by default. Snapshots must not
include local/private reports by default. Public search and GitHub Pages static
output must not read report roots by default.

## Deferred

Still future: staged pack inspector, local quarantine/staging tool, staging
report writer runtime, local index candidate mode, contribution queue candidate
export, native staging UI, and any hosted submission path.
