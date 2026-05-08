# OBS-REPLAN-01 Agent-Assisted Observation Workflow

OBS was replanned because manual-only observation is too expensive to block the rest of Eureka development. Manual Observation Batch 0 remains the gold-standard calibration lane, while agents may prepare candidates, source leads, and WorkUnit seeds for human review.

This task adds:

- Agent-assisted observation workflow docs.
- Candidate review, source access, and parallel development policies.
- ObservationCandidate and ObservationReviewDecision contracts.
- Policy inventories, public-safe examples, validators, summarizer, tests, and audit evidence.

Agents may run repo-local evals, inspect committed fixtures, mine local failure reports, and prepare review packets. Agents must not scrape, crawl, open browsers, call APIs, query live sources, fabricate evidence, or turn candidates into observed baselines.

Humans approve, reject, tune, and grade. Approval chooses the next safe action; it does not create evidence truth.

Main development may continue in parallel with OBS unless a task specifically depends on completed manual baseline evidence.

Validation:

```powershell
python scripts/validate_agent_assisted_observation_policy.py
python scripts/validate_observation_candidate.py
python scripts/summarize_observation_candidates.py
python -m unittest discover -s tests -t .
```

Next task: TRACK-B-01 - Eureka Node manifest contract.
