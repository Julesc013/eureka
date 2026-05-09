# Native Project Skeleton Contract

`contracts/native/native_project_skeleton.v0.json` describes a native lane
skeleton: project files, source files, resource files, build status, consumed
contracts, forbidden dependencies, and product boundaries.

Current C-BUNDLE-02 skeletons are read-only and build-unverified or manual-build
required. They consume snapshot, relay, action, and blocked-action contracts.
They do not authorize live access, downloads, installers, execution, telemetry,
public index mutation, master index mutation, or truth acceptance.
