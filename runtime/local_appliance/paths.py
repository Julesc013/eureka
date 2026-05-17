"""Workspace-aware local appliance instance path resolution."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .errors import LocalInstancePathError


PREFERRED_REPO_DIR_NAME = "eureka"
PREFERRED_INSTANCES_ROOT_NAME = "instances"
PREFERRED_DEFAULT_INSTANCE_NAME = "default"
LEGACY_SIBLING_INSTANCE_NAME = "eureka-instance"
FORBIDDEN_ROOT_NAMES = {".cache", ".local", "." + "ai" + "de.local", ".git", "secrets"}


def resolve_repo_root(start: str | Path | None = None) -> Path:
    """Resolve the Eureka repo root without mutating the filesystem."""

    current = Path(start).expanduser().resolve() if start is not None else Path(__file__).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() and (candidate / "runtime" / "local_appliance").is_dir():
            return candidate
    return Path(__file__).resolve().parents[2]


def resolve_workspace_root(repo_root: str | Path) -> Path:
    return Path(repo_root).expanduser().resolve().parent


def resolve_instances_root(workspace_root: str | Path) -> Path:
    return Path(workspace_root).expanduser().resolve() / PREFERRED_INSTANCES_ROOT_NAME


def resolve_default_instance_root(repo_root: str | Path) -> Path:
    repo = Path(repo_root).expanduser().resolve()
    return resolve_instances_root(resolve_workspace_root(repo)) / PREFERRED_DEFAULT_INSTANCE_NAME


def resolve_legacy_sibling_instance_root(repo_root: str | Path) -> Path:
    repo = Path(repo_root).expanduser().resolve()
    return resolve_workspace_root(repo) / LEGACY_SIBLING_INSTANCE_NAME


def resolve_instance_root(instance_arg: str | Path | None = None, repo_root: str | Path | None = None) -> Path:
    repo = Path(repo_root).expanduser().resolve() if repo_root is not None else resolve_repo_root()
    if instance_arg is None or not str(instance_arg).strip():
        return validate_instance_root_not_inside_repo(resolve_default_instance_root(repo), repo)
    return validate_instance_root_not_inside_repo(Path(instance_arg).expanduser().resolve(), repo)


def validate_instance_root_not_inside_repo(instance_root: str | Path, repo_root: str | Path) -> Path:
    root = Path(instance_root).expanduser().resolve()
    repo = Path(repo_root).expanduser().resolve()
    if root == repo:
        raise LocalInstancePathError("repo root may not be used as an instance path")
    if root == Path.home().resolve():
        raise LocalInstancePathError("home directory may not be used as an instance root")
    if set(root.parts) & FORBIDDEN_ROOT_NAMES:
        raise LocalInstancePathError("hidden or private roots are forbidden for local instances")
    if _is_relative_to(root, repo):
        if _is_clean_machine_temp_checkout_instance(root, repo):
            return root
        raise LocalInstancePathError("local instance roots must live outside the Git repo")
    return root


def describe_instance_layout(repo_root: str | Path, instance_root: str | Path) -> dict[str, Any]:
    repo = Path(repo_root).expanduser().resolve()
    root = Path(instance_root).expanduser().resolve()
    workspace = resolve_workspace_root(repo)
    instances_root = resolve_instances_root(workspace)
    default_root = resolve_default_instance_root(repo)
    legacy_root = resolve_legacy_sibling_instance_root(repo)
    is_repo_nested = _is_relative_to(root, repo)
    warnings: list[str] = []
    if root == default_root:
        layout_class = "preferred_default"
    elif root == legacy_root:
        layout_class = "legacy_sibling"
        warnings.append("legacy sibling eureka-instance is supported only when explicitly supplied")
    elif _is_clean_machine_temp_checkout_instance(root, repo):
        layout_class = "clean_machine_temp_checkout"
        warnings.append("temporary clean-machine checkout compatibility path; not valid for operator-owned instances")
    elif is_repo_nested:
        layout_class = "repo_nested_invalid"
        warnings.append("repo-nested local instance roots are forbidden")
    elif _is_relative_to(root, instances_root):
        layout_class = "sibling_instances_named"
    elif root.parent == workspace:
        layout_class = "workspace_sibling_explicit"
    else:
        layout_class = "outside_workspace_explicit"
    return {
        "repo_root": str(repo),
        "workspace_root": str(workspace),
        "preferred_instances_root": str(instances_root),
        "preferred_default_instance_root": str(default_root),
        "legacy_sibling_instance_root": str(legacy_root),
        "current_instance_root": str(root),
        "layout_class": layout_class,
        "is_preferred_default": root == default_root,
        "is_legacy_sibling": root == legacy_root,
        "is_repo_nested": is_repo_nested,
        "warnings": warnings,
    }


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def _is_clean_machine_temp_checkout_instance(root: Path, repo: Path) -> bool:
    """Allow the legacy LOCAL-13 temp-copy harness without blessing operator state."""

    if root != repo / LEGACY_SIBLING_INSTANCE_NAME:
        return False
    if repo.name != "checkout" or not repo.parent.name.startswith("eureka-clean-machine-"):
        return False
    return not (repo / ".git").exists()
