# H5 Vendor Update Driver Model

H5 reuses the Source OS split between control inventory, source records, connector-family assignments, examples, coverage previews, scorecards, and audit reports. The model is intentionally conservative because vendor drivers, firmware, and runtime packages are high-risk artifacts.

H5-BUNDLE-01 defines policy and pack structure only. H5-BUNDLE-02 is expected to add committed fixture runtime and normalizers. H5-BUNDLE-03 may add approved metadata-only probes, but only after committed gates explicitly allow bounded requests.

The model treats vendor metadata as source observation material, never as public truth. Official-looking source metadata does not by itself prove vendor identity, compatibility, authenticity, installability, malware safety, rights clearance, or production coverage.
