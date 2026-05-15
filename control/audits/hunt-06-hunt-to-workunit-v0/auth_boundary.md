# Auth Boundary

Persisting WorkUnits from a SearchNeed is operator-token gated and localhost-only.

Plan-only CLI preview is read-only. Local POST plan and persist routes are token gated by the existing local operator mutation boundary.

LAN mutation attempts return 403.
