# Breaking Change Policy

Public Data Contract Stability Review v0 defines breaking changes only for the
listed `stable_draft` field paths.

A breaking-change note is required before:

- removing a `stable_draft` field
- renaming a `stable_draft` field
- changing the type of a `stable_draft` field
- changing a safety flag from false to true without a new enabling contract
- marking a future/deferred/live-disabled posture as implemented without the
  matching implementation milestone
- changing source placeholder semantics or hiding `source_id`
- removing route path/status/stability basics from `page_registry.json`
- removing public-alpha non-production and blocked/review count semantics from
  `route_summary.json`

The following are non-breaking unless a specific consumer contract says
otherwise:

- count value movement after inventory/eval changes
- adding new fields
- adding new source records
- adding new page/route records
- adding new route classifications when documented
- adding new capability booleans under experimental capability objects
- wording changes in limitation or next-step text
- CI-provenance value changes in volatile fields

This policy does not create production API compatibility. It only prevents
accidental client dependence on unstable pre-alpha public JSON details.
