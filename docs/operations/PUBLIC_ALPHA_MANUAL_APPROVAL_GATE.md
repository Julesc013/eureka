# Public Alpha Manual Approval Gate

Launch-candidate readiness is not launch readiness. Manual operator approval is
required before any task may deploy, publish, enable live source fanout, enable
public mutation, or claim production/public launch readiness.

Approval must identify:

- exact commit
- deploy mode
- rollback path
- expected public surface
- disabled capabilities
- smoke checks
- incident contact path

Without that explicit approval, the only valid next step from this gate is a
bounded deploy dry run.
