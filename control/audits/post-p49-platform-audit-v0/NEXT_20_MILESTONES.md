# Next 20 Milestones

| Rank | Milestone | Work gate | Audit classification | Notes |
|---:|---|---|---|---|
| 1 | P51 Post-P50 Remediation Pack | Codex-safe | `planning_only` | Repair audit/doc/test metadata drift and tighten validators. |
| 2 | Static Deployment Evidence / GitHub Pages Repair | operator-gated | `operator_gated` | Enable Pages/rerun workflow if operator access exists. |
| 3 | Manual Observation Batch 0 Execution | human-operated | `manual_pending` | Fill real external baseline observations. |
| 4 | Public Search Production Contract v0 | Codex-safe | `contract_only` | Define hosted-readiness contract without deploying. |
| 5 | Hosted Public Search Wrapper v0 | operator-gated | `operator_gated` | Requires host, rate limits, logging, rollback. |
| 6 | Public Search Index Builder v0 | Codex-safe | `planning_only` | Build from governed fixture/pack inputs, not public queries. |
| 7 | Static Site Search Integration v0 | Codex-safe | `implemented_static_artifact` | Static handoff integration only unless backend exists. |
| 8 | Public Search Safety Evidence v0 | Codex-safe | `contract_only` | Expand abuse/privacy evidence. |
| 9 | Hosted Public Search Rehearsal v0 | production-gated | `operator_gated` | Only after hosted wrapper and safety evidence. |
| 10 | Query Observation Contract v0 | Codex-safe | `contract_only` | Privacy-filtered query observation shape. |
| 11 | Shared Query/Result Cache v0 | Codex-safe | `planning_only` | Shared cache design with poisoning controls. |
| 12 | Search Miss Ledger v0 | Codex-safe | `planning_only` | Misses become durable, reusable search needs. |
| 13 | Search Need Record v0 | Codex-safe | `contract_only` | Govern reusable search-need records. |
| 14 | Probe Queue v0 | approval-gated | `approval_gated` | Queue only, no live execution without approval. |
| 15 | Candidate Index v0 | Codex-safe | `planning_only` | Candidate index separated from truth/master index. |
| 16 | Candidate Promotion Policy v0 | Codex-safe | `contract_only` | Slow truth gate for candidate promotion. |
| 17 | Known Absence Page v0 | Codex-safe | `implemented_static_artifact` | Static absence surface, no live claims. |
| 18 | Query Privacy and Poisoning Guard v0 | Codex-safe | `contract_only` | Must precede runtime query learning. |
| 19 | Source Cache and Evidence Ledger v0 | Codex-safe | `contract_only` | Cache/ledger contract before live source work. |
| 20 | IA Metadata Live Probe Approval Pack v0 | approval-gated | `approval_gated` | Approval pack only; no live probe implementation. |
