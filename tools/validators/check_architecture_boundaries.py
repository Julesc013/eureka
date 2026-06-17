from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys
from typing import Iterable, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKED_TOP_LEVEL_PATHS = ("runtime", "surfaces")
GATEWAY_PUBLIC_API_PREFIX = "runtime.gateway.public_api"
CONNECTORS_PREFIX = "runtime.connectors"
ENGINE_PREFIX = "runtime.engine"
SURFACES_PREFIX = "surfaces"
ALLOWED_ACTIVE_TOP_LEVEL_ROOTS = (
    ".aide",
    ".github",
    "archive",
    "contracts",
    "control",
    "crates",
    "docs",
    "evals",
    "examples",
    "external",
    "native",
    "release",
    "runtime",
    "scripts",
    "site",
    "snapshots",
    "surfaces",
    "tests",
    "tools",
)
CLASSIFIED_TOP_LEVEL_EXCEPTIONS = {
    ".aide.local.example": "control_plane_local_state_template",
}
CONVENTIONAL_ROOT_FILES = (
    ".dockerignore",
    ".gitignore",
    "AGENTS.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "Dockerfile",
    "LICENSE-SUMMARY.md",
    "LICENSE.md",
    "NOTICE.md",
    "README.md",
    "SECURITY.md",
)
FORBIDDEN_ACTIVE_TOP_LEVEL_ROOTS = (
    "apps",
    "common",
    "data",
    "engine",
    "experimental",
    "helpers",
    "infra",
    "misc",
    "modules",
    "plugins",
    "renderers",
    "services",
    "skins",
    "temp",
    "tmp",
    "utils",
)


@dataclass(frozen=True)
class ModuleLocation:
    path: Path
    source_file: str
    module_name: str
    package_name: str


@dataclass(frozen=True)
class BoundaryViolation:
    rule_id: str
    source_file: str
    source_module: str
    imported_module: str
    line: int
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "rule_id": self.rule_id,
            "source_file": self.source_file,
            "source_module": self.source_module,
            "imported_module": self.imported_module,
            "line": self.line,
            "message": self.message,
        }


@dataclass(frozen=True)
class RootModelCheck:
    source: str
    active_roots: tuple[str, ...]
    allowed_roots: tuple[str, ...]
    classified_exceptions: Mapping[str, str]
    conventional_root_files: tuple[str, ...]
    unexpected_top_level_entries: tuple[str, ...]
    forbidden_active_roots: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "active_roots": list(self.active_roots),
            "allowed_roots": list(self.allowed_roots),
            "classified_exceptions": dict(self.classified_exceptions),
            "conventional_root_files": list(self.conventional_root_files),
            "unexpected_top_level_entries": list(self.unexpected_top_level_entries),
            "forbidden_active_roots": list(self.forbidden_active_roots),
            "status": "pass" if not self.unexpected_top_level_entries else "fail",
        }


