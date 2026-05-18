#!/usr/bin/env python3
"""Diagnose Python TLS trust without disabling certificate verification."""

from __future__ import annotations

import argparse
import json
import os
import platform
import socket
import ssl
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


DEFAULT_HOST = "archive.org"
CERT_ENV_VARS = ("SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host to test with a verified TLS handshake.")
    parser.add_argument("--task-id", default="IA-02-TLS-TRUST-CONTINUE", help="Task identifier to record.")
    parser.add_argument(
        "--redact-local-paths",
        action="store_true",
        help="Redact local filesystem paths from the emitted diagnostic.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--output", help="Optional JSON output path.")
    args = parser.parse_args(argv)

    result = diagnose_python_tls_trust(args.host, task_id=args.task_id, redact_local_paths=args.redact_local_paths)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("Python TLS trust diagnosis", file=stdout)
        print(f"host: {result['host']}", file=stdout)
        print(f"tls_handshake_status: {result['tls_handshake_status']}", file=stdout)
        print(f"failure_type: {result['failure_type']}", file=stdout)
    return 0


def diagnose_python_tls_trust(
    host: str = DEFAULT_HOST,
    port: int = 443,
    timeout: float = 10.0,
    *,
    task_id: str = "IA-02-TLS-TRUST-CONTINUE",
    redact_local_paths: bool = False,
) -> dict[str, Any]:
    certifi_available, certifi_path = _certifi_info()
    context_info = _default_context_info()
    verify_paths = ssl.get_default_verify_paths()
    cert_env_vars = {name: os.environ.get(name, "") for name in CERT_ENV_VARS}
    can_resolve_host = False
    tls_status = "not_run"
    failure_type = ""
    failure_message_redacted = ""
    peer_subject = ""
    peer_issuer = ""
    try:
        socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        can_resolve_host = True
    except OSError as exc:
        failure_type = "dns_failed"
        failure_message_redacted = _redact_error(exc)

    if can_resolve_host:
        try:
            context = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=host) as tls_sock:
                    certificate = tls_sock.getpeercert() or {}
                    tls_status = "pass"
                    peer_subject = _name_tuple_to_text(certificate.get("subject", ()))
                    peer_issuer = _name_tuple_to_text(certificate.get("issuer", ()))
        except ssl.SSLCertVerificationError as exc:
            tls_status = "fail"
            failure_type = "ssl_certificate_verify_failed"
            failure_message_redacted = _redact_error(exc)
        except ssl.SSLError as exc:
            tls_status = "fail"
            failure_type = "ssl_error"
            failure_message_redacted = _redact_error(exc)
        except OSError as exc:
            tls_status = "fail"
            failure_type = "network_error"
            failure_message_redacted = _redact_error(exc)

    return {
        "schema_version": "python_tls_trust_diagnosis.v0",
        "task": task_id,
        "host": host,
        "port": port,
        "python_version": sys.version.replace("\n", " "),
        "executable": _redact_path(sys.executable) if redact_local_paths else sys.executable,
        "local_paths_redacted": bool(redact_local_paths),
        "platform": platform.platform(),
        "ssl_openssl_version": ssl.OPENSSL_VERSION,
        "ssl_default_verify_paths": _redact_path_mapping(_verify_paths_to_dict(verify_paths), redact_local_paths),
        "ssl_default_verify_path_exists": _verify_path_exists(verify_paths),
        "cert_file_env_vars": _redact_path_mapping(cert_env_vars, redact_local_paths),
        "certifi_available": certifi_available,
        "certifi_path": _redact_path(certifi_path) if redact_local_paths and certifi_path else certifi_path,
        "can_create_default_context": bool(context_info["can_create_default_context"]),
        "default_context_verify_mode": context_info["verify_mode"],
        "default_context_check_hostname": context_info["check_hostname"],
        "can_resolve_host": can_resolve_host,
        "tls_handshake_status": tls_status,
        "failure_type": failure_type,
        "failure_message_redacted": failure_message_redacted,
        "peer_subject": peer_subject,
        "peer_issuer": peer_issuer,
        "verification_enabled": True,
        "insecure_context_used": False,
    }


def _certifi_info() -> tuple[bool, str]:
    try:
        import certifi  # type: ignore
    except Exception:
        return False, ""
    try:
        return True, str(certifi.where())
    except Exception:
        return True, ""


def _default_context_info() -> dict[str, Any]:
    try:
        context = ssl.create_default_context()
    except Exception:
        return {"can_create_default_context": False, "verify_mode": "", "check_hostname": False}
    return {
        "can_create_default_context": True,
        "verify_mode": _verify_mode_name(context.verify_mode),
        "check_hostname": bool(context.check_hostname),
    }


def _verify_paths_to_dict(paths: ssl.DefaultVerifyPaths) -> dict[str, str | None]:
    return {
        "cafile": paths.cafile,
        "capath": paths.capath,
        "openssl_cafile": paths.openssl_cafile,
        "openssl_cafile_env": paths.openssl_cafile_env,
        "openssl_capath": paths.openssl_capath,
        "openssl_capath_env": paths.openssl_capath_env,
    }


def _redact_path_mapping(values: Mapping[str, str | None], redact: bool) -> dict[str, str | None]:
    if not redact:
        return dict(values)
    return {key: _redact_path(value) if value else value for key, value in values.items()}


def _redact_path(value: str | None) -> str | None:
    if not value:
        return value
    text = str(value)
    if "\\" in text or "/" in text or ":" in text:
        return "<redacted-local-path>"
    return text


def _verify_path_exists(paths: ssl.DefaultVerifyPaths) -> dict[str, bool]:
    return {
        "cafile": bool(paths.cafile and Path(paths.cafile).exists()),
        "capath": bool(paths.capath and Path(paths.capath).exists()),
        "openssl_cafile": bool(paths.openssl_cafile and Path(paths.openssl_cafile).exists()),
        "openssl_capath": bool(paths.openssl_capath and Path(paths.openssl_capath).exists()),
    }


def _verify_mode_name(mode: ssl.VerifyMode) -> str:
    if mode == ssl.CERT_REQUIRED:
        return "CERT_REQUIRED"
    if mode == ssl.CERT_OPTIONAL:
        return "CERT_OPTIONAL"
    if mode == ssl.CERT_NONE:
        return "CERT_NONE"
    return str(mode)


def _name_tuple_to_text(value: object) -> str:
    if not isinstance(value, tuple):
        return ""
    parts: list[str] = []
    for item in value:
        if isinstance(item, tuple):
            for pair in item:
                if isinstance(pair, tuple) and len(pair) == 2:
                    parts.append(f"{pair[0]}={pair[1]}")
    return "; ".join(parts)


def _redact_error(exc: BaseException) -> str:
    text = str(exc)
    lowered = text.lower()
    if "self-signed" in lowered:
        return "self_signed_certificate_in_chain"
    if "certificate_verify_failed" in lowered or "certificate verify failed" in lowered:
        return "certificate_verify_failed"
    if "timed out" in lowered or "timeout" in lowered:
        return "timeout"
    if "getaddrinfo failed" in lowered:
        return "dns_resolution_failed"
    return exc.__class__.__name__


if __name__ == "__main__":
    raise SystemExit(main())
