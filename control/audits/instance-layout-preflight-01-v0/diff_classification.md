# Diff Classification

All four dirty documentation files align with the intended sibling instance
layout.

| Path | Classification | Action |
| --- | --- | --- |
| `docs/operations/LOCAL_INSTANCE_BOOTSTRAP.md` | Replaces `./eureka-instance` examples with `$Instance = "..\\instances\\default"` and preserves `./eureka-instance` only as an older validation fixture. | `commit_preflight` |
| `docs/operations/LOCAL_INSTANCE_MIGRATION_POLICY.md` | Replaces migration commands with `..\\instances\\default` and recommends long-lived operator state outside the Git checkout. | `commit_preflight` |
| `docs/operations/INSTANCE_PATH_POLICY.md` | Adds explicit instance path policy, preferred role names, forbidden roots, and future resolver guidance. | `commit_preflight` |
| `docs/operations/LOCAL_INSTANCE_LAYOUT.md` | Adds the preferred workspace layout, terminology, instance contents, PowerShell examples, and boundaries. | `commit_preflight` |

No file incorrectly recommends a repo-nested instance as the default. No
operator review blocker was found.
