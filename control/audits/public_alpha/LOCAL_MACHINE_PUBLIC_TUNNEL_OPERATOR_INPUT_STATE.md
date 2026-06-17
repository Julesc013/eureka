# Local Machine Public Tunnel Operator Input State

Task: `LOCAL-MACHINE-PUBLIC-TUNNEL-OPERATOR-INPUT-00`

Generated at: `2026-06-17T14:20:04Z`

## Repo State

- Branch: `dev`
- HEAD: `4d882a8add09aea79e11b979ab97414610a71a97`
- Initial worktree: clean
- `origin/dev...HEAD`: `0 0`
- Remote sync status: synced

## Operator Choice Artifact

The existing operator-choice machinery was reused to regenerate:

```text
.eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json
.eureka/public-alpha/exposure/operator-choice/latest/OPERATOR_CHOICE_REPORT.md
```

These files are generated under ignored `.eureka/` state and were not force-added.

Selected values:

- Exposure mode: `reverse_tunnel`
- Provider class: `provider_managed_https_tunnel`
- Provider name: `OPERATOR_REQUIRED`
- Public URL: `OPERATOR_REQUIRED`
- Public URL status: `operator_required`
- Provider HTTPS status: `operator_required`
- Staged record ID: `local-reviewed-record:1792f5ba3d54774c`
- Staged record ID status: present
- Remote sync status: synced
- Public exposure enabled: false
- Tunnel started: false

## Current Status

```text
BLOCKED_ON_OPERATOR_PROVIDER_URL
```

The provider name and public URL were not supplied by the operator. The generated
choice is safe and valid, but it is not ready for tunnel rehearsal.

Remaining blockers:

- `BLOCKED_ON_OPERATOR_PROVIDER_URL`
- `BLOCKED_ON_PROVIDER_HTTPS`
- `tunnel_rehearsal_not_run`
- `full_discovery_report_missing`
- `release_promotion_report_missing`
- `public_launch_approval_missing`

## Safety State

- No public exposure was enabled.
- No tunnel or reverse proxy was started.
- No DNS, firewall, or router setting was changed.
- Workbench exposure remains disabled.
- Public mutation remains disabled.
- Downloads/uploads remain disabled.
- Live metadata remains disabled.
- No launch approval was created.
- `.aide/queue/` was not mutated.

## Non-Claims

- AIDE was not run for this operator-input audit.
- Full unittest discovery was not run and is not claimed.
- This is not launch approval, release promotion, or public exposure evidence.
