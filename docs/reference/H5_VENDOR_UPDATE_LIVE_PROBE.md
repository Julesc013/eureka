# H5 Vendor/Update Live Probe

H5 vendor/update live probes are approval-gated metadata observations for vendor, update, driver, firmware, and runtime sources. The default mode is offline preflight. A live call requires `--live` and source-specific committed approval for the exact request key, endpoint or metadata class, rate limit, cache decision, kill switch, and output path.

The probe may emit candidate and preview artifacts only: normalized metadata records, vendor identity candidates, driver/device compatibility candidates, firmware/update candidates, runtime redistributable candidates, payload metadata candidates, source-cache previews, evidence previews, review seeds, and connector health summaries.

It does not enable catalog sync, downloads, vendor tools, package managers, firmware flashing, install, execution, public index mutation, master index mutation, or truth acceptance.
