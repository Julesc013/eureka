# Contract Summary

Staging Report Path Contract v0 makes stdout the default report output mode and
requires an explicit output path before any tool writes a report file.

It defines allowed synthetic/audit-safe committed report roots, forbidden repo
roots for local/private reports, future ignored local report roots, filename
safety, and redaction requirements.

The contract is not a report path runtime and not a staging runtime.
