from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ".aide/policies/commit-message-standard.yaml"
SUBJECT_RE = re.compile(r"^(?P<type>[a-z]+)\((?P<scope>[A-Za-z0-9_.-]+)\): (?P<summary>.+)$")
TRAILER_RE = re.compile(r"^(AIDE-[A-Za-z-]+):\s*(.+)$")


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preview grouped Eureka changelog entries from structured commits.")
    parser.add_argument("--message-file", action="append", default=[], help="Structured commit message file to parse.")
    parser.add_argument("--from", dest="from_rev", help="Start revision for git log range.")
    parser.add_argument("--to", dest="to_rev", default="HEAD", help="End revision for git log range.")
    parser.add_argument("--output", help="Explicit path to write the preview.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    messages: list[str] = []
    for path in args.message_file:
        messages.append(Path(path).read_text(encoding="utf-8"))
    if args.from_rev:
        messages.extend(read_git_messages(args.from_rev, args.to_rev))
    if not messages:
        parser.error("provide --message-file or --from")

    commits = [parse_commit_message(message) for message in messages]
    preview = render_changelog_preview(commits)
    if args.output:
        Path(args.output).write_text(preview, encoding="utf-8")
    (stdout or sys.stdout).write(preview)
    return 0


def read_git_messages(from_rev: str, to_rev: str = "HEAD") -> list[str]:
    """Read local git commit bodies without network calls or repository mutation."""

    rev_range = f"{from_rev}..{to_rev}"
    completed = subprocess.run(
        ["git", "log", "--format=%B%x1e", rev_range],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return [part.strip() for part in completed.stdout.split("\x1e") if part.strip()]


def parse_commit_message(message: str) -> dict[str, Any]:
    lines = message.replace("\r\n", "\n").strip().split("\n")
    subject = lines[0].strip() if lines else ""
    match = SUBJECT_RE.match(subject)
    subject_info = match.groupdict() if match else {"type": "", "scope": "", "summary": subject}
    return {
        "subject": subject,
        "type": subject_info["type"],
        "scope": subject_info["scope"],
        "summary": subject_info["summary"],
        "changelog": parse_changelog_groups(lines),
        "trailers": parse_trailers(lines),
    }


def parse_changelog_groups(lines: Sequence[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    in_changelog = False
    current_group: str | None = None
    for line in lines:
        stripped = line.strip()
        if stripped == "## Changelog":
            in_changelog = True
            current_group = None
            continue
        if in_changelog and stripped.startswith("## "):
            break
        if not in_changelog or not stripped:
            continue
        group_match = re.match(r"^-\s*([A-Za-z][A-Za-z -]*):\s*(.*)$", stripped)
        if group_match:
            current_group = group_match.group(1).strip()
            inline = group_match.group(2).strip()
            if inline:
                groups[current_group].append(inline)
            continue
        item_match = re.match(r"^-\s+(.+)$", stripped)
        if current_group and item_match:
            groups[current_group].append(item_match.group(1).strip())
    return {group: items for group, items in sorted(groups.items())}


def parse_trailers(lines: Sequence[str]) -> dict[str, str]:
    trailers: dict[str, str] = {}
    for line in lines:
        match = TRAILER_RE.match(line.strip())
        if match:
            trailers[match.group(1)] = match.group(2).strip()
    return dict(sorted(trailers.items()))


def render_changelog_preview(commits: Sequence[Mapping[str, Any]]) -> str:
    policy = load_policy()
    group_order = list(policy["changelog"]["groups"])
    grouped: dict[str, list[str]] = {group: [] for group in group_order}
    trailer_lines: list[str] = []

    for commit in commits:
        scope = commit.get("scope") or "unknown"
        summary = commit.get("summary") or commit.get("subject", "")
        changelog = commit.get("changelog", {})
        if isinstance(changelog, Mapping) and changelog:
            for group, items in changelog.items():
                if group not in grouped:
                    grouped[group] = []
                for item in items:
                    grouped[group].append(f"{item} ({scope})")
        else:
            fallback_group = conventional_type_to_group(str(commit.get("type", "")))
            grouped.setdefault(fallback_group, []).append(f"{summary} ({scope})")
        trailers = commit.get("trailers", {})
        if isinstance(trailers, Mapping):
            task = trailers.get("AIDE-Task")
            result = trailers.get("AIDE-Result")
            if task or result:
                trailer_lines.append(f"- {commit.get('subject')}: {task or 'no-task'} / {result or 'no-result'}")

    lines = ["# Eureka Changelog Preview", ""]
    for group in group_order:
        items = grouped.get(group, [])
        if not items:
            continue
        lines.append(f"## {group}")
        lines.extend(f"- {item}" for item in items)
        lines.append("")
    if trailer_lines:
        lines.append("## AIDE Trailers")
        lines.extend(trailer_lines)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def conventional_type_to_group(commit_type: str) -> str:
    mapping = {
        "feat": "Added",
        "fix": "Fixed",
        "docs": "Docs",
        "test": "Tests",
        "security": "Security",
        "refactor": "Changed",
        "contracts": "Changed",
        "audit": "Internal",
        "aide": "Internal",
        "ops": "Internal",
    }
    return mapping.get(commit_type, "Changed")


def load_policy() -> Mapping[str, Any]:
    return json.loads((REPO_ROOT / POLICY_PATH).read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
