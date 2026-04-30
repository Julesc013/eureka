# Pack Import Planning

Source/Evidence/Index Pack Import Planning v0 defines the future local import
boundary for governed packs. It is planning only and validation guidance only.
It does not implement import.

## Supported Pack Types

- source packs
- evidence packs
- index packs
- contribution packs

Master-index review queues are adjacent governance inputs, not normal user
import packs.

## Import Means Future Explicit Validation

Future import means an explicit user-selected pack path, schema validation,
checksum validation, JSON/JSONL parsing, privacy/rights/risk classification,
provenance recording, and possibly private local staging.

Import does not mean scanning arbitrary directories, trusting pack records as
truth, merging into the canonical source registry, affecting public search,
mutating a local index, uploading, submitting, accepting into the master index,
fetching URLs, loading plugins, importing raw databases, downloading, or
executing anything.

## Modes

`validate_only` is the first recommended future mode. It runs validators and
emits a report without staging or mutation.

`stage_local_quarantine` is the next future mode. It records pack metadata and
validation results in a private, user-controlled local staging root without
search or index impact.

`inspect_staged`, `local_index_candidate`, and `contribution_queue_candidate`
are future modes that need separate milestones.

## Validation Commands

Future import planning relies on the existing pack validators:

```bash
python scripts/validate_source_pack.py
python scripts/validate_evidence_pack.py
python scripts/validate_index_pack.py
python scripts/validate_contribution_pack.py
```

The master-index review queue validator remains relevant for future review
queue artifacts:

```bash
python scripts/validate_master_index_review_queue.py
```

Pack Import Validator Aggregator v0 now provides the first single validate-only
entrypoint:

```bash
python scripts/validate_pack_set.py --list-examples
python scripts/validate_pack_set.py --all-examples
python scripts/validate_pack_set.py --all-examples --json
```

The aggregate validator delegates to the individual validators. It validates
known examples or one explicit root, reports pass/fail/unavailable/unknown
type, and still does not import, stage, index, upload, submit, or mutate a
master index.

Pack Import Report Format v0 defines the report that future validate-only
tooling should emit after validation:

```bash
python scripts/validate_pack_import_report.py --all-examples
python scripts/validate_pack_import_report.py --all-examples --json
```

The report format records pack results, issues, privacy/rights/risk summaries,
provenance, and explicit next actions. It does not implement import. It does
not stage packs. It does not mutate local index state, runtime state, public
search, or public output. It does not mutate the master index. It does not
upload or submit anything.
It does not mutate local index state.
It does not mutate the master index.

AI Provider Contract v0 is separate from pack import. Typed AI outputs may
later help draft pack/contribution candidates. Typed AI Output Validator v0 now
validates those outputs through `scripts/validate_ai_output.py` before any
future drafting workflow may inspect them, but pack import remains
validate-only first and cannot treat AI output as truth, rights clearance,
malware safety, source trust, or automatic acceptance.

## Privacy, Rights, And Risk

Future import must detect private paths, credentials, `local_private` versus
shareable mismatches, executable payloads, raw databases, cache dumps, long
copyrighted text, missing rights/access docs, rights-clearance claims, and
malware-safety claims.

Uncertainty means quarantine or rejection, not silent acceptance.

## Relationship To Other Contracts

Source packs provide source metadata and fixture/evidence inputs. Evidence packs
provide claims and observations. Index packs provide coverage and record
summaries. Contribution packs wrap review candidates. The master-index review
queue is the future review layer for public acceptance.

Pack import planning connects those contracts without implementing import or
acceptance. Validation is not indexing, reporting is not staging, staging is
not publication, and import is not master-index review.

## Not Implemented

P39 does not implement pack import runtime, local staging, local index mutation,
canonical registry mutation, public search mutation, uploads, submissions,
moderation, accounts, hosted master-index writes, live source behavior,
external observation collection, executable plugins, downloads, installers,
native clients, relay runtime, snapshot reader runtime, rights clearance,
malware safety, or production readiness.
