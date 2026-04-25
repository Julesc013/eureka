# Hard Test Proposals

These are future executable tests proposed by this audit. They are not all
implemented in this milestone.

Do not rewrite hard fixtures to make reports look better. Hard tests should
protect difficult eval expectations and force capability gaps to stay visible
until evidence-backed behavior actually improves.

| Test id | Target | Failure it should catch | Why it matters | Suggested implementation | Severity | Milestone |
| --- | --- | --- | --- | --- | --- | --- |
| HTP-001 | Source Registry | malformed source registry record accepted | Source inventory is the control plane | Add temp invalid `.source.json` fixture test | high | Hard Test Pack v0 |
| HTP-002 | Source Registry/Rust parity | duplicate source ID silently accepted | Duplicate source IDs break parity and trust | Test duplicate temp inventory in Python and Rust optional lane | high | Hard Test Pack v0 |
| HTP-003 | Public Alpha | route inventory mismatch | Public-alpha posture can drift | Compare route patterns to handler constants if centralized | high | Hard Test Pack v0 |
| HTP-004 | Public Alpha | local path leakage in status or blocked response | Demo safety depends on no private path exposure | Use sentinel private path and assert absence | high | Hard Test Pack v0 |
| HTP-005 | Docs | README command drift | First-time operators may run stale commands | Parse fenced/script commands and check files exist | medium | Docs Link/Command Drift Guard v0 |
| HTP-006 | Eval Truth | hard eval accidentally weakened | Evals lose value if made easy | Snapshot required hard task ids and expected statuses | high | Hard Test Pack v0 |
| HTP-007 | Search Usefulness | external baseline fabricated | Audit comparisons must be evidence-backed | Reject `observed` external observations without manual evidence fields | high | Hard Test Pack v0 |
| HTP-008 | Python Oracle | golden drift hidden | Rust parity depends on Python oracle stability | Run generator check in full lane and inspect normalized fields | high | Hard Test Pack v0 |
| HTP-009 | Rust Parity | Rust JSON mismatch | Rust cannot replace Python without parity | Generalize source-registry comparison pattern | medium | Rust Query Planner Parity Candidate v0 |
| HTP-010 | Query Planner | fallback misclassification | Planner expansion must be deterministic | Add representative queries per family with expected task kind | high | Planner Gap Reduction Pack v0 |
| HTP-011 | Local Index/Absence | no-result path lacks absence summary | Search misses should explain checked sources | Add no-result query test through index/audit runner | medium | Hard Test Pack v0 |
| HTP-012 | Resolution Memory | memory captures private path | Memory must stay privacy-conscious | Create memory from temp run and assert normalized/no private roots | high | Hard Test Pack v0 |
| HTP-013 | Local Tasks | task output exposes private root in public-alpha mode | Safe mode must not leak local controls | Smoke local task endpoints with sentinel roots | high | Hard Test Pack v0 |
| HTP-014 | Member Access | unsupported archive/member access hides error | Users need clear next steps | Add unsupported representation and missing member tests | medium | Eval Capability Gap Reduction Pack v0 |
| HTP-015 | Source Registry | placeholder source marked implemented | Source gaps should remain honest | Assert placeholder connectors remain non-live/non-implemented | medium | Real Source Coverage Pack v0 |
