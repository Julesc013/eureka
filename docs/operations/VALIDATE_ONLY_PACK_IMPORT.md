# Validate-Only Pack Import

Validate-Only Pack Import Tool v0 is the first executable preflight step for
future pack import workflows. It validates explicit pack roots or known
repository examples, delegates to existing pack validators, and emits Pack
Import Report v0 JSON.

It is validate-only. It does not import. It does not stage packs. It does not
index. It does not upload. It does not mutate runtime state, public search,
local indexes, the runtime source registry, or the master index. It does not
call networks, fetch URLs, scrape, crawl, call models, load AI providers, or
write hidden local state.

Validate-Only Pack Import Tool v0 emits Pack Import Report v0 and does not import, does not stage, does not index, does not upload, and does not mutate the master index.

Local Quarantine/Staging Model v0 is planning-only. No staging runtime exists,
it does not create staged state, and it does not import, does not stage, does
not index, does not upload, and does not mutate public search or the master
index. It defines the future private/local path and reset/delete/export model
after this validate-only report step.

## Command Usage

List known examples:

```bash
python scripts/validate_only_pack_import.py --list-examples
```

Validate all known pack examples and print a human summary:

```bash
python scripts/validate_only_pack_import.py --all-examples
```

Emit the full Pack Import Report v0 JSON:

```bash
python scripts/validate_only_pack_import.py --all-examples --json
```

Validate one explicit pack root:

```bash
python scripts/validate_only_pack_import.py --pack-root examples/source_packs/minimal_recorded_source_pack_v0 --json
```

Include registered typed AI output examples as an `ai_output_bundle` report
input without model calls:

```bash
python scripts/validate_only_pack_import.py --all-examples --include-ai-outputs --json
```

Write the generated report only to an explicit output path whose parent already
exists:

```bash
python scripts/validate_only_pack_import.py --all-examples --output tmp/report.json
```

The tool does not create the output parent directory. This prevents accidental
creation of staging, quarantine, cache, or import roots.

Staging Report Path Contract v0 governs report output locations. The tool
defaults to stdout, writes files only for an explicit output path, rejects
forbidden committed/runtime/public roots, and redacts local absolute paths in
report content. This redaction boundary applies before any report is committed
or exposed publicly. Report path success is still not import, staging,
indexing, rights clearance, malware safety, public-search eligibility, or
master-index acceptance.

## Input Scope

The tool accepts only:

- explicit `--pack-root` values
- known examples from `control/inventory/packs/example_packs.json`
- typed AI output examples from
  `control/inventory/ai_providers/typed_output_examples.json` when
  `--include-ai-outputs` is supplied

It does not recursively scan arbitrary directories. Unknown roots become
`unknown_type` or `unsupported_pack_type` report entries.

## Report Generation

The generated report uses `contracts/packs/pack_import_report.v0.json` and is
validated against `scripts/validate_pack_import_report.py`.

The report records:

- input roots, redacting local absolute paths outside the repo
- per-pack validation status
- validator ids and validator commands
- checksum, schema, privacy, rights, and risk status summaries
- issues and remediations
- record-count hints when safely available from manifests
- next actions such as `inspect_future`, `fix_pack_and_revalidate`, or
  `unsupported`
- hard mutation-safety fields

The report itself is not import. It is a local validation artifact for review.

## Safety Guarantees

Every generated report records:

- `import_performed: false`
- `staging_performed: false`
- `indexing_performed: false`
- `upload_performed: false`
- `master_index_mutation_performed: false`
- `runtime_mutation_performed: false`
- `network_performed: false`

The same fields appear in `mutation_summary`. Success means the selected
validators passed. It does not prove truth, rights clearance, malware safety,
source trust, compatibility truth, public-search eligibility, or master-index
acceptance.

## Relationships

Pack Import Validator Aggregator v0 validates pack roots. Pack Import Report
Format v0 defines the report envelope. Validate-Only Pack Import Tool v0
combines those two pieces for a preflight report without staging or import.

Future Local Quarantine/Staging Model v0 may define private staging roots.
Future staged inspection may render report and pack metadata. Future local
index candidate import may opt in to public-safe staged records. Future
contribution and master-index review paths remain separate and review-gated.

Local Staging Manifest Format v0 defines the future local/private manifest
envelope that may link back to a reviewed Pack Import Report v0. The manifest
format is contract/example/validation only. No staging runtime exists, no
staged state is created, and it does not mutate public search, local indexes,
runtime source registry state, uploads, or the master index.

Typed AI outputs may be included only after Typed AI Output Validator v0 checks
them. They remain suggestions/candidates and do not become evidence,
contribution records, search ranking input, or master-index claims.

## Deferred

Still future: staging directories, quarantine, staged inspection, source pack
import, evidence pack import, index pack import, contribution pack import,
master-index queue import, local index mutation, public search mutation,
hosted submission, moderation, accounts, AI provider runtime, model calls,
live source connectors, downloads, installers, relay runtime, native clients,
rights clearance, malware safety, canonical truth selection, and production
readiness.
