# Public Search Result Card Contract v0

Status: implemented as a contract reference and used by Local Public Search Runtime v0.

Public Search Result Card Contract v0 defines the public result-card envelope
for Eureka search displays and JSON responses. The card is the unit that local
`/search` HTML and `/api/v1/search` JSON now emit in Local Public Search Runtime
v0, and that lite/text surfaces, native clients, relay clients, snapshot
consumers, and contribution/review tooling may consume after their own contracts
allow it.

This contract does not make public search hosted, does not add static search
handoff, does not enable live probes, and does not enable downloads, installers,
execution, uploads, or local path search. It does not claim production ranking
quality, production API stability, malware safety, rights clearance, or
production readiness.

In short: the result card is not a production ranking guarantee, must not claim
malware safety, must not claim rights clearance, and prepared the safety
milestone, Public Search Safety / Abuse Guard v0, rather than replacing it.
Public Search Safety / Abuse Guard v0 is now implemented as guardrails, and
Local Public Search Runtime v0 uses those guardrails for local/prototype result
cards. Hosted public exposure still waits for later rehearsal and operator
approval.

## Contract Files

- Schema: `contracts/api/search_result_card.v0.json`
- Examples: `contracts/api/examples/search_result_card_*.v0.json`
- API response alignment: `contracts/api/search_response.v0.json`
- Audit pack: `control/audits/public-search-result-card-contract-v0/`

## Required Card Shape

Every public result card must contain:

- `schema_version` and `contract_id`
- `stability`
- `result_id`, `title`, and `record_kind`
- `result_lane`
- `user_cost`
- `source`
- `identity`
- `evidence`
- `compatibility`
- `actions`
- `rights`
- `risk`
- `warnings`
- `limitations`
- `gaps`

Optional blocks include `subtitle`, `summary`, `matched_query_terms`,
`why_matched`, `why_ranked`, `parent_lineage`, `member`, `representation`,
`temporal`, `links`, and `debug`. Optional blocks must remain public-safe and
must not leak private paths, raw source payloads, credentials, local store roots,
or live fetch locators.

## Lanes And User Cost

`result_lane` uses the bounded vocabulary already aligned with the engine:

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

`user_cost.score` is an integer from 0 through 9. Lower scores mean less user
detective work. The score is a deterministic stable-draft hint, not a
production ranking guarantee. Cards must include `user_cost.reasons` so old and
text clients can explain the score without rich UI.

## Source And Identity

The `source` block identifies the public source family, coverage depth, source
posture, and whether the source was checked as a local index, recorded fixture,
static summary, future live probe, or not checked. In v0, future live probe is a
label for future contracts only; it does not enable live probes.

The `identity` block carries a public-safe target reference plus optional
resource, representation, member, native, object, or state identifiers.
Identity status is explicit: exact, candidate, ambiguous, unresolved,
synthetic_member, article_segment, or unknown. Private local paths and internal
database row ids are not public identity.

## Evidence And Compatibility

The `evidence` block carries public-safe summaries, counts, provenance notes,
and missing-evidence notes. It must not include raw source payloads by default.

The `compatibility` block carries status, target platforms, architecture,
evidence summaries, confidence, caveats, and unknowns. It must not claim
universal compatibility. Compatibility status is a public signal, not proof that
an artifact has been tested on every platform.

## Parent, Member, And Representation

Cards support smallest-actionable-unit behavior through `member`,
`parent_lineage`, and `representation`. A member result may explain that a small
driver, article segment, file, or documentation member is more useful than the
larger bundle that contains it.

Representation fields describe public-safe representation metadata such as kind,
media type, file name, size, checksum, and limitations. They do not expose
private local paths or executable handoff URLs.

## Actions

Actions are split into `allowed`, `blocked`, and `future_gated`.

Allowed v0 concepts are read-only or inspection-oriented:

- `inspect`
- `preview`
- `read`
- `cite`
- `export_manifest`
- `view_provenance`
- `compare`
- `view_source`
- `view_absence_report`

Blocked or future-gated concepts include:

