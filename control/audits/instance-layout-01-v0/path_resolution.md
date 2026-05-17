# Path Resolution

Shared path helpers live in `runtime/local_appliance/paths.py`.

The resolver exposes:

- `resolve_repo_root(start=None)`
- `resolve_workspace_root(repo_root)`
- `resolve_instances_root(workspace_root)`
- `resolve_default_instance_root(repo_root)`
- `resolve_legacy_sibling_instance_root(repo_root)`
- `resolve_instance_root(instance_arg=None, repo_root=None)`
- `validate_instance_root_not_inside_repo(instance_root, repo_root)`
- `describe_instance_layout(repo_root, instance_root)`

The default path from the repo root resolves to `../instances/default`.
Explicit `../eureka-instance` remains accepted as a legacy sibling path. A
repo-nested `./eureka-instance` path is rejected by the shared resolver.
