# Instance Path Policy

Eureka local appliance commands must keep source, mutable runtime state, user data, logs, and temporary files separate.

## Required Convention

Use explicit instance paths:

```powershell
cd D:\Projects\Eureka\eureka
$Instance = "..\instances\default"
python scripts/eureka_init_instance.py --instance $Instance --json
```

Commands should not infer an instance from the current working directory, the Git repo root, the user home directory, or a hidden cache directory. The repo root is source and governance material only.

## Preferred Names

- `instances/default`: normal local development.
- `instances/smoke`: disposable smoke and validation runs.
- `instances/lan`: LAN/manual proof runs.
- `instances/syn`: synthetic or eval runs.
- `instances/f0`: extraction experiments.
- `instances/dirty`: destructive/manual experiments.

Use role names instead of numbered or vague names.

## Forbidden Roots

An instance root must not be:

- the repo root;
- the user home directory as an implicit instance;
- a hidden/private local root such as `.cache`, `.local`, or `.aide.local`;
- generated site output such as `site/dist`;
- product source areas such as `runtime`, `contracts`, `surfaces`, `native`, `crates`, `examples`, or `control/prototypes`;
- any tracked Git path containing local database, log, run, tmp, import, or export state.

The current validators also reject committed local instance state and fail closed on unsupported instance schema versions.

## Repo Guard

The repo already ignores the historical repo-local instance fixtures:

```gitignore
eureka-instance/
eureka-instance-*/
```

The preferred sibling `D:\Projects\Eureka\instances\...` directory is outside the Git checkout. If a future task deliberately supports repo-local `instances/` for fixtures, it should add an explicit ignore rule and validator coverage in the same change.

## Resolver Rule

Local appliance scripts should continue to route concrete instance paths through the shared local appliance path validation layer. New scripts should reuse the existing resolver behavior instead of creating their own path rules.

A future runtime-local task may add a workspace-aware resolver for:

```text
workspace_root
repo_root
instances_root
instance_root
config_root
db_root
logs_root
run_root
tmp_root
imports_root
exports_root
```

That would be a runtime/script change and should be handled separately from documentation-only policy work.
