# Local Machine Public Tunnel Operator Choice State

Task: `LOCAL-MACHINE-PUBLIC-TUNNEL-OPERATOR-CHOICE-00`

## Repo State

- Branch: `dev`
- HEAD: `8ca08ffa5ce9f1ba7c811e81d2dd4a68c6456d5d`
- Worktree: dirty during implementation; start guard reported clean before edits
- `HEAD...origin/dev`: ahead 0, behind 0
- Remote sync required before exposure: no
- Post-commit note: after this task is committed, local `dev` is expected to be
  ahead of `origin/dev` by this commit until pushed.
- Current queue recommendation: `IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00`
- Selected launch-track task: `LOCAL-MACHINE-PUBLIC-TUNNEL-OPERATOR-CHOICE-00`

## Operator Choice

- Exposure mode: `reverse_tunnel`
- Provider class: `provider_managed_https_tunnel`
- Provider name: `OPERATOR_REQUIRED`
- Public URL: `OPERATOR_REQUIRED`
- TLS/provider HTTPS: `operator_required`
- Local bind: `127.0.0.1:8765`
- Ops posture: `READY_FOR_EXPOSURE_PLAN`
- Exposure plan: `READY_FOR_OPERATOR_URL`
- Status: `BLOCKED_ON_OPERATOR_PROVIDER_URL`

## Safety

- Public exposure enabled: false
- Tunnel/proxy started: false
- Public Workbench exposure: false
- Public mutation: false
- Live metadata: false
- Downloads/uploads: false / false
- Launch approval: false
- Production readiness claim: false

## Future Commands

Local server template:

```powershell
python scripts/run_eureka_local.py --host 127.0.0.1 --port 8765 --public-alpha --staging-bundle .eureka/staging/public-alpha
```

Future tunnel template:

```powershell
<selected-tunnel-provider> tunnel --url http://127.0.0.1:8765
```

## Remaining Blockers

- Operator provider name or public URL is required.
- Provider HTTPS/TLS posture is unresolved.
- Staged record ID is needed for future `/record` route smoke.
- Actual tunnel/proxy rehearsal has not run.
- Full discovery launch report is missing.
- Release promotion report is missing.
- Manual public launch approval is missing.

Next recommended task: `LOCAL-MACHINE-PUBLIC-TUNNEL-OPERATOR-INPUT-00`.
