"""Domain errors for the local HTML workbench."""


class LocalWorkbenchError(Exception):
    """Base error for local workbench failures."""


class LocalWorkbenchValidationError(LocalWorkbenchError):
    """Raised when rendered workbench HTML violates the local boundary."""
