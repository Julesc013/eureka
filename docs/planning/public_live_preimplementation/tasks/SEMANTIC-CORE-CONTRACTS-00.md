# SEMANTIC-CORE-CONTRACTS-00

Goal: audit and, only if needed, align semantic/action/status contracts for
fallback and public projections.

Inputs to read first: `contracts/semantic/**`, `contracts/action/**`,
`contracts/route/**`, `contracts/representation/**`,
`proposed_contracts/*.proposed.json`.

Allowed paths: `contracts/**`, `tests/contracts/**`, `scripts/validate_*.py`,
`control/inventory/**`.

Protected paths: runtime behavior and public deployment paths.

Deliverables: gap report, contract updates if justified, validators, focused
tests.

Non-goals: renderer/runtime implementation, source calls, reviewed truth.

Validation: TSIS/representation/semantic parity validators and focused contract
tests.

Exit criteria: every user-visible result/action can map to canonical
status/action policy.

Impact statement: contract/schema impact required.

