# H3_OS_PACKAGE_WAVE_POSTMORTEM

Run H3 postmortem after policy packs, fixtures, and live-probe envelopes exist. Preserve no live calls by default, no repository index sync, no downloads, no package manager invocation, no installs, no execution, and no truth acceptance.

Validation commands: `python scripts/validate_h3_os_package_review_quality_audit.py`, `python scripts/audit_h3_os_package_archive_wave.py --check`, and focused H3 review unit tests.
