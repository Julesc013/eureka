# Next Task Handoff

## Recommended Task

Title: `EUREKA-AIDE-SELFTEST-01 - Repair imported AIDE Lite selftest fixture fallback`

Packet path: `.aide/context/latest-task-packet.md`

## Objective

Make the imported Eureka-local AIDE Lite `test` and `selftest` aliases pass
without copying optional source `core/**` roots, mutating the AIDE source repo,
or changing Eureka product code.

## Why This Task

Q26 confirms the main AIDE Lite workflow works in Eureka, but `test` and
`selftest` still fail in the temporary fixture path. This is the smallest
current reliability gap and directly improves confidence in the imported pack
before broader AIDE-guided Eureka work.

## Context Refs

- `.aide/context/latest-task-packet.md`
- `.aide/queue/EUREKA-AIDE-HANDOVER-01/evidence/validation.md`
- `.aide/queue/EUREKA-AIDE-HANDOVER-01/evidence/pack-refresh.md`
- `.aide/queue/EUREKA-AIDE-HANDOVER-01/evidence/quality-readiness.md`
- `.aide/scripts/aide_lite.py`
- `.aide/scripts/tests/test_export_import.py`
- `.aide/scripts/tests/test_aide_lite.py`
- `AGENTS.md`

## Allowed Paths

- `.aide/scripts/aide_lite.py`
- `.aide/scripts/tests/test_aide_lite.py`
- `.aide/scripts/tests/test_gateway_commands.py`
- `.aide/scripts/tests/test_provider_adapter.py`
- `.aide/scripts/tests/test_export_import.py`
- `.aide/queue/EUREKA-AIDE-SELFTEST-01/**`
- `.aide/context/**`
- `.aide/reports/**`
- `.aide/evals/runs/**`

## Forbidden Paths

- Eureka product source paths: `runtime/**`, `contracts/**`, `surfaces/**`,
  `site/**`, `crates/**`, `native/**`, and non-AIDE `tests/**`.
- Broad optional AIDE roots: `core/**` and source `docs/reference/**`.
- `.env`, `.aide.local/**`, `secrets/**`, raw prompts, raw responses,
  provider keys, live provider/model/network-call code.

## Validation Commands

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- `py -3 scripts/check_architecture_boundaries.py`
- `git diff --check`

## Acceptance Criteria

- `test` and `selftest` exit 0 in Eureka.
- No `core/**` or source `docs/reference/**` files are added to Eureka.
- Safe import mode still skips broad roots.
- Product source files are unchanged.
- Validation and evidence are recorded.
- Queue status ends `needs_review`.

## Review Packet Guidance

GPT-5.5 or Codex review should use `.aide/context/latest-review-packet.md` and
Q26 evidence only. Do not paste long repo history or the entire source tree.

## Token Estimate

- Latest task packet: 5767 chars / 1442 approximate tokens.
- Method: `chars / 4`.
- Budget status: within budget.
