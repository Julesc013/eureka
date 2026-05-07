# AIDE Outcome Report

## RESULT

- result: WARN
- mode: advisory_only
- applies_automatically: false

## SIGNALS

- adapter_guidance: PASS / unknown / info
- context_artifacts: PASS / unknown / info
- golden_tasks: PASS / unknown / info
- review_packet: WARN / review_packet_incomplete / warning
- token_ledger: PASS / unknown / info
- verifier: WARN / verifier_fail / warning

## FAILURE_CLASSES

- review_packet_incomplete: 1
- verifier_fail: 1

## NEXT_ACTION

- top_recommendation: REC-REVIEW-PACKET: Rerun `review-pack` or repair the review-packet template/evidence refs.
- recommendations: `.aide/controller/latest-recommendations.md`
- outcome_ledger: `.aide/controller/outcome-ledger.jsonl`

## SAFETY

- provider_or_model_calls: none
- network_calls: none
- automatic_mutation: false
- raw_prompt_storage: false
- raw_response_storage: false
- controller_policy: `.aide/policies/controller.yaml`
