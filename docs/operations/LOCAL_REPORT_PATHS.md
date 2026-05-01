# Local Report Paths

Local Report Paths is the operator-facing guide for Staging Report Path
Contract v0. It covers validate-only report output and future staging report
locations before any staging runtime exists.

No staging runtime exists. No local report directory is created by this
milestone. Tools do not create `.eureka-local/`, do not stage pack contents, do
not index packs, do not upload, do not mutate public search, and do not mutate
the master index.

## Validate-Only Reports

The safe default is stdout:

```bash
python scripts/validate_only_pack_import.py --all-examples --json
```

Writing a report file requires an explicit output path:

```bash
python scripts/validate_only_pack_import.py --all-examples --output tmp/report.json
```

The output parent must already exist. The tool must not silently create
staging, quarantine, cache, import-report, or hidden local-state directories.

## Safe Future Local Roots

Future local/private report roots are:

- `.eureka-local/reports/`
- `.eureka-local/staging/`
- `.eureka-local/quarantine/`
- `.eureka-local/import-reports/`
- `.eureka-reports/`
- application-local data roots for native clients
- user-configured cache or staging roots outside the repo
- test temp directories

Repo-local future roots are ignored by git and must not be committed.

## Forbidden Output Roots

Do not write local/private reports to `site/`, `site/dist/`, `external/`,
`runtime/`, `surfaces/`, `control/inventory/`, `contracts/`, `docs/` except
hand-authored docs, `snapshots/examples/`, `evals/`, `crates/`, `.github/`,
or canonical runtime source trees.

## Redaction

Reports intended for committed examples, audits, docs, public static output,
snapshots, relay, or contribution review must redact absolute local paths,
home directories, drive letters, usernames where possible, credentials, API
keys, passwords, tokens, and private keys.

Prefer pack-root-relative paths and synthetic placeholders such as
`<redacted-local-path>` or `<explicit-local-path>`.

## What Success Means

A valid report path means the output location follows policy. It does not mean
the pack was imported, staged, indexed, submitted, accepted, rights-cleared,
malware-safe, or canonical truth.

## Future Work

Local Staging Manifest Format v0 should define the future manifest envelope.
Staged Pack Inspector v0 should define read-only inspection. A staging tool
must wait until those contracts exist.
