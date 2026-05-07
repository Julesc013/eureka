# Manual Observation Batch 0 Execution

Batch 0 is the first manual external-baseline observation batch for Eureka search usefulness work. It contains 39 pending query/system slots under `evals/search_usefulness/external_baselines/batches/batch_0/observations/pending_batch_0_observations.json`.

This packet prepares human execution only. It does not perform observations, open browsers, fetch URLs, scrape, crawl, call APIs, call models, or mark pending slots observed.

## Source Files

- Batch manifest: `evals/search_usefulness/external_baselines/batches/batch_0/batch_manifest.json`
- Pending slots: `evals/search_usefulness/external_baselines/batches/batch_0/observations/pending_batch_0_observations.json`
- Canonical protocol: `docs/operations/MANUAL_OBSERVATION_PROTOCOL.md`
- Anti-fabrication checklist: `docs/operations/MANUAL_OBSERVATION_ANTI_FABRICATION_CHECKLIST.md`
- Failure taxonomy: `docs/operations/MANUAL_OBSERVATION_FAILURE_TAXONOMY.md`

## Human Execution Flow

1. Read the protocol, checklist, and failure taxonomy.
2. Select one `pending_manual_observation` slot by `observation_id`.
3. Confirm the `query_id`, `query_text`, and `system_id`.
4. Manually open the named external system yourself.
5. Manually enter the exact query and record the observation timestamp.
6. Record visible result rank, title, URL or stable locator, and a short public-safe snippet or summary.
7. Record usefulness, limitations, failure classes, and any Eureka comparison fields available.
8. Validate the completed observation with the local validators.
9. Leave the slot pending if the manual session was not actually completed.

## Recording Outcomes

Top-result observations should include rank, title, URL or stable locator, snippet or short summary, usefulness note, limitations, and failure taxonomy classes where relevant.

No-result observations should record the searched scope, visible result count if available, why the outcome is no-result, and why the scope is not exhaustive global search.

Near matches should record why the result is close, why it does not satisfy the need, and whether the gap is identity, compatibility, ranking, source, extraction, representation, or policy related.

## Stop Conditions

Stop and leave the slot pending if legal, privacy, account, paywall, copyright, identity, manual-access, or safety uncertainty appears. Do not invent missing fields to complete a slot.

## Validation

```powershell
python scripts/prepare_manual_observation_batch0_execution.py --check
python scripts/validate_manual_observation_batch0_execution.py
python scripts/validate_manual_observation_protocol.py
python scripts/validate_external_baseline_observations.py
```

Warnings may be recorded, but an observation must not be promoted from pending unless the human observation was actually performed and the required fields are present.
