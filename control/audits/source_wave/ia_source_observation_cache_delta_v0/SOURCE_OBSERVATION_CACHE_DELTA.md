# IA Source Observation Cache Delta

- task: IA-SOURCE-OBSERVATION-CACHE-DELTA-00
- status: PASS_WITH_WARNINGS
- input smoke report: `control/audits/source_wave/ia_metadata_provider_wiring_and_smoke_v0/ia_metadata_provider_smoke_report.json`
- input smoke report hash: `sha256:811bbecf07120e6a410ca122020f63296e59b50faa8a0363fb4df743459bf906`
- generated cache delta path: `.eureka/source-wave/ia-metadata/source-observation-cache/latest/`
- generated manifest: `.eureka/source-wave/ia-metadata/source-observation-cache/latest/source_observation_delta_manifest.json`
- delta id: `source-observation-delta:ia_metadata:441fe581c6a78a797365`
- source observations written: 56
- observation ID pattern: `source-observation:ia_metadata:<short_hash>`
- query count: 7
- workunit count: 70
- provider modes represented: fixture, live
- policy gate status: PASS
- unsafe record count: 0
- redacted error count: 0
- generated observation file hash: `sha256:8a0bf5bd51a8e04fa03a7b477f1b792da397530dd3b48f2f2c17c46f2bc3612f`
- previous delta: none
- diff status: first-run/no-previous-delta
- reviewed/master mutation: false
- public-index mutation: false
- candidate-index mutation: false
- evidence-ledger mutation: false
- public fanout: false
- downloads/file fetch: false
- Wayback replay: false
- rights/safety claims: false
- public-alpha posture unchanged: true
- license posture unchanged: true
- generated `.eureka` output committed: false
- full unittest discovery claimed: false

## Current Source-Index Path

```text
IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00
-> IA-SOURCE-OBSERVATION-CACHE-DELTA-00
-> IA-CANDIDATE-INDEX-REFRESH-00
-> IA-EVIDENCE-LEDGER-SUMMARY-00
-> REVIEW-IA-CANDIDATES-BATCH-00
```

## Remaining Blockers

- External artifact evidence remains waiting.
- User hardware details remain waiting.
- Public launch remains paused pending separate operator decisions.

Recommended next task: `IA-CANDIDATE-INDEX-REFRESH-00`.
