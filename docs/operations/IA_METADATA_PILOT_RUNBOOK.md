# IA Metadata Pilot Runbook

IA-00 does not run a pilot. This runbook records the approval sequence for a
future pilot.

## IA-00

Approve metadata-only policy with runtime disabled. Validate:

```powershell
python scripts/validate_ia_metadata_policy.py
```

No live call is allowed in IA-00.

## IA-01

Harden fixture replay before any live request:

- metadata search fixture
- exact item metadata fixture
- file-list metadata fixture
- missing item fixture
- malformed/partial fixture
- 429/Retry-After fixture
- large file-list fixture
- no-download proof

Run:

```powershell
python scripts/eureka_ia_fixture_replay.py --fixture-dir examples/internet_archive_metadata --json
python scripts/validate_ia_fixture_replay.py
```

IA-01 output is source-observation candidate material only. It is not source
truth, and it performs no live calls, downloads, source-cache writes, evidence
writes, or index mutation.

## IA-02

Only after IA-01, an operator may approve a tiny local live metadata probe. The
probe must be one-shot, row-capped, cached, kill-switch guarded, and identified
by a descriptive User-Agent with contact.

IA-02 command:

```powershell
python scripts/eureka_ia_live_metadata_probe.py --approve-live --query sampleproject --rows 1 --max-requests 2 --user-agent "EurekaLocalPilot/0.1 (metadata-only; contact: local-operator)" --contact "local-operator" --json --redacted-output control/audits/ia-02-local-live-metadata-probe-v0/generated/live_probe_redacted_summary.json --boundary-output control/audits/ia-02-local-live-metadata-probe-v0/generated/live_probe_boundary_report.json
```

IA-02 initially exposed a local Python TLS trust failure. The follow-up TLS
continuation repaired the local trust lane and reran the same bounded metadata
probe successfully. Only redacted summaries and normalized preview records were
committed; raw response bodies were not committed.

Still forbidden in IA-02:

- downloads
- uploads/write APIs
- public fanout
- source-cache writes by default
- evidence writes
- candidate or reviewed index mutation

## Later Gates

## IA-03

IA-03 adds the first source-cache write path for IA metadata observations. It
accepts IA-01 fixture normalized records and IA-02 redacted live-preview records
only. The write path defaults to dry-run and may write only to an explicit
temporary or local instance with `--apply` and a configured operator token.

Run:

```powershell
python scripts/validate_ia_source_cache_write.py
python scripts/eureka_ia_source_cache_write.py --instance ..\instances\default --operator-token local-dev-token --from-fixtures --dry-run --json
```

IA-03 source-cache records are not evidence and are not reviewed/indexed truth.

## IA-04

IA-04 converts IA source-cache records into evidence-ledger candidates. The
write path defaults to dry-run and may write only to an explicit temporary or
local instance with `--apply` and a configured operator token.

Run:

```powershell
python scripts/validate_ia_evidence_ledger_integration.py
python scripts/eureka_ia_evidence_ledger_write.py --instance ..\instances\default --operator-token local-dev-token --from-source-cache --dry-run --json
```

IA-04 evidence candidates require review and are not accepted truth. Candidate,
reviewed, and master indexes remain untouched.

## IA-05

IA-05 converts IA evidence candidates into provisional candidate-index records.
The write path defaults to dry-run and may write only to an explicit temporary
or local instance with `--apply` and a configured operator token.

Run:

```powershell
python scripts/validate_ia_candidate_index_integration.py
python scripts/eureka_ia_candidate_index_write.py --instance ..\instances\default --operator-token local-dev-token --from-evidence-ledger --dry-run --json
```

IA-05 candidates are searchable provisional records for future review. They are
not reviewed records, not accepted truth, and do not mutate reviewed or master
indexes.

## IA-06

IA-06 loads provisional IA candidate records into a review queue and records
local review decisions. The temp-instance proof uses
`approve_for_reviewed_index_dry_run` to create promotion previews only.

Run:

```powershell
python scripts/validate_ia_review_promotion_dry_run.py
python scripts/eureka_ia_review_queue.py --instance ..\instances\default --from-candidate-index --decision approve_for_reviewed_index_dry_run --dry-run --json
python scripts/eureka_ia_promotion_dry_run.py --from-review-decisions --from-review-report <review-report.json> --json
```

IA-06 does not write the reviewed index or master index. Promotion previews are
not accepted truth and do not create final reviewed records.

## Later Gates

IA-07 may define a reviewed local index rebuild. No gate may convert live
metadata directly into public truth.
