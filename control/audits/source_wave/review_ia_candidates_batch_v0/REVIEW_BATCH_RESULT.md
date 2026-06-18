# IA Candidate Review Batch Result

Task: `REVIEW-IA-CANDIDATES-BATCH-00`

Status: `PASS_WITH_WARNINGS`

## Inputs

- source-observation delta: `.eureka/source-wave/ia-metadata/source-observation-cache/latest/source_observation_delta_manifest.json`
- source-observation delta hash: `sha256:ae231580c7696b1631fe1fabe310567a18bb3eeadbcf306ef455e6c100dd86e4`
- candidate-index delta: `.eureka/source-wave/ia-metadata/candidate-index/latest/candidate_index_delta_manifest.json`
- candidate-index delta hash: `sha256:78c9fd2f46fcbc48d658f2bd5d3c61304856c23a9748129e281c7ce4b5cd70c8`
- evidence-summary delta: `.eureka/source-wave/ia-metadata/evidence-ledger/latest/evidence_summary_delta_manifest.json`
- evidence-summary delta hash: `sha256:d0ca0d667bd2c7aaeea8c4c9cffc7eb232c66292b20a5d887abcef5d008ca570`

## Batch

- batch id: `review-batch:ia_metadata:4cb823d17388bdf2ec3a`
- source observations consumed: 56
- candidates consumed: 56
- evidence summaries consumed: 344
- review items prepared: 56
- pending review items: 56
- review group counts: `{"absence_or_near_miss": 40, "evidence_rich_pending_review": 16}`
- attention band counts: `{"high_attention": 8, "medium_attention": 32, "standard_attention": 16}`
- missing field counts: `{"missing_platform_or_date_hint": 8, "missing_representation_member_hint": 24}`
- provider modes in inputs: `fixture`, `live`
- provider modes in review items: `fixture`
- contradiction items: 0
- insufficient-support items: 40
- absence/near-miss items: 40
- live-derived review items: 0
- fixture-derived review items: 56
- previous batch: none
- diff status: `first_run_no_previous_batch`

## Decisions

- operator decision file supplied: false
- decisions supplied: false
- decisions recorded: 0
- review-ledger events written: 0
- promote: 0
- reject: 0
- supersede: 0
- near miss: 0
- need: 0
- policy blocked: 0
- request more evidence: 0
- undecided: 56

## Boundary

- automatic decisions: false
- automatic promotion: false
- reviewed records created: false
- reviewed/master mutation: false
- public-index mutation: false
- candidate-index store mutation: false
- evidence-ledger store mutation: false
- reviewed-index rebuild: false
- snapshot refresh: false
- accepted truth created: false

## Safety

- network/provider calls: false
- downloads/file fetch/Wayback: false
- public fanout: false
- public mutation: false
- public exposure: unchanged and paused
- rights/safety claims: false
- production/readiness claim: false
- license posture: restricted source-available, unchanged

## Operator Handoff

Review the generated operator packet and fill an explicit decision file for any
reviewed subset. Omitted items remain pending. Promotion requires
`local_only_confirmed: true`.

Remaining blocker:

```text
WAITING_FOR_OPERATOR_REVIEW_DECISIONS
```

Recommended next action:

```text
Fill and validate the generated operator decision template, then rerun
record-decisions for an explicitly reviewed subset.
```
