"""Safe validator adapters for P104 pack import dry-run."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys

from runtime.packs.policy import REPO_ROOT, ensure_approved_input_root, repo_relative


VALIDATOR_SCRIPTS = {
    "source_pack": REPO_ROOT / "scripts" / "validate_source_pack.py",
    "evidence_pack": REPO_ROOT / "scripts" / "validate_evidence_pack.py",
    "index_pack": REPO_ROOT / "scripts" / "validate_index_pack.py",
    "contribution_pack": REPO_ROOT / "scripts" / "validate_contribution_pack.py",
}


@dataclass(frozen=True)
class ValidatorResult:
    """Bounded validator result captured without import or mutation."""

    validation_status: str
    validator_command: str | None
    exit_code: int | None
    stdout_excerpt: str = ""
    stderr_excerpt: str = ""
    warning: str | None = None


def discover_validator_script(pack_kind: str) -> Path | None:
    script = VALIDATOR_SCRIPTS.get(pack_kind)
    return script if script and script.is_file() else None


def run_validator_for_pack(root: Path, pack_kind: str, *, timeout_seconds: int = 30) -> ValidatorResult:
    """Run a repo-local Python validator against one approved pack root."""

    script = discover_validator_script(pack_kind)
    if script is None:
        return ValidatorResult(
            validation_status="validator_missing" if pack_kind != "pack_set" else "validator_not_run",
            validator_command=None,
            exit_code=None,
            warning=f"no bounded repo validator configured for {pack_kind}",
        )
    checked_root = ensure_approved_input_root(root)
    command = [sys.executable, str(script), "--pack-root", repo_relative(checked_root), "--json"]
    try:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return ValidatorResult(
            validation_status="invalid",
            validator_command=_display_command(command),
            exit_code=None,
            warning="validator timed out",
        )
    status = "valid" if completed.returncode == 0 else "invalid"
    return ValidatorResult(
        validation_status=status,
        validator_command=_display_command(command),
        exit_code=completed.returncode,
        stdout_excerpt=_excerpt(completed.stdout),
        stderr_excerpt=_excerpt(completed.stderr),
    )


def _display_command(command: list[str]) -> str:
    display: list[str] = []
    for index, item in enumerate(command):
        if index == 0:
            display.append("python")
            continue
        path = Path(item)
        if path.is_absolute():
            display.append(repo_relative(path))
        else:
            display.append(item)
    return " ".join(display)


def _excerpt(text: str, *, limit: int = 500) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 3] + "..."
