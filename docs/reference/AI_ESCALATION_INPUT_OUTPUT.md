# AI Escalation Input And Output

Input packets must include a Search Hunt, SearchNeed, exhaustion report, disabled agent research task, checked layers, deferred layers, blocked policy list, steering preferences, candidate context, absence context, forbidden actions, and desired output schema.

The gate refuses raw-query-only escalation. The input packet always records `provider_enabled: false` and `execution_enabled: false`.

Future output classes are:

- alias hypotheses
- source lead candidates
- dead URL trace plan
- archived URL trace plan
- compatibility clues
- provenance questions
- extraction targets
- candidate WorkUnits
- absence explanation draft

Output is candidate-only. It does not become truth, accepted evidence, rights clearance, safety certification, source approval, ranking authority, or index mutation.
