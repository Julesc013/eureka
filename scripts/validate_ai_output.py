from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.engine.ai.typed_output_validator import (  # noqa: E402
    load_json,
    validate_ai_output_bundle,
    validate_provider_manifest,
    validate_typed_ai_output_file,
)


DEFAULT_PROVIDER_ROOT = REPO_ROOT / "examples" / "ai_providers" / "disabled_stub_provider_v0"
DEFAULT_PROVIDER = DEFAULT_PROVIDER_ROOT / "AI_PROVIDER.json"
EXAMPLE_REGISTRY = REPO_ROOT / "control" / "inventory" / "ai_providers" / "typed_output_examples.json"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate typed AI output examples without model calls.")
    parser.add_argument("--output", help="Validate one typed AI output JSON file.")
    parser.add_argument("--provider", help="Provider manifest to validate against.")
    parser.add_argument("--bundle-root", help="Validate a provider bundle root containing AI_PROVIDER.json and examples/*.json.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all registered typed AI output examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Require registry-backed all-example validation.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_ai_outputs(
        output_path=Path(args.output) if args.output else None,
        provider_path=Path(args.provider) if args.provider else None,
        bundle_root=Path(args.bundle_root) if args.bundle_root else None,
        all_examples=args.all_examples or (not args.output and not args.bundle_root),
        strict=args.strict,
    )
    stream = stdout or sys.stdout
    if args.json:
        stream.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        stream.write(_format_plain(report))
    return 0 if report["ok"] else 1


def validate_ai_outputs(
    *,
    output_path: Path | None = None,
    provider_path: Path | None = None,
    bundle_root: Path | None = None,
    all_examples: bool = False,
    strict: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    checked_outputs: list[dict[str, Any]] = []
    checked_providers: list[dict[str, Any]] = []
    mode = "all_examples" if all_examples else "single"

    if bundle_root is not None:
        root = _resolve(bundle_root)
        bundle_report = validate_ai_output_bundle(root)
        checked_outputs.extend(_rel_output_results(bundle_report["checked_outputs"]))
        checked_providers.extend(_rel_provider_results(bundle_report["checked_providers"]))
        errors.extend(bundle_report["errors"])
        mode = "bundle"
    elif all_examples:
        examples = _load_example_registry(errors)
        if not examples and strict:
            errors.append(f"{_rel(EXAMPLE_REGISTRY)}: strict mode requires typed output example registry entries.")
        provider_manifest = _load_provider(provider_path or DEFAULT_PROVIDER, checked_providers, errors)
        for item in examples:
            path = _resolve(Path(str(item.get("path", ""))))
            result = validate_typed_ai_output_file(path, provider_manifest=provider_manifest)
            result["path"] = _rel(Path(result["path"]))
            result["expected_validation_status"] = item.get("expected_validation_status")
            checked_outputs.append(result)
            errors.extend(f"{result['path']}: {error}" for error in result["errors"])
    elif output_path is not None:
        provider_manifest = _load_provider(provider_path or DEFAULT_PROVIDER, checked_providers, errors)
        path = _resolve(output_path)
        result = validate_typed_ai_output_file(path, provider_manifest=provider_manifest)
        result["path"] = _rel(Path(result["path"]))
        checked_outputs.append(result)
        errors.extend(f"{result['path']}: {error}" for error in result["errors"])
    else:
        errors.append("no typed AI output validation target supplied.")

    passed = sum(1 for result in checked_outputs if result.get("ok"))
    failed = sum(1 for result in checked_outputs if not result.get("ok"))
    return {
        "schema_version": "typed_ai_output_validation.v0",
        "validator_id": "typed_ai_output_validator_v0",
        "ok": not errors,
        "mode": mode,
        "strict": strict,
        "checked_outputs": checked_outputs,
        "checked_providers": checked_providers,
        "passed": passed,
        "failed": failed,
        "unavailable": 0,
        "errors": errors,
        "model_calls_performed": False,
        "network_performed": False,
        "mutation_performed": False,
        "import_performed": False,
    }


def _load_example_registry(errors: list[str]) -> list[Mapping[str, Any]]:
    if not EXAMPLE_REGISTRY.exists():
        errors.append(f"{_rel(EXAMPLE_REGISTRY)}: typed output example registry is missing.")
        return []
    try:
        payload = load_json(EXAMPLE_REGISTRY)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{_rel(EXAMPLE_REGISTRY)}: could not parse typed output example registry: {exc}.")
        return []
    examples = payload.get("examples") if isinstance(payload, Mapping) else None
    if not isinstance(examples, list):
        errors.append(f"{_rel(EXAMPLE_REGISTRY)}: examples must be an array.")
        return []
    return [item for item in examples if isinstance(item, Mapping)]


def _load_provider(
    provider_path: Path,
    checked_providers: list[dict[str, Any]],
    errors: list[str],
) -> Mapping[str, Any] | None:
    path = _resolve(provider_path)
    if not path.exists():
        errors.append(f"{_rel(path)}: provider manifest is unavailable.")
        checked_providers.append({"path": _rel(path), "status": "unavailable", "ok": False, "errors": ["provider manifest is unavailable."]})
        return None
    try:
        payload = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{_rel(path)}: could not parse provider manifest: {exc}.")
        checked_providers.append({"path": _rel(path), "status": "failed", "ok": False, "errors": [str(exc)]})
        return None
    if not isinstance(payload, Mapping):
        errors.append(f"{_rel(path)}: provider manifest must be a JSON object.")
        checked_providers.append({"path": _rel(path), "status": "failed", "ok": False, "errors": ["provider manifest must be a JSON object."]})
        return None
    provider_errors = validate_provider_manifest(payload)
    checked_providers.append(
        {
            "path": _rel(path),
            "provider_id": payload.get("provider_id"),
            "provider_type": payload.get("provider_type"),
            "status": "passed" if not provider_errors else "failed",
            "ok": not provider_errors,
            "errors": provider_errors,
        }
    )
    errors.extend(f"{_rel(path)}: {error}" for error in provider_errors)
    return payload


def _rel_output_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rel_results: list[dict[str, Any]] = []
    for result in results:
        copy = dict(result)
        copy["path"] = _rel(Path(str(copy.get("path", ""))))
        rel_results.append(copy)
    return rel_results


def _rel_provider_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rel_results: list[dict[str, Any]] = []
    for result in results:
        copy = dict(result)
        copy["path"] = _rel(Path(str(copy.get("path", ""))))
        rel_results.append(copy)
    return rel_results


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except (OSError, ValueError):
        return str(path)


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Typed AI Output validation",
        f"status: {'valid' if report['ok'] else 'invalid'}",
        f"mode: {report['mode']}",
        f"checked_outputs: {len(report['checked_outputs'])}",
        f"passed: {report['passed']}",
        f"failed: {report['failed']}",
        f"model_calls_performed: {report['model_calls_performed']}",
        f"network_performed: {report['network_performed']}",
        f"mutation_performed: {report['mutation_performed']}",
        f"import_performed: {report['import_performed']}",
    ]
    if report["errors"]:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
