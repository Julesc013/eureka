import json
import ssl
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.diagnose_python_tls_trust import diagnose_python_tls_trust


ROOT = Path(__file__).resolve().parents[2]


class FakeSocket:
    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False


class FakeTlsSocket:
    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False

    def getpeercert(self):
        return {
            "subject": ((("commonName", "archive.org"),),),
            "issuer": ((("organizationName", "Example CA"),),),
        }


class FakeContext:
    verify_mode = ssl.CERT_REQUIRED
    check_hostname = True

    def wrap_socket(self, sock, server_hostname=None):
        self.server_hostname = server_hostname
        return FakeTlsSocket()


class FailingContext(FakeContext):
    def wrap_socket(self, sock, server_hostname=None):
        raise ssl.SSLCertVerificationError("self-signed certificate in certificate chain")


class IATlsTrustDiagnosticTests(unittest.TestCase):
    def test_diagnostic_reports_successful_verified_handshake(self):
        with patch("socket.getaddrinfo", return_value=[object()]), patch(
            "socket.create_connection", return_value=FakeSocket()
        ), patch("ssl.create_default_context", return_value=FakeContext()):
            result = diagnose_python_tls_trust("archive.org")
        self.assertEqual("pass", result["tls_handshake_status"])
        self.assertTrue(result["verification_enabled"])
        self.assertFalse(result["insecure_context_used"])
        self.assertEqual("CERT_REQUIRED", result["default_context_verify_mode"])
        self.assertTrue(result["default_context_check_hostname"])

    def test_diagnostic_redacts_certificate_failures(self):
        with patch("socket.getaddrinfo", return_value=[object()]), patch(
            "socket.create_connection", return_value=FakeSocket()
        ), patch("ssl.create_default_context", return_value=FailingContext()):
            result = diagnose_python_tls_trust("archive.org")
        self.assertEqual("fail", result["tls_handshake_status"])
        self.assertEqual("ssl_certificate_verify_failed", result["failure_type"])
        self.assertEqual("self_signed_certificate_in_chain", result["failure_message_redacted"])
        self.assertTrue(result["verification_enabled"])
        self.assertFalse(result["insecure_context_used"])

    def test_diagnostic_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "scripts/diagnose_python_tls_trust.py", "--host", "archive.org", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["verification_enabled"])
        self.assertFalse(payload["insecure_context_used"])

    def test_tls_validator_passes_without_insecure_bypass(self):
        completed = subprocess.run(
            [sys.executable, "scripts/validate_ia_tls_trust.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"], payload)
        self.assertTrue(payload["verification_enabled"])
        self.assertFalse(payload["insecure_context_used"])


if __name__ == "__main__":
    unittest.main()
