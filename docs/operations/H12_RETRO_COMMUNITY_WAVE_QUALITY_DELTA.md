# H12 Retro Community Wave Quality Delta

Use the quality delta to compare H12 fixture/replay/review coverage and known gaps. Do not use it as production retro archive coverage, search quality, rights, safety, authenticity, checksum, compatibility, installability, or playability proof.

Validation:

- `python scripts/validate_h12_retro_community_review_quality_audit.py`
- `python scripts/integrate_h12_retro_community_review.py --input-dir examples/connectors/h12_retro_community/replay_results --check`
- `python scripts/summarize_h12_retro_community_quality_delta.py --input-dir examples/connectors/h12_retro_community/review_integration --check`
- `python scripts/audit_h12_retro_community_wave.py --check`

No-goals preserved: no new live source calls, no broad retro/community/archive/web/forum search, no downloads, no extraction, no execution, no acquisition actions, no uploads, no hash submissions, no scraping/crawling, no bypass, no restricted-source access, no public/master index mutation, and no truth acceptance.
