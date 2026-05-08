# Eureka Node Policy

Eureka Node policy is the boundary layer between node identity and future node behavior.

The manifest says which node exists. The policy says what that node may do, what it must not do, and which review gates are required before any proposed output moves downstream.

## Allowed Current Work

Current policies may allow repo-local inspection, contract validation, pack validation, local eval analysis, local gap summaries, observation-candidate preparation, source-lead preparation, dry-run reports, review packets, and human review requests.

These actions operate on committed repo artifacts or pending manual records only. They do not authorize runtime execution.

## Source And Network Boundary

Current examples keep network disabled. Source access is limited to repo-local, committed fixture, manual-human, or no-autonomous modes unless a future source policy explicitly approves more.

Future source access needs source ID, allowed path or endpoint, rate limits, cache TTL, contact policy, kill switch, terms/robots posture, privacy posture, rights/risk posture, operator approval, and human review.

## Output Truth Boundary

Node policy allows proposed outputs such as dry-run reports, observation candidates, source leads, WorkUnit seeds, evidence drafts, candidate drafts, pack drafts, and review items.

Those outputs are not public truth, accepted evidence, observed baselines, or master index mutations.

## Review Gates

Review gates cover human review, source policy, evidence, candidate, pack, master index, rights, risk, privacy, network, hosted behavior, and legal or rights stop decisions. Approval means a next safe action is allowed; it does not by itself promote truth.

## Deferred

Node runtime, local private state, pack import/export behavior, hosted workers, source connectors, live probes, and WorkUnit execution remain future tasks.
