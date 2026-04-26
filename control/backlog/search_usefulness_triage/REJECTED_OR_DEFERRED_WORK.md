# Rejected Or Deferred Work

This triage intentionally rejects or defers work that would blur evidence, overclaim maturity, or skip the selected usefulness wedge.

| Work | Status | Why deferred | Prerequisite before reconsidering |
| --- | --- | --- | --- |
| Live crawling | Deferred | Current source capability and recorded fixture coverage are not ready. Crawling would make behavior unstable. | Source capability model, recorded fixtures, no-network tests, explicit operator policy |
| Google scraping | Rejected | External baselines must be manual evidence records. Scraping Google is out of scope. | None in this repo lane |
| Internet Archive scraping | Rejected for this phase | IA coverage should begin with recorded fixtures, not live scraping or API dependence in required tests. | Source capability model and recorded IA fixture policy |
| Broad source federation | Deferred | Too many source families before capability depth would create vague coverage claims. | Source coverage/capability model plus first recorded source pack |
| Vector search | Deferred | Current failures are source/planner/member/evidence gaps, not vector recall gaps. | Stable corpus, explicit relevance benchmark, and accepted retrieval policy |
| LLM planning | Deferred | Query planner gaps should be solved deterministically first; AI remains optional and non-authoritative. | Deterministic planner baseline plus evidence-bounded AI policy tests |
| Trust scoring | Deferred | Source truth and disagreement must remain visible before scoring is introduced. | Claim/evidence model and disagreement tests |
| Installer automation | Deferred | Eureka should find and explain objects before executing or installing anything. | Acquisition/action policy, safety review, compatibility evidence |
| Production hosting | Deferred | Public alpha is constrained and not production. Auth/TLS/accounts/abuse controls are absent. | External deployment posture and operator approval outside this task |
| Native apps | Deferred | Backend usefulness must improve before GUI shell work. | Stable backend usefulness and public boundary contracts |
| Broad Rust rewrite | Deferred | Python remains oracle; Rust moves seam-by-seam through parity. | Useful Python seam stabilized and golden outputs captured |
| Shared cloud memory | Deferred | Resolution Memory v0 is local/manual. Privacy and invalidation are not ready. | Privacy policy, invalidation model, explicit sharing rules |
| Full identity clustering | Deferred | Vague identity queries need source/evidence first. | Source coverage and claim/disagreement model |
| Production queue/worker system | Deferred | Local Worker v0 is synchronous. Current needs are eval/source/planner guardrails. | Durable task contracts and hosting posture |
| Compatibility oracle | Rejected as framing | Compatibility must remain evidence-backed with unknown outcomes. | Evidence pack and confidence model, not an oracle |
| Modern `/app` workbench | Deferred | Surface polish would hide backend usefulness gaps. | Source/planner/member/compatibility improvements |
| Old-browser `/lite` surface implementation | Deferred | Public-alpha posture and backend usefulness come first. | Clear public-alpha demo scope and compatibility surface strategy |

No item here should be implemented as part of Search Usefulness Backlog Triage v0.