- `download`
- `download_member`
- `mirror`
- `install_handoff`
- `package_manager_handoff`
- `emulator_handoff`
- `vm_handoff`
- `execute`
- `live_probe`
- `restore_apply`
- `uninstall`
- `rollback`
- `upload`
- `submit_private_source`

Every action entry has an `action_id`, `status`, `reason`, optional
`policy_reference`, and optional future-policy/confirmation flags. A future
runtime must not treat a future-gated action as enabled.

## Rights And Risk

The `rights` block records public metadata posture, source-term caveats,
restricted/review-required states, or unknown rights status. It must not claim
rights clearance. `distribution_allowed: "unknown"` is not permission.

The `risk` block records executable-risk posture and malware-scan status. It
must not claim malware safety. In v0, executable artifacts are not made
downloadable or executable through a result card.

## Warnings, Limitations, And Gaps

Warnings have a type, message, and severity: `info`, `caution`, `warning`, or
`blocked`.

Common limitations include fixture-backed evidence, limited source coverage,
limited compatibility evidence, no live probe, no download, no install, no
execute, no upload, no malware scan, no rights clearance, external-baseline
pending, static summary only, local-index-only, and not production ranking.

Gaps explain bounded absence and next actions. A card may say that the local
index did not find a result, but it must not imply that the live web or external
archives were checked.

## Field Stability

The field matrix in
`control/audits/public-search-result-card-contract-v0/RESULT_CARD_FIELD_MATRIX.md`
classifies fields as stable-draft, experimental, volatile, internal, or future.
Stable-draft fields are intended for old-client and future-runtime continuity.
Experimental fields may change before a runtime implementation. Internal fields
are forbidden from public cards.

## Old-Client Rendering

Lite HTML and text clients should render at least title, lane, user-cost score
and label, source id/family, public target ref, first evidence summary, allowed
inspect/read actions, blocked unsafe actions, warnings, and limitations. They
should degrade by dropping rich panels first, not by hiding source, uncertainty,
or safety posture.

## Relationship To Other Contracts

Public Search API Contract v0 uses this card as the canonical shape for
`results[]` in `contracts/api/search_response.v0.json`. The API contract remains
contract-only.

The Action Download Install Policy governs blocked and future-gated actions.
Executable Risk Policy governs executable-risk caveats. Rights and Access Policy
governs rights caveats. Native, relay, and snapshot contracts may reference this
card as a future input shape, but this milestone does not implement native
clients, relay runtime, or snapshot reader runtime.

Future reviewed evidence packs may supply public-safe evidence summaries,
source locators, compatibility caveats, member notes, and absence notes for
result cards. Evidence Pack Contract v0 does not import those packs, make claims
canonical, or change current local public search runtime behavior.
Future reviewed index packs may supply public-safe coverage and record-summary
metadata for result cards. Index Pack Contract v0 does not import or merge
those packs, export raw databases or caches, make summaries canonical proof, or
change current local public search runtime behavior.
Future reviewed contribution packs may supply accepted public deltas or review
notes for result cards only after Master Index Review Queue Contract v0-governed
review. Contribution Pack Contract v0 does not upload, import, moderate,
accept, or make contributed records canonical proof, and it does not change
current local public search runtime behavior.
Source/Evidence/Index Pack Import Planning v0 does not change result cards.
Future validated or quarantined packs remain local claims/candidates and must
not appear in public result cards until a later explicit local-index or
master-index review milestone permits reviewed public output.
AI Provider Contract v0 does not add AI result cards or generated snippets.
Future AI explanations may appear only as typed, review-required suggestions
after separate output validation and public-search contract updates. They are
not canonical truth, rights clearance, malware safety, or ranking authority.
Typed AI Output Validator v0 adds that offline output validation step through
`scripts/validate_ai_output.py`, but it does not display AI output on result
cards, import AI output into evidence/contribution packs, or alter ranking.
Pack Import Report Format v0 may record future validation outcomes for packs
or typed AI output bundles before reviewed public records exist. It does not
change result-card fields, import packs, stage packs, mutate local indexes,
upload, or mutate public search or the master index.

