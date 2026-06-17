# IA Candidate Index Refresh Delta

Task: `IA-CANDIDATE-INDEX-REFRESH-00`

Status: `PASS_WITH_WARNINGS`

## Result

- input source-observation delta:
  `.eureka/source-wave/ia-metadata/source-observation-cache/latest/source_observation_delta_manifest.json`
- input source-observation delta hash:
  `sha256:ae231580c7696b1631fe1fabe310567a18bb3eeadbcf306ef455e6c100dd86e4`
- source observations consumed: 56
- provisional candidates written: 56
- deduplicated candidate count: 56
- candidate ID pattern: `candidate:ia_metadata:<short_hash>`
- query count: 7
- provider modes represented: fixture, live
- policy gate status: PASS
- unsafe record count: 0
- redacted error count: 0
- generated candidate-index delta path:
  `.eureka/source-wave/ia-metadata/candidate-index/latest/`
- generated manifest path:
  `.eureka/source-wave/ia-metadata/candidate-index/latest/candidate_index_delta_manifest.json`
- generated candidate file hash:
  `sha256:baacb66438dabeaa361066e88749eb99280bcfda67d56960b5a4969bb36a4fa7`
- previous candidate delta: none
- diff status: first_run_no_previous_delta
- reviewed/master mutation: false
- public-index mutation: false
- candidate-index store mutation: false
- evidence-ledger mutation: false
- review/promotion mutation: false
- public fanout: false
- downloads/file fetch: false
- Wayback replay: false
- rights/safety claims: false
- public-alpha posture unchanged: true
- license posture unchanged: true

## Current Source-Index Path

```text
IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00
-> IA-SOURCE-OBSERVATION-CACHE-DELTA-00
-> IA-CANDIDATE-INDEX-REFRESH-00
-> IA-EVIDENCE-LEDGER-SUMMARY-00
-> REVIEW-IA-CANDIDATES-BATCH-00
```

## Remaining Blockers

- `WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE`
- `WAITING_FOR_USER_HARDWARE_DETAILS`
- Public launch remains paused pending separate operator decisions.

Recommended next task: `IA-EVIDENCE-LEDGER-SUMMARY-00`.
