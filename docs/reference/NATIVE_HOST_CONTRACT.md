# Native Host Contract

`contracts/native/native_host.v0.json` records optional and future native build hosts.

Host records describe supported lanes, expected toolchains, manual steps, and evidence requirements. They do not install toolchains, run package restores, download dependencies, or require a build to pass when the host is unavailable.

Current validation is static unless a local compiler or build tool is already available and can run without network or installation.
