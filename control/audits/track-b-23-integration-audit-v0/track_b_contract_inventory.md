# Track B Contract Inventory

## Contract Families

- `contracts/node/`: node manifest, node policy, node capability, WorkUnit,
  WorkUnit result, and local foundry state.
- `contracts/query/`: query observation, search miss, SearchNeed, candidate,
  and observation-review related contracts.
- `contracts/source/cache/`: source cache record and manifest contracts.
- `contracts/pack/`: source, evidence, index, contribution, and pack staging
  contracts.
- `contracts/index/master/`: review queue and reviewed public-record proposal
  contracts.
- `docs/reference/EVIDENCE_LEDGER_CONTRACT.md`: current evidence ledger
  contract reference.

## Consistency Findings

- Node manifests, policies, and capabilities share governed node inventories.
- WorkUnits and WorkUnit results align through node contracts and dry-run
  policies.
- QueryObservation, SearchMiss, SearchNeed, and Candidate Store preserve the
  signal-to-candidate path without public truth acceptance.
- Source cache and evidence ledger separate observations from evidence
  candidates.
- Source-cache-to-evidence bridge preserves provenance and no-truth conversion.
- Review queue, promotion dry-run, and reviewed public-index rebuild contract
  preserve review gates before any public proposal.
- Pack builder and pack export preserve draft/export-only status.

## Warning

The prompt-listed `contracts/evidence/` directory is not present. Current
evidence ledger semantics are represented by reference docs and governed
control inventories, so this is tracked as a warning rather than a blocker.