@dataclass(frozen=True)
class BoundaryCheckResult:
    root: str
    checked_files: int
    root_model: RootModelCheck
    violations: tuple[BoundaryViolation, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "root": self.root,
            "checked_files": self.checked_files,
            "root_model": self.root_model.to_dict(),
            "violation_count": len(self.violations),
            "violations": [violation.to_dict() for violation in self.violations],
        }


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check Eureka's bootstrap Python import boundaries.",
    )
    parser.add_argument(
        "--root",
        default=str(REPO_ROOT),
        help="Repo root to scan. Defaults to this checkout.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    output = stdout or sys.stdout
    result = run_boundary_check(Path(args.root))
    if args.json:
        output.write(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        output.write("\n")
    else:
        output.write(render_text_report(result))
    return 1 if result.violations else 0


def run_boundary_check(root: Path) -> BoundaryCheckResult:
    normalized_root = root.resolve()
    root_model, root_violations = check_root_model(normalized_root)
    violations: list[BoundaryViolation] = list(root_violations)
    checked_files = 0

    for file_path in iter_python_files(normalized_root):
        checked_files += 1
        location = module_location_for_file(normalized_root, file_path)
        try:
            module = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        except SyntaxError as error:
            violations.append(
                BoundaryViolation(
                    rule_id="python_syntax_error",
                    source_file=location.source_file,
                    source_module=location.module_name,
                    imported_module="(parse failed)",
                    line=error.lineno or 1,
                    message=f"Could not parse Python file: {error.msg}.",
                )
            )
            continue

        for imported_module, line in iter_imported_modules(location, module):
            violation = classify_violation(location, imported_module, line)
            if violation is not None:
                violations.append(violation)

    violations.sort(
        key=lambda item: (
            item.source_file,
            item.line,
            item.rule_id,
            item.imported_module,
        )
    )
    return BoundaryCheckResult(
        root=str(normalized_root),
        checked_files=checked_files,
        root_model=root_model,
        violations=tuple(violations),
    )


def render_text_report(result: BoundaryCheckResult) -> str:
    lines = [
        f"Checked {result.checked_files} Python files under {result.root}",
        (
            "Root model: "
            f"{result.root_model.to_dict()['status']} "
            f"({len(result.root_model.active_roots)} active/classified top-level dirs; "
            f"{len(result.root_model.unexpected_top_level_entries)} unexpected)"
        ),
    ]
    if not result.violations:
        lines.append("No architecture-boundary violations found.")
        return "\n".join(lines) + "\n"

    lines.append(f"Found {len(result.violations)} architecture-boundary violation(s):")
    for violation in result.violations:
        lines.append(
            f"- {violation.source_file}:{violation.line} [{violation.rule_id}] "
            f"{violation.imported_module}"
        )
        lines.append(f"  {violation.message}")
    return "\n".join(lines) + "\n"


def check_root_model(root: Path) -> tuple[RootModelCheck, tuple[BoundaryViolation, ...]]:
    top_level, source = top_level_entries(root)
    allowed = set(ALLOWED_ACTIVE_TOP_LEVEL_ROOTS)
    exceptions = set(CLASSIFIED_TOP_LEVEL_EXCEPTIONS)
    conventional_files = set(CONVENTIONAL_ROOT_FILES)
    forbidden = set(FORBIDDEN_ACTIVE_TOP_LEVEL_ROOTS)
    unexpected: list[str] = []
    forbidden_present: list[str] = []
    violations: list[BoundaryViolation] = []

    for name, kind in sorted(top_level.items()):
        if kind == "file":
            if name in conventional_files:
                continue
            unexpected.append(name)
            violations.append(
                BoundaryViolation(
                    rule_id="unexpected_top_level_file",
                    source_file=name,
                    source_module="(repo_root)",
                    imported_module=name,
                    line=1,
                    message="Top-level files must be conventional root files or moved under an accepted root.",
                )
            )
            continue

        if name in allowed or name in exceptions:
            continue

        unexpected.append(name)
        if name in forbidden:
            forbidden_present.append(name)
            rule_id = "forbidden_top_level_root"
            message = (
                "This active top-level root is forbidden by the frozen Eureka root model; "
                "place the concept under an existing canonical root instead."
            )
        else:
            rule_id = "unexpected_top_level_root"
            message = "Top-level roots must be accepted by the Eureka root model or explicitly classified."
        violations.append(
            BoundaryViolation(
                rule_id=rule_id,
                source_file=name,
                source_module="(repo_root)",
                imported_module=name,
                line=1,
                message=message,
            )
        )

    root_model = RootModelCheck(
        source=source,
        active_roots=tuple(sorted(name for name, kind in top_level.items() if kind == "dir")),
        allowed_roots=tuple(sorted(ALLOWED_ACTIVE_TOP_LEVEL_ROOTS)),
        classified_exceptions=dict(CLASSIFIED_TOP_LEVEL_EXCEPTIONS),
        conventional_root_files=tuple(sorted(name for name, kind in top_level.items() if kind == "file")),
        unexpected_top_level_entries=tuple(sorted(unexpected)),
        forbidden_active_roots=tuple(sorted(forbidden_present)),
    )
    return root_model, tuple(violations)


def top_level_entries(root: Path) -> tuple[dict[str, str], str]:
    tracked_files = git_ls_files(root)
    if tracked_files is not None:
        return top_level_entries_from_paths(tracked_files), "git_ls_files"

    entries: dict[str, str] = {}
    try:
        children = sorted(root.iterdir(), key=lambda path: path.name)
    except OSError:
        return entries, "filesystem"
    for child in children:
        if child.name == ".git":
            continue
        entries[child.name] = "dir" if child.is_dir() else "file"
    return entries, "filesystem"


def git_ls_files(root: Path) -> list[str] | None:
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return [line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()]


def top_level_entries_from_paths(paths: Sequence[str]) -> dict[str, str]:
    entries: dict[str, str] = {}
    for path in paths:
        parts = path.split("/")
        name = parts[0]
        kind = "dir" if len(parts) > 1 else "file"
        entries[name] = "dir" if entries.get(name) == "dir" or kind == "dir" else kind
    return entries


def iter_python_files(root: Path) -> Iterable[Path]:
    for top_level in CHECKED_TOP_LEVEL_PATHS:
        search_root = root / top_level
        if not search_root.exists():
            continue
        for file_path in sorted(search_root.rglob("*.py")):
            if "__pycache__" in file_path.parts:
                continue
            yield file_path


def module_location_for_file(root: Path, file_path: Path) -> ModuleLocation:
    relative_path = file_path.relative_to(root)
    module_parts = list(relative_path.with_suffix("").parts)
    if module_parts[-1] == "__init__":
        module_parts = module_parts[:-1]
        module_name = ".".join(module_parts)
        package_name = module_name
    else:
        module_name = ".".join(module_parts)
        package_name = ".".join(module_parts[:-1])
    return ModuleLocation(
        path=file_path,
        source_file=relative_path.as_posix(),
        module_name=module_name,
        package_name=package_name,
    )


def iter_imported_modules(location: ModuleLocation, module: ast.AST) -> Iterable[tuple[str, int]]:
    for node in ast.walk(module):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, node.lineno
            continue

        if isinstance(node, ast.ImportFrom):
            resolved_base = resolve_from_import_base(location.package_name, node.level, node.module)
            if resolved_base is None:
                continue
            if len(node.names) == 1 and node.names[0].name == "*":
                yield resolved_base, node.lineno
                continue
            for alias in node.names:
                if alias.name == "*":
                    yield resolved_base, node.lineno
                    continue
                yield f"{resolved_base}.{alias.name}", node.lineno


def resolve_from_import_base(package_name: str, level: int, module_name: str | None) -> str | None:
    if level == 0:
        return module_name

    package_parts = [part for part in package_name.split(".") if part]
    levels_up = level - 1
    if levels_up > len(package_parts):
        return None
    if levels_up:
        package_parts = package_parts[: -levels_up]

    if module_name:
        package_parts.extend(part for part in module_name.split(".") if part)
    return ".".join(package_parts)


def classify_violation(
    location: ModuleLocation,
    imported_module: str,
    line: int,
) -> BoundaryViolation | None:
    source_module = location.module_name
    surface_prefix = surface_family_prefix(source_module)
    if surface_prefix is not None:
        return classify_surface_violation(
            location,
            imported_module,
            line,
            allowed_surface_prefix=surface_prefix,
        )

    if source_module.startswith(GATEWAY_PUBLIC_API_PREFIX) and imported_module.startswith(SURFACES_PREFIX):
        return BoundaryViolation(
            rule_id="gateway_public_api_surface_import",
            source_file=location.source_file,
            source_module=source_module,
            imported_module=imported_module,
            line=line,
            message="runtime/gateway/public_api modules must not import surfaces.",
        )

    if source_module.startswith(CONNECTORS_PREFIX) and imported_module.startswith(SURFACES_PREFIX):
        return BoundaryViolation(
            rule_id="connector_surface_import",
            source_file=location.source_file,
            source_module=source_module,
            imported_module=imported_module,
            line=line,
            message="runtime/connectors modules must not import surfaces.",
        )

    if source_module.startswith(ENGINE_PREFIX) and imported_module.startswith(SURFACES_PREFIX):
        return BoundaryViolation(
            rule_id="engine_surface_import",
            source_file=location.source_file,
            source_module=source_module,
            imported_module=imported_module,
            line=line,
            message="runtime/engine modules must not import surfaces.",
        )

    return None


def surface_family_prefix(module_name: str) -> str | None:
    if not module_name.startswith(f"{SURFACES_PREFIX}."):
        return None
    parts = module_name.split(".")
    if len(parts) < 2:
        return None
    return ".".join(parts[:2])


def classify_surface_violation(
    location: ModuleLocation,
    imported_module: str,
    line: int,
    *,
    allowed_surface_prefix: str,
) -> BoundaryViolation | None:
    if imported_module.startswith(ENGINE_PREFIX):
        return BoundaryViolation(
            rule_id="surface_engine_import",
            source_file=location.source_file,
            source_module=location.module_name,
            imported_module=imported_module,
            line=line,
            message="Surface modules must not import runtime.engine internals directly.",
        )

    if imported_module.startswith(CONNECTORS_PREFIX):
        return BoundaryViolation(
            rule_id="surface_connector_import",
            source_file=location.source_file,
            source_module=location.module_name,
            imported_module=imported_module,
            line=line,
            message="Surface modules must not import runtime.connectors directly.",
        )

    if imported_module.startswith("runtime") and not imported_module.startswith(GATEWAY_PUBLIC_API_PREFIX):
        return BoundaryViolation(
            rule_id="surface_runtime_outside_public_api",
            source_file=location.source_file,
            source_module=location.module_name,
            imported_module=imported_module,
            line=line,
            message="Surface modules may import runtime only through runtime.gateway.public_api.",
        )

    if imported_module.startswith(SURFACES_PREFIX) and not imported_module.startswith(allowed_surface_prefix):
        return BoundaryViolation(
            rule_id="surface_cross_surface_import",
            source_file=location.source_file,
            source_module=location.module_name,
            imported_module=imported_module,
            line=line,
            message="Surface modules may import only same-surface helpers plus gateway public APIs and contracts.",
        )

    return None


if __name__ == "__main__":
    raise SystemExit(main())
