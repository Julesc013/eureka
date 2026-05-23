# Local Instance Layout

Eureka separates source code from mutable local appliance state.

The preferred development workspace is:

```text
D:\Projects\Eureka\
  eureka\                 # repo_root: Git checkout, docs, tests, AIDE
  instances\              # instances_root: local runtime state, not a Git repo
    default\              # instance_root: normal local development instance
    smoke\                # disposable local smoke/test instance
    lan\                  # read-only LAN/manual proof instance
    syn\                  # synthetic/eval run instance
    f0\                   # extraction experiment instance
```

From the repo root, the normal local development instance is:

```powershell
$Workspace = "D:\Projects\Eureka"
$Instance = "$Workspace\instances\default"
```

or, when already inside `D:\Projects\Eureka\eureka`:

```powershell
$Instance = "..\instances\default"
```

## Terms

- `workspace_root`: the parent directory that contains the repo and local state roots.
- `repo_root`: the Git checkout, normally `workspace_root/eureka`.
- `instances_root`: the local instance collection, normally `workspace_root/instances`.
- `instance_root`: one explicit local appliance instance, such as `workspace_root/instances/default`.
- `config_root`: `instance_root/config`.
- `db_root`: `instance_root/db`.
- `logs_root`: `instance_root/logs`.
- `run_root`: `instance_root/run`.
- `tmp_root`: `instance_root/tmp`.
- `imports_root`: `instance_root/imports`.
- `exports_root`: `instance_root/exports`.

## Instance Contents

A populated instance root can contain mutable local runtime state:

```text
instances/default/
  config/
    instance.json
    migration_state.json
    operator.json
    store_manifest.json
  db/
    source_cache.sqlite
    evidence_ledger.sqlite
    review_queue.sqlite
    public_index.sqlite
    workunit_queue.sqlite
    search_hunt.sqlite
    search_need.sqlite
    agent_research.sqlite
    ai_escalation.sqlite
  exports/
  imports/
  logs/
  run/
  tmp/
```

The sibling `../eureka-instance` name is still reflected in older LOCAL-01/LOCAL-02 validation history and remains a valid explicit instance path. New long-lived developer state should prefer the sibling `../instances/default` shape so smoke, LAN, synthetic, and experiment runs can use separate instances without polluting the default state.

The current legacy sibling layout:

```text
D:\Projects\Eureka\eureka-instance
```

is allowed as an explicit `--instance` path but is not preferred.

## Manual Migration

Repository scripts do not move, delete, or copy operator instance state unless a
future operator command explicitly asks them to. To migrate manually:

```powershell
mkdir D:\Projects\Eureka\instances
move D:\Projects\Eureka\eureka-instance D:\Projects\Eureka\instances\default
python scripts/eureka_init_instance.py --instance D:\Projects\Eureka\instances\default --json
python scripts/eureka_validate_instance.py --instance D:\Projects\Eureka\instances\default --json
```

For a dry-run plan only:

```powershell
python scripts/eureka_migrate_instance_layout.py --from ..\eureka-instance --to ..\instances\default --dry-run --json
```

## Commands

Initialize and validate the default development instance:

```powershell
python scripts/eureka_init_instance.py --instance $Instance --json
python scripts/eureka_validate_instance.py --instance $Instance --json
python scripts/eureka_instance_status.py --instance $Instance --json
```

Set a local operator token only for the selected instance:

```powershell
$Token = "local-dev-token"
python scripts/eureka_set_operator_token.py --instance $Instance --token $Token --json
```

Run a local server against the selected instance:

```powershell
python scripts/eureka_local_server.py --instance $Instance --host 127.0.0.1 --port 8765 --operator-token $Token
```

Use a different explicit instance for throwaway or role-specific work:

```powershell
$Instance = "D:\Projects\Eureka\instances\smoke"
python scripts/eureka_init_instance.py --instance $Instance --json
python scripts/eureka_validate_instance.py --instance $Instance --json
```

## Boundaries

Local instances are not product truth and are not source code. They may contain config, SQLite stores, logs, run files, imports, exports, and temporary files. They must not be committed, and scripts should continue to require an explicit `--instance` path instead of guessing mutable state from the repo path.

The current runtime path resolver is `runtime/local/appliance/instance.py`. A future broader LOCAL task can add a workspace-level resolver if scripts need shared `workspace_root`, `repo_root`, `instances_root`, and named-instance discovery.

## Installed Layout Notes

Future installed layouts should use platform state locations rather than the
development workspace. On Windows that means installed code under Program Files
and shared machine state under ProgramData. Linux and macOS should likewise use
their normal config/state/cache/log directories. This development layout is a
repo-adjacent analogue, not an installed-app requirement.
