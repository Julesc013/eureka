# R0 Production Recovery Plan

R0 interrupts F0 so the dev branch can be classified, quarantined where needed, and rebuilt around real product seams.

## Sequence

1. `R0-01` - Dev production reality inventory
2. `R0-02` - Runtime architecture leakage gate
3. `R0-03` - Contract taxonomy refactor
4. `R0-04` - Source observation production seam
5. `R0-05` - Durable source cache store
6. `R0-06` - Durable evidence ledger store
7. `R0-07` - Review queue product seam
8. `R0-08` - Reviewed public index rebuild
9. `R0-09` - One-source live test
10. `R0-10` - Dev-to-main production review

## Rules

- R0-01 is audit/classification only.
- R0-02 must turn architecture leakage findings into an enforceable gate.
- R0-03 must separate product/domain contracts from audit, fixture, policy, and preview schemas.
- R0-04 through R0-08 must create real product seams before extraction work resumes.
- R0-09 must prove one bounded source observation through review and public index output.
- R0-10 decides whether dev is promoted, squashed, cherry-picked, or further quarantined.

F0 cannot resume until the relevant R0 blockers are cleared. dev must not merge to main before R0-10.
