# Live Vs Proposed Contract Audit

## Live Contract Authority

Current checked-in live contract authority is under:

- `contracts/semantic/**`
- `contracts/representation/**`
- `contracts/view/**`
- `contracts/action/**`
- `contracts/route/**`
- `contracts/policy/**`
- `contracts/surface/**`

The focused repair did not edit these live contracts.

## Proposed Contracts

`docs/planning/public_live_preimplementation/proposed_contracts/**` is planning
material. It was not promoted into live contract law by this task and was not
used as the failing validator source.

## Runtime Surface

`runtime/surface/**` is implementation, not contract authority. It is used only
as current phase evidence for whether the old TSIS-00 absence check should apply
to the current repo.

## Conclusion

The drift was not proposed-vs-live contract confusion. It was a stale current
repo phase expectation in a TSIS validator.

