# Security Privacy And Policy Spec

## Public Safety

- public routes are read-only
- public mutation disabled
- public live fanout disabled unless future gate enables it
- downloads, installs, extraction, execution, uploads, and model/provider calls
  disabled for public v1

## Private Safety

- Workbench requires operator authorization
- raw local state and raw source responses are not public by default
- query logs are minimized and redacted according to future privacy policy

## Policy Switches

- fallback disable switch
- source-family disable switch
- review freeze switch
- renderer/profile disable switch
- public route safe mode

