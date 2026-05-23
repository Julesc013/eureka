"""Domain exceptions for local SearchNeed records."""


class SearchNeedError(Exception):
    """Base SearchNeed runtime error."""


class SearchNeedValidationError(SearchNeedError):
    """Raised when a SearchNeed payload violates local policy."""


class SearchNeedNotFoundError(SearchNeedError):
    """Raised when a SearchNeed does not exist in the local store."""


class SearchNeedTransitionError(SearchNeedError):
    """Raised when a SearchNeed transition is not allowed."""


class SearchNeedClosedError(SearchNeedError):
    """Raised when a closed SearchNeed store is used."""


class SearchNeedIntegrityError(SearchNeedError):
    """Raised when SearchNeed store integrity fails."""
