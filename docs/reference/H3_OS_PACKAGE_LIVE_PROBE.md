# H3 OS Package Live Probe

H3 OS package archive live probes are approval-gated metadata-only observations. Current committed policy is fail-closed: offline validation and blocked preflight are allowed, but no live network request is made unless a future committed source-specific policy approves an exact bounded metadata request.

This artifact is not package identity truth, compatibility truth, dependency correctness, rights clearance, malware safety, installability verification, production archive coverage, source sync, repository index sync, package download permission, package-manager invocation permission, install permission, execution permission, public index mutation, or master index mutation.

The current H3-BUNDLE-03 examples use blocked outputs from committed policies. Fixture-equivalent outputs from H3-BUNDLE-02 remain available for H3-BUNDLE-04 review integration.

Validation:

- `python scripts/validate_h3_os_package_live_probe.py`
- `python scripts/run_h3_os_package_live_probe.py --source-id debian_snapshot --request-key example_package_metadata --check`
- `python scripts/summarize_h3_os_package_live_probe_outputs.py --input examples/connectors/h3_os_package_archives/live_probe_results --check`
