# Public Search Result Card Contract v0

Status: implemented as a contract-only audit pack.

This pack records the governed public search result-card envelope introduced
after Public Search API Contract v0. It defines the display and JSON unit that
future web, API, lite/text, native, relay, snapshot, and contribution consumers
may read when a future local-index-only public search runtime exists.

This pack does not implement public search runtime, add `/search` or
`/api/v1/search` behavior, enable live probes, enable downloads or installers,
claim malware safety, claim rights clearance, or claim production API stability.

## Contents

- `RESULT_CARD_FIELD_MATRIX.md`: field stability and visibility decisions.
- `STABILITY_DECISIONS.md`: why fields are stable-draft, experimental,
  volatile, internal, or future.
- `CLIENT_RENDERING_GUIDANCE.md`: web/API/lite/text/native/relay/snapshot
  rendering guidance.
- `ACTION_AND_RISK_GUIDANCE.md`: allowed, blocked, future-gated, rights, and
  executable-risk posture.
- `EXAMPLES.md`: fixture-safe example card index.
- `public_search_result_card_contract_report.json`: structured report for
  validators and future audits.

## Related Files

- `contracts/api/search_result_card.v0.json`
- `contracts/api/search_response.v0.json`
- `contracts/api/examples/search_result_card_*.v0.json`
- `docs/reference/PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md`
- `docs/reference/PUBLIC_SEARCH_API_CONTRACT.md`
