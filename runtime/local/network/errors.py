"""Domain errors for local network safety checks."""


class LocalNetworkError(Exception):
    """Base error for local network safety failures."""


class LocalNetworkHostError(LocalNetworkError):
    """Raised when a bind or client host is outside policy."""


class LocalNetworkPolicyError(LocalNetworkError):
    """Raised when a route is outside network policy."""


class LocalNetworkSafetyError(LocalNetworkError):
    """Raised when LAN mode is not safe to enable."""
