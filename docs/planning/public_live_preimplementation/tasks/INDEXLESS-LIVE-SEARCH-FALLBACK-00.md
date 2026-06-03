# INDEXLESS-LIVE-SEARCH-FALLBACK-00

Goal: implement indexless live metadata fallback as a bounded
ResolutionRunKernel mode.

Inputs to read first: `architecture/INDEXLESS_LIVE_SEARCH_FALLBACK_SPEC.md`,
`architecture/SOURCE_OBSERVATION_LAYER_SPEC.md`, source policy docs,
resolution-run tests.

Allowed paths: selected resolver runtime path, source observation/action policy
paths, gateway/public projection paths as needed, focused tests, control
evidence.

Protected paths: public deployment, public/master index mutation, downloads,
extraction, model/provider calls.

Deliverables: fallback run mode, policy gates, disable switches, candidate/need
outputs, tests, validation report.

Non-goals: arbitrary fanout, full Archive.org integration, reviewed truth
promotion.

Validation: index unavailable, insufficient local result, allowlist denial,
budget exhaustion, disable switch, candidate labeling tests.

Exit criteria: fallback is a run mode and never emits verified truth.

Impact statement: runtime, public projection, and contract impact if any.

