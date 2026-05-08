# Agent-Assisted Observation Workflow

Manual-only observation is too expensive for every hard query and source gap. Batch 0 remains the gold-standard human calibration lane, but agents may prepare review-gated candidates so the human role becomes approve, reject, tune, and grade rather than bulk data entry.

This workflow does not authorize external searches, browser automation, scraping, crawling, API calls, live probes, downloads, source connectors, or model/provider calls.

## Lanes

- OBS-MANUAL: human-operated baseline observations. This is the gold-standard calibration lane.
- OBS-AGENT: agent-prepared observation candidates, source leads, search-need seeds, and work-unit seeds. Human review is required.
- OBS-LOCAL: repo-local evals, fixture indexing, failure mining, hard-query analysis, and local regression reports.
- OBS-SOURCE: approved-source metadata observation only after explicit source policy, quota, contact/User-Agent, and kill-switch decisions.
- OBS-REVIEW: human approval, rejection, tuning, and grading for generated candidates and work units.

## Allowed Agent Work

Agents may run repo-local tests and evals, run search usefulness audits, mine local failure reports, inspect committed fixtures, summarize local source gaps, produce observation candidates, produce source-lead candidates, produce WorkUnit candidates, prepare review packets, prepare source policy decision packets, and prepare approved-source fixture normalizers.

## Source-Approval Required Work

Agents may only use an external source after a specific source policy approves the source family, endpoint or path, quota, timeout, retry behavior, cache TTL, contact/User-Agent posture, kill switch, terms/robots posture, privacy posture, rights/risk posture, and review gate.

Google web search observation by agents requires an approved API path or remains manual-human-only. Scraping Google result pages is never authorized by this workflow.

## Forbidden Agent Work

Agents must not scrape Google search results, automate browsers, crawl forums without approval, perform bulk Reddit ingestion, call external APIs without explicit source approval, probe live sources without approval, download binaries automatically, claim rights clearance, claim malware safety, treat AI summaries as evidence, treat source leads as accepted truth, or treat observation candidates as observed baselines.

## Candidate Boundary

An observation candidate is a proposed next step. It is not observed external baseline evidence. A source lead is a possible source to inspect or govern. It is not source validation. A demand signal is useful planning evidence. It is not object truth.

Approved candidates may later become SearchNeed seeds, WorkUnit seeds, EvidencePack candidates, or Candidate fixtures, but only after review. Approval decides safe downstream action; it does not make the candidate true.

## Review Gate

Every OBS-AGENT output must declare that human review is required, that it is not an observed baseline, that it is not evidence truth, and that master-index mutation is not allowed.
