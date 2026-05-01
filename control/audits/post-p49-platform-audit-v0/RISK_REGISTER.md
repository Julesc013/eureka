# Risk Register

| Risk | Classification | Current evidence | Mitigation |
|---|---|---|---|
| False production claim | `blocked` | Validators and docs avoid positive deployment/runtime claims. | Keep P51 focused on claim cleanup and validation. |
| Broken static deployment | `blocked` | Recorded Pages run failed before artifact upload. | Operator must enable Pages/GitHub Actions and rerun. |
| Hosted backend absent | `operator_gated` | No host config or deployment evidence. | Decide host and ops controls before backend work. |
| Live source overreach | `approval_gated` | Live probe gateway contract only, disabled sources. | Require approval pack before IA probe. |
| Query privacy leakage | `contract_only` | Safety policy exists, query learning absent. | Design privacy/poisoning guard before query cache. |
| Metadata poisoning | `planning_only` | Review queue contracts exist; promotion policy absent. | Add candidate promotion policy before imports. |
| Pack import confusion | `planning_only` | Validate-only tools exist; import runtime absent. | Keep no-mutation flags visible. |
| AI truth leakage | `approval_gated` | AI output validator exists; runtime absent. | Keep candidate-only doctrine. |
| Source coverage gaps | `fixture_only` | 10 source gaps and 7 capability gaps remain. | Prioritize source cache/evidence ledger after query gaps. |
| External baseline absence | `manual_pending` | 192 pending, 0 observed. | Human-operated batch 0. |
| Ops/security gaps | `operator_gated` | No root security/contribution docs, no hosted ops. | Add docs/policy pack before public intake. |
