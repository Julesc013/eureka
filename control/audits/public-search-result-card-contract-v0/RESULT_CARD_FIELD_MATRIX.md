# Result Card Field Matrix

Public Search Result Card Contract v0 classifies fields by client stability and
visibility. Stable-draft fields are expected to survive into the first runtime
implementation unless a later contract explicitly changes them.

The matrix includes stable_draft, experimental, volatile, internal, and future
classifications. Volatile public wording is expected to be limited, while
private paths and raw payloads remain internal instead of public volatile fields.

| Field or block | Classification | Notes |
| --- | --- | --- |
| `schema_version` | stable_draft | Version marker for card readers. |
| `contract_id` | stable_draft | `eureka_public_search_result_card_v0`. |
| `result_id` | stable_draft | Public card identifier, not an internal row id. |
| `title` | stable_draft | Primary display text. |
| `subtitle` | stable_draft | Optional compact context. |
| `summary` | experimental | Human-readable explanation may change with ranking work. |
| `record_kind` | stable_draft | Result object category. |
| `result_lane` | stable_draft | Bounded lane vocabulary for user intent and display grouping. |
| `user_cost.score` | stable_draft | Bounded 0..9 hint; lower means less detective work. |
| `user_cost.label` | stable_draft | Coarse label for old clients. |
| `user_cost.reasons` | stable_draft | Short public reasons. |
| `source.source_id` | stable_draft | Public source id. |
| `source.source_family` | stable_draft | Public source family. |
| `source.coverage_depth` | stable_draft | Coverage/posture label. |
| `source.checked_as` | stable_draft | `local_index`, `recorded_fixture`, `static_summary`, `future_live_probe`, or `not_checked`. |
| `source.trust_lane` | experimental | Trust lanes are not finalized. |
| `identity.public_target_ref` | stable_draft | Public-safe target reference. |
| `identity.target_ref` | stable_draft | Compatibility alias only when public-safe. |
| `identity.resolved_resource_id` | experimental | Future runtime may refine resource ids. |
| `identity.object_id` | future | Reserved for object truth. |
| `identity.release_or_state_id` | future | Reserved for release/state modeling. |
| `evidence.evidence_count` | stable_draft | Public evidence count. |
| `evidence.summaries` | stable_draft | Public-safe summaries only, not raw payloads. |
| `evidence.summaries.confidence` | experimental | Confidence vocabulary may change. |
| `compatibility.status` | stable_draft | Bounded compatibility status. |
| `compatibility.confidence` | experimental | Compatibility confidence is provisional. |
| `parent_lineage` | experimental | Used for smallest-actionable-unit context. |
| `member` | experimental | Member extraction model is still evolving. |
| `representation` | experimental | Representation projection may change. |
| `actions.allowed.status` | stable_draft | Read-only/public-safe actions only. |
| `actions.blocked.status` | stable_draft | Must expose blocked unsafe actions. |
| `actions.future_gated.status` | stable_draft | Must expose gated actions without enabling them. |
| `rights` | stable_draft | Caveat block; never a rights-clearance claim. |
| `risk` | stable_draft | Caveat block; never a malware-safety claim. |
| `warnings` | stable_draft | Public warnings and blocked severities. |
| `limitations` | stable_draft | Standard limitation vocabulary. |
| `gaps` | stable_draft | Bounded absence and next-step notes. |
| `links` | experimental | Base-path-safe public links only. |
| `debug` | future | Disabled by default in public runtimes. |
| Private local paths | internal | Forbidden from public cards. |
| Raw source payloads | internal | Forbidden from public cards. |
| Credentials | internal | Forbidden from public cards. |
| Internal database row ids | internal | Forbidden unless later made public-safe by contract. |

## Lane Vocabulary

Stable-draft lanes are:

- `best_direct_answer`
- `installable_or_usable_now`
- `inside_bundles`
- `official`
- `preservation`
- `community`
- `documentation`
- `mentions_or_traces`
- `absence_or_next_steps`
- `still_searching`
- `other`
