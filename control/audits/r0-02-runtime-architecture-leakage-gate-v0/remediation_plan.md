# Remediation Plan

## Recommended Sequence

- R0-03 — Contract taxonomy refactor
- R0-04 — Source observation production seam
- R0-05 — Durable source cache store

## Do Not Do

- do not rename or move runtime paths inside R0-02
- do not silently bless known leaks forever
- do not resume F0 until at least the R0-02 gate is active and downstream remediation is scheduled
- do not promote dev to main while production-path task vocabulary remains unresolved
