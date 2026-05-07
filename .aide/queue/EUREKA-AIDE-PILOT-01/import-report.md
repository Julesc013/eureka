# Import Report

## Source Pack

- Pack path: `D:/Projects/AIDE/aide/.aide/export/aide-lite-pack-v0`.
- Pack id: `aide-lite-pack-v0`.
- Source repo: `julesc013/aide`.
- Source commit recorded by manifest: `e2088aed6dd32674c00b8d4701ce8c8be784fdde`.
- Source pack checksums: valid.
- Source boundary result: PASS.

## Import Method

The Q21 import command was available and dry-ran successfully:

```text
py -3 D:/Projects/AIDE/aide/.aide/scripts/aide_lite.py import-pack --pack D:/Projects/AIDE/aide/.aide/export/aide-lite-pack-v0 --target D:/Projects/Eureka/eureka --dry-run
```

Dry-run result: 127 operations, 0 conflicts, no provider/model/network calls.

The direct apply command was not used because its implementation copies every
`files/` root, including optional `core/` skeletons and AIDE reference docs
outside Q22's allowed target scope. The actual import was target-scoped and
manual from the exported pack.

## Imported

- Portable `.aide/**` pack metadata, scripts, policies, prompts, validators, adapter templates, and golden tasks.
- Safe `.aide.local.example/**` documentation only.
- Eureka-specific `.aide/memory/project-state.md`, `decisions.md`, and `open-risks.md`.
- Target-generated `.aide/context/**`, `.aide/reports/**`, `.aide/verification/**`, `.aide/generated/**`, `.aide/routing/**`, `.aide/cache/**`, and `.aide/controller/**` outputs.
- Managed AGENTS token-discipline sections.

## Excluded / Not Copied

- No AIDE source `.aide/queue/` history was copied.
- No AIDE source `.aide/memory/project-state.md` was copied.
- No AIDE source generated context was copied.
- No AIDE source generated reports, cache reports, route decisions, controller output, Gateway status, or provider status were copied.
- No AIDE source `.aide.local/` was copied.
- No `.env`, provider key, raw prompt log, raw response log, or secret was copied.
- Optional source `core/**` skeletons were not imported because they are outside Q22 target scope.

## Target State

- Target memory is Eureka-specific.
- Target snapshot and packets were generated inside Eureka.
- Actual `.aide.local/` is ignored and absent.
- Provider/model/network calls remained disabled and were not made.
