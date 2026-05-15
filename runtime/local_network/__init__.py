"""LAN safety helpers for the local appliance service."""

from .client_scope import ClientScope, classify_client_scope
from .errors import LocalNetworkError, LocalNetworkHostError, LocalNetworkPolicyError, LocalNetworkSafetyError
from .hosts import classify_client_host, is_lan_bind_host, is_loopback_host, validate_service_host
from .policy import is_mutation_allowed_for_scope, is_route_allowed_for_scope, load_lan_policy
from .safety import build_firewall_warning, build_lan_warning, validate_lan_mode_safe
from .validation import validate_bind_lan_flag_required, validate_lan_read_only_route, validate_no_lan_mutation

__all__ = [
    "ClientScope",
    "LocalNetworkError",
    "LocalNetworkHostError",
    "LocalNetworkPolicyError",
    "LocalNetworkSafetyError",
    "build_firewall_warning",
    "build_lan_warning",
    "classify_client_host",
    "classify_client_scope",
    "is_lan_bind_host",
    "is_loopback_host",
    "is_mutation_allowed_for_scope",
    "is_route_allowed_for_scope",
    "load_lan_policy",
    "validate_bind_lan_flag_required",
    "validate_lan_mode_safe",
    "validate_lan_read_only_route",
    "validate_no_lan_mutation",
    "validate_service_host",
]
