#!/usr/bin/env python3
"""Check public alpha config manifest safe defaults."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_public_alpha_deployment_plan import RISKY_DISABLED_KEYS, REQUIRED_CONFIG_KEYS, detect_forbidden_deployment_claims


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="examples/hosting/deployment/public_alpha_config_manifest_v0.json")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = _load(args.input)
    errors = check_config_manifest(payload)
    result = {"schema_version": "public_alpha_config_manifest_check.v0", "status": "fail" if errors else "pass", "errors": errors}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.check:
        print(f"Public alpha config manifest check status: {result['status']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


def check_config_manifest(payload: dict) -> list[str]:
    errors = detect_forbidden_deployment_claims(payload, "config")
    variables = {item.get("config_key"): item for item in payload.get("config_variables", [])}
    missing = sorted(REQUIRED_CONFIG_KEYS - set(variables))
    if missing:
        errors.append(f"missing config keys: {missing}")
    for key in RISKY_DISABLED_KEYS:
        if variables.get(key, {}).get("safe_default") is not False:
            errors.append(f"{key}: risky default must be false.")
    for key in ("RATE_LIMIT_ENABLED", "KILL_SWITCH_GLOBAL", "KILL_SWITCH_CONNECTORS", "KILL_SWITCH_DOWNLOADS"):
        if variables.get(key, {}).get("safe_default") is not True:
            errors.append(f"{key}: protective default must be true.")
    return errors


def _load(value: str) -> dict:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
