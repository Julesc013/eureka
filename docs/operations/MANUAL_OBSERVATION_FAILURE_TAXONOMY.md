# Manual Observation Failure Taxonomy

Manual observations should classify gaps honestly. Use one or more classes when a result is missing, weak, misleading, incomplete, or not comparable.

| Class | Meaning |
| --- | --- |
| `source_gap` | The relevant source or collection appears absent from Eureka or the external baseline. |
| `capability_gap` | The system cannot express or execute the needed search capability. |
| `ranking_gap` | Useful evidence exists but is not ranked visibly or early enough. |
| `extraction_gap` | Source content exists but needed metadata/member/snippet extraction is missing. |
| `compatibility_gap` | Compatibility target, platform, version, or environment is unclear or missing. |
| `representation_gap` | The result exists but is represented at the wrong level, such as parent instead of member. |
| `identity_gap` | Identity is ambiguous, duplicated, renamed, or not resolvable. |
| `temporal_version_gap` | The right time/version boundary is missing or unclear. |
| `rights_or_policy_block` | Rights, policy, robots, account, or access limits block evaluation. |
| `query_interpretation_gap` | The system interpreted the query differently from the intended need. |
| `near_match_only` | A related result exists but does not satisfy the need. |
| `noisy_result_list` | Results are too broad, spammy, or mixed to identify useful evidence quickly. |
| `dead_link_or_unavailable` | A visible result points to an unavailable or dead locator. |
| `ambiguous_need` | The query itself is too ambiguous for fair scoring without more context. |
| `external_baseline_unavailable` | The external system or result page could not be reached manually. |
| `observation_incomplete` | The session happened but required fields are incomplete. |
| `not_evaluable` | The slot cannot be evaluated under the protocol. |

The machine-readable taxonomy lives at `control/inventory/observations/manual_observation_failure_taxonomy.json`.

Failure classes do not complete pending observation slots. A pending slot remains pending until a human-operated manual session records the required evidence fields.
