# Validation

- git diff --check: pass
- full unittest discovery: pass, 4323 tests
- architecture boundaries: pass
- runtime leakage validator: pass, with warning-only exact allowlist debt
- local machine proof: pass
- LAN smoke: pass with external-device limitation
- clean-machine proof: pass with warning-only skipped local instance state
- generated artifact cleanliness: requires post-commit rerun because this audit pack is generated output
- AIDE: pass with verify warnings only
