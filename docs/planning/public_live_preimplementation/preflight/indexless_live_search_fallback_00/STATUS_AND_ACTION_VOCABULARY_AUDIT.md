# Status And Action Vocabulary Audit

## Status Vocabulary

| Canonical status | Repo path if present | Current names or synonyms | Public alpha visibility | Operator visibility | Index eligibility | Evidence requirement | Review requirement | Fallback behavior | Conflicts or gaps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `verified` | planning vocabulary; public UX cards; reviewed index paths | `verified`, `reviewed_metadata_record`, `reviewed_source_lead`, `ia_reviewed_local` | allowed only for reviewed records | visible | reviewed/public index only | required | required before display as verified | fallback must never emit | Runtime uses limited reviewed statuses that are not equivalent to verified artifact truth. |
| `candidate` | `runtime/candidate_store/runtime.py`, public search candidate cards | `needs_review`, `candidate_results_only`, `archive_org_metadata_candidate` | allowed if labeled | visible | candidate index or candidate lane only | source observation or candidate summary | required for promotion | fallback may emit | Needs mapping from `needs_review` to public `candidate`. |
| `need` | `runtime/search/need/**`, contracts/query | `proposed`, `open`, `waiting_for_policy`, `known_need` | allowed if public-safe | visible | need/absence lane, not reviewed index | absence or local miss context | review if promoted/public persisted | fallback may emit when no usable candidate | Contract public runtime flags are future/disabled. |
| `near_miss` | `runtime/candidate_store/runtime.py`, IA candidate kinds, absence reports | `ia_near_miss_candidate`, absence near matches | allowed if labeled | visible | candidate/absence lane | local related result or source observation | required for promotion | emit only if existing support applies | Existing near-match records and candidate near-miss are separate shapes. |
| `mention_only` | not found as canonical runtime status | weak source mention concepts only | maybe, if explicitly labeled | visible | no reviewed index | source observation | review required | fallback can defer to candidate/need unless clear mapping exists | Missing current first-class status. |
| `policy_blocked` | source action policy, SearchNeed WorkUnit policy, public error codes | `blocked_by_policy`, `blocked`, `live_probes_disabled`, `downloads_disabled` | allowed as non-result/degraded state | visible | no result index | policy decision | no promotion | fallback must emit for disabled fallback/source | Naming varies. |
| `private_local` | public alpha filters, SearchNeed local/private flags | `local_private`, private path blockers | disallowed except redacted notice | visible locally | no public index | privacy classification | review/privacy gate | fallback must not expose private data | Existing runtime Need defaults public_safe_summary_allowed=false. |
| `superseded` | review queue and SearchNeed states | `superseded`, `superseded_future` | allowed if reviewed/public-safe | visible | depends on review | review event | required | not a fallback output | Good enough for later review ledger. |
| `rejected` | review queue and candidate states | `rejected_wrong_object`, `rejected_low_quality`, `reject_candidate` | allowed only as public-safe review state | visible | no reviewed result | review rationale | required | not a fallback output | Runtime has more detailed rejection names. |
| `unknown` | checked source summaries, compatibility and public fields | `unknown`, `unavailable`, `failed` | allowed as degraded state | visible | no result index | notice or failure reason | no promotion | fallback can emit unavailable/unknown for failures | Canonical list says unknown; prompt also permits unavailable. |

## Action And Affordance Vocabulary

| Canonical affordance | Current repo names | Classification | Notes |
| --- | --- | --- | --- |
| `view` | `view`, `read`, `view_need` | public_alpha_allowed | Use as safe public navigation/read action. |
| `inspect_evidence` | `view_provenance`, `inspect`, evidence pages | public_alpha_allowed | Map current public action IDs to canonical affordance in future semantic alignment. |
| `compare` | `compare` route/action manifests | public_alpha_allowed if read-only | Merge/dedupe effects remain disabled. |
| `cite` | `cite`, `copy_citation` | public_alpha_allowed | Manifest/export-only citation is safe. |
| `export_manifest` | `export_manifest`, `export-resolution-manifest` | public_alpha_allowed if manifest-only | Must remain no import/submission/download side effect. |
| `watch_need` | no stable public runtime action found | future_gated | Could be read-only interest marker later; not needed for fallback v1. |
| `report_issue` | no stable public runtime action found | future_gated | Public mutation channel; keep disabled. |
| `review_candidate` | `review_candidate`, review routes | operator_only | Public search marks future-gated. |
| `promote` | `promote`, `accept`, promotion preview | operator_only | Public candidate promotion blocked. |
| `reject` | review decision routes | operator_only | Public rejection blocked. |
| `rebuild_index` | local reviewed-index refresh/rebuild | operator_only | Public must not expose. |

## Unsafe Current Or Future Actions

These remain public-alpha disallowed or unsafe for v1:

- download
- install or execute
- upload
- extract
- live_source_fanout
- mutate_public_index
- mutate_master_index
- accept/promote from public routes

## Implementation Requirement

Fallback output must map to:

- `candidate`
- `need`
- `near_miss` only where existing support applies
- `policy_blocked`
- `unknown` or `unavailable`

Fallback must not map to `verified`.