Public Search Index Builder v0 projects the controlled generated public index
documents back into this result-card shape for the local/prototype public-search
runtime. Each generated document carries source, evidence, compatibility,
action, warning, and limitation summaries; blocked actions still include
download, install handoff, execute, and upload. The generated index does not
prove source truth, rights clearance, malware safety, production ranking
quality, or hosted availability.

## Runtime Preconditions

Local Public Search Runtime v0 emits public result cards after satisfying the
implemented Public Search Safety / Abuse Guard v0 policy, local index
ownership, public route validation, bounded query/result limits,
no-live-probe enforcement, action-policy enforcement, and tests proving no
downloads, installers, execution, uploads, arbitrary URL fetch, local path
search, private data exposure, malware-safety claim, rights-clearance claim, or
production API claim was added by accident.

Hosted public exposure must still pass the runtime readiness checklist at
`docs/operations/PUBLIC_SEARCH_RUNTIME_READINESS_CHECKLIST.md`; this checklist
does not approve hosted deployment by itself.
Public Search Rehearsal v0 now records local/prototype evidence that emitted
cards remain aligned with this contract for representative safe queries and
absence cases. It adds no hosted backend, live probes, downloads, installers,
uploads, execution, malware-safety claim, rights-clearance claim, telemetry, or
production ranking guarantee.

Public Search Safety Evidence v0 adds a broader pre-hosted safety check. It
verifies local result-card safety shape for safe public-search queries while
downloads, installs, execution, uploads, live probes, and local path access
remain blocked or disabled.

## Out Of Scope

This contract and local runtime do not implement hosted backend deployment,
live source probes, Internet Archive calls, Google
queries, arbitrary URL fetch, crawling, downloads, installers, uploads,
accounts, telemetry, native clients, relay runtime, snapshot reader runtime,
TLS, auth, rate limiting, process management, custom domains, production API
stability, or production readiness.
## P58 Rehearsal Alignment

P58 safe-query checks verify that local hosted search responses still expose
result-card safety shape, including source, evidence, compatibility, warnings,
limitations, and blocked dangerous actions.
## Query Observation Boundary

P59 Query Observation Contract v0 records only summary-level result posture for
future query intelligence. It does not copy result cards into a result cache,
does not publish query observations, and does not mutate candidate, local, or
master indexes.

## Shared Result Cache Boundary

P60 Shared Query/Result Cache v0 may summarize public-safe result-card fields
for future reuse. A cache entry is not the full result card, not source
evidence, not a download/install promise, not telemetry, and not master-index
truth.

## Search Miss Ledger Boundary

P61 Search Miss Ledger v0 may reference public-safe result-card summaries as
weak hits or near misses. A miss entry is not the full result card, not source
evidence, not a search need, not a probe job, not telemetry, and not
master-index truth.

## Search Need Record Boundary

P62 Search Need Record v0 may reference public-safe result-card summaries as
context for a scoped unresolved need. A need record is not the full result card,
not source evidence, not a probe job, not a candidate record, not telemetry, and
not master-index truth.

## Probe Queue Boundary

P63 Probe Queue v0 may reference public-safe result-card context only through
query observation, cache, miss, or search-need refs. A probe queue item is not
the full result card, not source evidence, not probe execution, not a candidate
record, not telemetry, and not master-index truth.
## P64 Candidate Index Note

Result cards are not candidate records. P64 candidate examples are provisional
contract artifacts and do not become public result cards, public action
targets, evidence acceptance, or master-index records.

## P65 Candidate Promotion Boundary

P65 adds Candidate Promotion Policy v0 as contract-only governance. Candidate promotion policy is not promotion runtime; candidate confidence is not truth; automatic promotion is forbidden; destructive merge is forbidden; future promotion assessment requires evidence, provenance, source policy, privacy, rights, risk, conflict, human, policy, and operator gates. No candidate, source, evidence, public index, local index, or master-index state is mutated.

## P66 Known Absence Page v0

Known Absence Page v0 is contract-only. It defines scoped absence, not global absence, for future no-result explanations with checked/not-checked scope, near misses, weak hits, gap explanations, safe next actions, privacy redaction, and no download/install/upload/live fetch. Known absence page is not a runtime page yet, not evidence acceptance, not candidate promotion, not master-index mutation, and not telemetry.
