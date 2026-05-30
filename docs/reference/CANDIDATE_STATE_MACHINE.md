# Candidate State Machine

Public mutation is disabled. System/runtime transitions may only move through
the small automatic set. Operator transitions require explicit operator approval
and still do not create accepted truth by themselves.

`accepted_local_reviewed` records that a separate local review path accepted a
candidate; it is not a public launch or production readiness claim.
