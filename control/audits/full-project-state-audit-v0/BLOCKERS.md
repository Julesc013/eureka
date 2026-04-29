# Blockers

Hard blockers:

- Cargo is unavailable in this local environment, so Cargo-backed Rust checks are not verified.
- Manual external baseline comparison is blocked until human observations exist.
- Native GUI skeleton implementation is blocked pending explicit human approval and Windows build-host/toolchain verification.
- Relay prototype implementation is blocked pending explicit human approval, bind-scope approval, input-root approval, and privacy/security review.
- Internet Archive Live Probe v0 is blocked pending explicit human approval and live probe gateway review.
- Hosted public-alpha rehearsal is blocked pending operator signoff and checked GitHub Actions/Pages evidence.

Policy blockers:

- Downloads, installers, package-manager handoff, executable launch, malware scanning, rights clearance, local cache runtime, private ingestion, telemetry, accounts, and cloud sync remain blocked until separate approved policy/implementation milestones.

Not blockers:

- Local Python test/eval/static/publication validation is currently passing.
- Rust structure/parity planning checks pass without Cargo.
