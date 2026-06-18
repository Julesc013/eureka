# IA Evidence Ledger Summary Delta

Task: `IA-EVIDENCE-LEDGER-SUMMARY-00`

Status: `PASS_WITH_WARNINGS`

## Result

- source-observation input:
  `.eureka/source-wave/ia-metadata/source-observation-cache/latest/source_observation_delta_manifest.json`
- source-observation hash:
  `sha256:ae231580c7696b1631fe1fabe310567a18bb3eeadbcf306ef455e6c100dd86e4`
- candidate-index input:
  `.eureka/source-wave/ia-metadata/candidate-index/latest/candidate_index_delta_manifest.json`
- candidate-index hash:
  `sha256:78c9fd2f46fcbc48d658f2bd5d3c61304856c23a9748129e281c7ce4b5cd70c8`
- source observations consumed: 56
- candidates consumed: 56
- evidence summaries written: 344
- deduplicated summaries: 344
- evidence ID pattern: `evidence-summary:ia_metadata:<short_hash>`
- query count: 7
- provider modes represented: fixture, live
- policy gate status: PASS
- unsafe record count: 0
- redacted error count: 0
- orphan candidate refs: 0
- orphan source-observation refs: 0
- generated evidence-summary delta path:
  `.eureka/source-wave/ia-metadata/evidence-ledger/latest/`
- generated manifest path:
  `.eureka/source-wave/ia-metadata/evidence-ledger/latest/evidence_summary_delta_manifest.json`
- generated evidence file hash:
  `sha256:8d0790f7bce282d5c4dd69cd0cdc3cd5379e674e2cf9d5ef76ee6f2c8ada2ade`
- previous evidence delta: none
- diff status: first_run_no_previous_delta
- reviewed/master mutation: false
- public-index mutation: false
- candidate-index store mutation: false
- evidence-ledger store mutation: false
- review/promotion mutation: false
- accepted truth created: false
- public fanout: false
- downloads/file fetch: false
- Wayback replay: false
- rights/safety claims: false
- public-alpha posture unchanged: true
- license posture unchanged: true

## Evidence Type Counts

```json
{
  "absence clue": 8,
  "date/time clue": 32,
  "near-miss clue": 32,
  "object-type clue": 56,
  "platform clue": 16,
  "provenance clue": 56,
  "representation/member clue": 32,
  "source-location clue": 56,
  "title/name clue": 56
}
```

## Support Posture Counts

```json
{
  "candidate_support": 192,
  "insufficient": 40,
  "metadata_mention": 112
}
```

## Current Source-Index Path

```text
IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00
-> IA-SOURCE-OBSERVATION-CACHE-DELTA-00
-> IA-CANDIDATE-INDEX-REFRESH-00
-> IA-EVIDENCE-LEDGER-SUMMARY-00
-> REVIEW-IA-CANDIDATES-BATCH-00
-> REVIEWED-INDEX-REFRESH-FROM-IA-00
```

## Remaining Blockers

- `WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE`
- `WAITING_FOR_USER_HARDWARE_DETAILS`
- Public launch remains paused pending separate operator decisions.

Recommended next task: `REVIEW-IA-CANDIDATES-BATCH-00`.
