# Local Machine Public Tunnel Plan State

Task: `LOCAL-MACHINE-PUBLIC-TUNNEL-PLAN-00`

## Repo State

- Branch: `dev`
- HEAD: `484a1001fbb7b6ea4293c1787a71bffdb97c9de6`
- Worktree: dirty during this task; start guard reported clean before edits
- `HEAD...origin/dev`: ahead 0, behind 0
- Local branch ahead of `origin/dev`: no
- Post-commit note: after this task is committed, local `dev` is expected to be
  ahead of `origin/dev` until pushed.
- Current queue recommendation: `IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00`
- Selected launch-track task: `LOCAL-MACHINE-PUBLIC-TUNNEL-PLAN-00`

## Exposure State

- Ops posture artifact: `.eureka/ops/public-alpha/latest/ops_posture.json`
- Ops posture status: `READY_FOR_EXPOSURE_PLAN`
- Selected exposure mode: `reverse_tunnel`
- Public URL: missing
- TLS/provider HTTPS: missing
- Auth/no-auth posture: `public_no_auth`
- Public Workbench exposure: false
- Public mutation: false
- Live metadata: false
- Downloads/uploads: false / false
- Public network exposure: false

## Command Candidates

Local server candidate:

```powershell
python scripts/run_eureka_local.py --host 127.0.0.1 --port 8765 --public-alpha --staging-bundle .eureka/staging/public-alpha
```

Future tunnel placeholder:

```powershell
<selected-tunnel-provider> tunnel --url http://127.0.0.1:8765
```

No command in this task starts the server, starts a tunnel, starts a proxy,
modifies DNS, or changes firewall/router state.

## Route Smokes

- `/`
- `/health`
- `/status`
- `/api/status`
- `/about`
- `/method`
- `/search?q=old%20blue%20FTP%20client%20for%20XP`
- `/api/search?q=manual%20for%20Sound%20Blaster%20CT1740`
- `/record/{known-id-or-fixture-id}`

## Remaining Blockers

- Operator public URL/provider choice is missing.
- Provider HTTPS/TLS posture is missing.
- Known staged record ID is needed for future `/record` smoke.
- Tunnel/proxy rehearsal has not run.
- Full discovery launch report is missing.
- Release promotion report is missing.
- Manual public launch approval is missing.

Next recommended task: `LOCAL-MACHINE-PUBLIC-TUNNEL-OPERATOR-CHOICE-00`.
