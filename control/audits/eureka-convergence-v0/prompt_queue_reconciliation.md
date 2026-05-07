# Prompt Queue Reconciliation

This file reconciles three planning streams:

- old P-number milestones visible in roadmap, audit, and AIDE report files;
- current AIDE queue entries;
- the new Track A/B/D/C/E execution order.

## Classification Vocabulary

- `already_live`: implemented local/runtime behavior that exists in repo.
- `generated_not_live`: generated, static, local, or dry-run artifact that must
  not be treated as hosted/live production behavior.
- `live_without_prompt_number`: real local behavior exists, but the durable
  queue should classify it by track rather than continuing old P numbering.
- `obsolete_or_merged`: old prompt should not run as-is; merge its intent into a
  track task.
- `should_execute_next`: immediate next task.
- `should_merge_into_larger_prompt`: keep the evidence but fold into a track.
- `operator_gated`: requires operator environment, approval, credentials,
  deployment settings, or external evidence.
- `human_operated`: requires human observation rather than Codex automation.
- `approval_gated`: blocked on explicit policy/source/operator approval.
- `deferred`: intentionally later than current tracks.

## Old P-number Sequence

| Range or item | Classification | Reconciliation |
| --- | --- | --- |
| Early backend/source/planner/index/eval/runtime seams through P49-style platform audit | `already_live` | Treat as current repo baseline, not next prompts. |
| Static site, generated public data, lite/text/files, demo snapshots | `generated_not_live` | Use as Track A context and Track E static-hosting evidence; do not claim hosted backend. |
| P54 Hosted Public Search Wrapper | `generated_not_live` | Local/prototype wrapper only; merge any hosted concerns into Track E. |
| P55 Public Search Index Builder and P56 Static Site Search Integration | `generated_not_live` | Static/local search artifacts only; use as Track A and Track E inputs. |
| P57 Public Search Safety Evidence and P58 Hosted Public Search Rehearsal | `generated_not_live` / `operator_gated` | Local safety/rehearsal evidence only; actual hosted proof waits for Track E. |
| P59-P68 query observation, cache, miss ledger, search need, probe queue, candidate, promotion, absence, privacy, demand | `should_merge_into_larger_prompt` | Fold into Track B work-unit, candidate, source/evidence, and review-loop tasks. |
| P69-P76 source sync/cache/evidence and connector approval packs | `approval_gated` | Fold into Track B only after source policy and approval gates are explicit. |
| P77 public hosted deployment evidence | `operator_gated` | Track E only; do not rerun as a Codex deployment task. |
| P78 external baseline comparison | `human_operated` | Manual Observation Batch 0 must run before comparison claims. |
| P79-P85 object/source/comparison/identity/ranking contracts | `should_merge_into_larger_prompt` | Fold view-model, card, identity, ranking, and explanation posture into Track A. |
| P86-P97 runtime planning and ranking/explanation/deep-extraction planning | `deferred` / `should_merge_into_larger_prompt` | Use as Track B/Track E planning references; do not implement runtime broadly now. |
| P98/P99 source-cache/evidence-ledger local dry-run runtimes | `generated_not_live` | Useful Track B dry-run evidence; not public truth or runtime mutation. |
| Public search runtime integration audit and later local ranking dry-run audits | `generated_not_live` | Treat as audit/local dry-run context; not hosted production behavior. |

## Current AIDE Queue

| Queue item | Classification | Reconciliation |
| --- | --- | --- |
| `EUREKA-AIDE-FINAL-HANDOFF-01` | `already_live` | Completed handoff evidence; keep as AIDE operating context. |
| `EUREKA-AIDE-REAL-01` | `already_live` | Repo-health report exists; keep as current health context. |
| `EUREKA-CONVERGE-01` | `should_execute_next` during this audit | This audit completes it and promotes Track A. |
| `EUREKA-AIDE-REAL-02` | `obsolete_or_merged` | Superseded by Track A/B/D/C/E queue; deterministic eval improvements move into specific track tasks. |
| `EUREKA-AIDE-REAL-03` | `obsolete_or_merged` | Superseded by staged track queue. |
| `EUREKA-PRODUCT-READY-REVIEW-01` | `deferred` | Reappears after Track A/B/D/C evidence, not before. |

## New Track Order

| Track | Classification | Reconciliation |
| --- | --- | --- |
| A0 convergence | `already_live` after this audit | Current task. |
| Track A representation/view-model spine | `should_execute_next` | Starts with `TRACK-A-01`. |
| Manual Observation Batch 0 | `human_operated` | Runs after Track A establishes public/result view-model spine. |
| Track B node/contribution/source/evidence loop | `should_merge_into_larger_prompt` | Absorbs old query/source/cache/evidence/candidate P-number work. |
| Track D snapshot/relay substrate | `deferred` until after Track B foundations | Prepares offline and old-client substrate before native clients. |
| Track C native clients | `deferred` until Track D | Native work waits for snapshot/relay substrate and explicit approval. |
| Track E hosting/ops | `operator_gated` and last | Actual hosted public alpha, backend URL, DNS/TLS, rate limits, monitoring, and public claims. |
