# H5 Vendor Update Review Integration

H5 review integration consumes explicit fixture replay outputs and blocked or approved metadata-only live-probe outputs. It creates review seeds and previews for vendor identity, driver/device compatibility, firmware/update, runtime redistributable, payload metadata, source-cache, evidence, candidate promotion, coverage, scorecard, and source-pack updates.

It is not promotion. It does not accept vendor truth, driver identity truth, firmware identity truth, runtime identity truth, compatibility truth, authenticity truth, safety truth, source truth, evidence truth, candidate truth, or public truth.

Validation: `python scripts/integrate_h5_vendor_update_review.py --input-dir examples/connectors/h5_vendor_update_driver/replay_results --check`.
