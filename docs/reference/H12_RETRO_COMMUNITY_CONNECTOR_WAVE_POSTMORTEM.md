# H12 Retro Community Connector Wave Postmortem

The H12 postmortem summarizes what worked, what failed, fixture gaps, live-probe gaps, normalizer gaps, policy gaps, community-lane trust gaps, and next-phase routing. It cannot auto-approve future connectors.

Validation:

- `python scripts/validate_h12_retro_community_review_quality_audit.py`
- `python scripts/integrate_h12_retro_community_review.py --input-dir examples/connectors/h12_retro_community/replay_results --check`
- `python scripts/summarize_h12_retro_community_quality_delta.py --input-dir examples/connectors/h12_retro_community/review_integration --check`
- `python scripts/audit_h12_retro_community_wave.py --check`

No-goals preserved: no new live source calls, no broad retro/community/archive/web/forum search, no downloads, no extraction, no execution, no acquisition actions, no uploads, no hash submissions, no scraping/crawling, no bypass, no restricted-source access, no public/master index mutation, and no truth acceptance.
