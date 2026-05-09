# Native Build Evidence Policy

C-BUNDLE-01 does not require native builds to pass on every workstation.

Static validation is required. Optional compile/build checks may run only when the local toolchain is already available and does not need network restore, dependency installation, package downloads, or project mutation.

Build outputs and binaries must not be committed. Evidence belongs under explicit audit generated paths, not product runtime paths.
