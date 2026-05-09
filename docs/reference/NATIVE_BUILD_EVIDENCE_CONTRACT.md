# Native Build Evidence Contract

`contracts/native/native_build_evidence.v0.json` records manual or future build
evidence for native lanes.

The contract separates source skeleton presence from verified build evidence.
Old-toolchain lanes may remain `manual_build_required` until a suitable host
opens, builds, launches, and records smoke evidence under a reviewed audit path.

Build evidence is not release evidence and does not create rights, safety,
installability, or production-readiness claims.
