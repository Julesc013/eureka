"""Small stdlib helpers for hardening tests.

This module is intentionally not a test framework. It keeps repeated repo
inspection logic compact while leaving each hard guard explicit.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Iterator


REPO_ROOT = Path(__file__).resolve().parents[2]

TEXT_EXTENSIONS = {
    ".json",
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}

PRIVATE_PATH_PATTERNS = [
    re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/][^\s\"']+"),
    re.compile(r"/(?:tmp|var/folders|Users|home)/[^\s\"']+"),
    re.compile(r"AppData[\\/][^\s\"']+", re.IGNORECASE),
]


def repo_path(relative_path: str | Path) -> Path:
    return REPO_ROOT / relative_path


def read_text(relative_path: str | Path) -> str:
    return repo_path(relative_path).read_text(encoding="utf-8")


def load_json(relative_path: str | Path) -> Any:
    return json.loads(read_text(relative_path))


def iter_text_files(relative_roots: Iterable[str | Path]) -> Iterator[Path]:
    ignored_parts = {
        ".git",
        ".pytest_cache",
        "__pycache__",
        "target",
        ".mypy_cache",
    }
    for relative_root in relative_roots:
        root = repo_path(relative_root)
        if root.is_file():
            if root.suffix in TEXT_EXTENSIONS:
                yield root
            continue
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in TEXT_EXTENSIONS:
                continue
            if any(part in ignored_parts for part in path.parts):
                continue
            yield path


def iter_string_values(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from iter_string_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_string_values(item)


def find_private_path_leaks(value: Any) -> list[str]:
    leaks: list[str] = []
    for text in iter_string_values(value):
        for pattern in PRIVATE_PATH_PATTERNS:
            leaks.extend(match.group(0) for match in pattern.finditer(text))
    return sorted(set(leaks))


def run_python(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        str(REPO_ROOT)
        if not existing_pythonpath
        else str(REPO_ROOT) + os.pathsep + existing_pythonpath
    )
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def local_markdown_link_targets(relative_path: str | Path) -> list[tuple[int, str]]:
    path = repo_path(relative_path)
    targets: list[tuple[int, str]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for match in MARKDOWN_LINK_RE.finditer(line):
            target = match.group(1).strip()
            if " " in target and not target.startswith("<"):
                target = target.split(" ", 1)[0]
            target = target.strip("<>")
            if not target or target.startswith("#"):
                continue
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            targets.append((line_number, target))
    return targets


def unresolved_local_markdown_links(relative_path: str | Path) -> list[str]:
    path = repo_path(relative_path)
    base = path.parent
    broken: list[str] = []
    for line_number, target in local_markdown_link_targets(relative_path):
        file_part = target.split("#", 1)[0]
        if not file_part:
            continue
        candidate = (base / file_part).resolve()
        try:
            candidate.relative_to(REPO_ROOT.resolve())
        except ValueError:
            broken.append(f"{relative_path}:{line_number}: {target} escapes repo")
            continue
        if not candidate.exists():
            broken.append(f"{relative_path}:{line_number}: {target}")
    return broken


def fenced_command_blocks(relative_path: str | Path) -> list[str]:
    text = read_text(relative_path)
    blocks = re.findall(r"```(?:bash|sh|powershell|text)?\n(.*?)```", text, re.DOTALL)
    commands: list[str] = []
    for block in blocks:
        for raw_line in block.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            commands.append(line)
    return commands


def script_paths_from_commands(commands: Iterable[str]) -> list[str]:
    paths: list[str] = []
    for command in commands:
        for match in re.finditer(r"(?:python|python3|py)\s+([^\s]+\.py)", command):
            path = match.group(1).strip("'\"")
            if path.startswith("scripts/") or path.startswith("scripts\\"):
                paths.append(path.replace("\\", "/"))
    return sorted(set(paths))
