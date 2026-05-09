import importlib
import unittest

from runtime.relay.profiles import load_relay_policy
from runtime.relay.security import build_policy_blocked_response, validate_bind_host


class RelaySecurityTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_relay_policy()

    def test_127_bind_allowed(self):
        self.assertEqual(validate_bind_host("127.0.0.1", self.policy), [])

    def test_localhost_bind_allowed(self):
        self.assertEqual(validate_bind_host("localhost", self.policy), [])

    def test_zero_bind_rejected(self):
        self.assertTrue(validate_bind_host("0.0.0.0", self.policy))

    def test_wildcard_public_bind_rejected(self):
        self.assertTrue(validate_bind_host("*", self.policy))
        self.assertTrue(validate_bind_host("::", self.policy))

    def test_server_module_import_does_not_start_server(self):
        module = importlib.import_module("runtime.relay.server")
        self.assertTrue(hasattr(module, "create_loopback_server"))

    def test_public_index_mutation_claim_rejected(self):
        response = build_policy_blocked_response("blocked", self.policy)
        response["truth_boundary"]["relay_mutates_public_index"] = True
        from runtime.relay.profiles import detect_relay_boundary_violations

        self.assertTrue(detect_relay_boundary_violations(response))

    def test_master_index_mutation_claim_rejected(self):
        response = build_policy_blocked_response("blocked", self.policy)
        response["truth_boundary"]["relay_mutates_master_index"] = True
        from runtime.relay.profiles import detect_relay_boundary_violations

        self.assertTrue(detect_relay_boundary_violations(response))

    def test_rights_malware_installability_claim_rejected(self):
        response = build_policy_blocked_response("blocked", self.policy)
        response["truth_boundary"]["rights_clearance_claimed"] = True
        response["truth_boundary"]["malware_safety_claimed"] = True
        response["truth_boundary"]["verified_installability_claimed"] = True
        from runtime.relay.profiles import detect_relay_boundary_violations

        self.assertGreaterEqual(len(detect_relay_boundary_violations(response)), 3)


if __name__ == "__main__":
    unittest.main()

