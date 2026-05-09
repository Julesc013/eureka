# IA-BUNDLE-02 Bounded Metadata Live Probe

Status: `blocked`.

IA-BUNDLE-02 adds the fail-closed live-probe boundary for one Internet Archive
metadata endpoint read. The committed policy state does not approve live access,
so no external call was attempted. Generated audit artifacts show the blocked
preflight result and not-created source-cache, evidence, and review-seed
previews.

No broad IA search, advancedsearch, download, item file fetch, scraping,
public-query fanout, source sync, public-index mutation, master-index mutation,
evidence acceptance, candidate acceptance, public truth creation, hosting,
uploads, accounts, telemetry, model call, or provider call is enabled.

## Generated Evidence

- `generated/sample_live_probe_result.json`
- `generated/sample_source_cache_candidate_from_live_probe.json`
- `generated/sample_evidence_candidate_preview_from_live_probe.json`
- `generated/sample_review_queue_seed_from_live_probe.json`
- `generated/sample_live_probe_summary.md`
