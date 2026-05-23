# Local Evidence Ledger Runtime

The local evidence ledger runtime records fixture-only, repo-local evidence candidate records from explicit JSON input. A record may describe a metadata claim, identity claim, compatibility claim, checksum claim, filename/member claim, source locator, pack-derived claim, contribution-derived claim, conflict record, review status record, or provenance link.

Evidence ledger records are candidates and provenance events. They are not accepted evidence, public truth, rights clearance, malware safety, verified installability, source-cache bridge output, or master-index records.

## Inputs

Current inputs are explicit local JSON only:

- committed evidence fixtures and pack examples
- committed candidate, source-cache, SearchNeed, WorkUnitResult, and node policy examples
- explicit evidence ledger record examples
- committed evidence pack examples

Forbidden inputs include live source results, scraped results, private files, secrets, account/session material, telemetry streams, executable downloads, installer payloads, browser profiles, unreviewed API payloads, and AI output claiming truth.

## Outputs

Scripts write no files by default. With an explicit `--output`, reports may be written only under `control/audits/**/generated/` or an explicit temporary test directory.

Allowed current outputs are evidence ledger records, summaries, snapshots, provenance reports, and conflict reports. Future review items, candidate-store requests, and pack drafts remain review-gated.

## Boundaries

Every current record preserves:

- `evidence_record_is_public_truth: false`
- `evidence_record_is_accepted_evidence: false`
- `evidence_record_can_mutate_master_index: false`
- `human_review_required_for_downstream_use: true`

The source-cache-to-evidence bridge is still deferred. No persistent append store is implemented; append intent is represented only in the record/snapshot shape.

## Commands

```bash
python scripts/record_evidence_ledger.py --input examples/evidence/ledger/records/metadata_claim_record_v0.json --check
python scripts/summarize_evidence_ledger.py --input examples/evidence/ledger/records --check
python scripts/validate_local_evidence_ledger_runtime.py
```
