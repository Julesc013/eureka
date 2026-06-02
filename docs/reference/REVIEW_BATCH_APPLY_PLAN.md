# Review Batch Apply Plan

The apply plan records the candidate, need, and absence rows selected for temp
local apply.

Required properties:

- `apply_target` is `temp_explicit_instance`
- operator instance apply is false
- rollback is required
- public/master/reviewed index mutation is false
- artifact, download, malware-clean, rights, compatibility, scan, and OCR
  claims are false

The plan is validated before any temp write occurs.
