"""Domain errors for the local appliance runtime."""


class LocalApplianceError(Exception):
    """Base error for local appliance runtime failures."""


class LocalInstancePathError(LocalApplianceError, ValueError):
    """Raised when an explicit instance path is missing or unsafe."""


class LocalInstanceConfigError(LocalApplianceError, ValueError):
    """Raised when instance configuration is missing or invalid."""


class LocalUnsupportedInstanceVersionError(LocalInstanceConfigError):
    """Raised when an instance schema version is not supported."""


class LocalStoreManifestError(LocalApplianceError, ValueError):
    """Raised when the store manifest is missing or invalid."""


class LocalMigrationStateError(LocalApplianceError, ValueError):
    """Raised when migration state blocks runtime opening."""


class LocalRuntimeCompositionError(LocalApplianceError, RuntimeError):
    """Raised when the runtime cannot compose all local stores."""


class LocalRuntimeClosedError(LocalRuntimeCompositionError):
    """Raised when a closed runtime is used."""


class LocalRuntimeIntegrityError(LocalRuntimeCompositionError):
    """Raised when local store integrity checks fail."""


class LocalReadOnlyStoreMutationError(LocalRuntimeCompositionError):
    """Raised when read-only composition receives a mutation call."""
