# H5 Vendor Update Quality Delta Report

The H5 quality delta counts review-readiness metrics from fixture and blocked-live-probe outputs. It reports source count, fixture source count, live probe source count, blocked source count, normalized record count, candidate counts, review seed counts, coverage preview counts, scorecard update counts, warnings, blockers, and known gaps.

It is not production search quality, production vendor coverage, exhaustive global coverage, official-status verification, compatibility verification, authenticity verification, safety verification, installability verification, rights clearance, malware safety, or automatic future connector approval.

Validation: `python scripts/summarize_h5_vendor_update_quality_delta.py --input-dir examples/connectors/h5_vendor_update_driver/review_integration --check`.
