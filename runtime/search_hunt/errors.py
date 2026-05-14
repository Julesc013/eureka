"""Domain exceptions for local Search Hunt sessions."""


class SearchHuntError(Exception):
    """Base error for Search Hunt session runtime failures."""


class SearchHuntClosedError(SearchHuntError):
    """Raised when a closed Search Hunt store is used."""


class SearchHuntIntegrityError(SearchHuntError):
    """Raised when the Search Hunt store fails integrity checks."""


class SearchHuntNotFoundError(SearchHuntError):
    """Raised when a Search Hunt session cannot be found."""


class SearchHuntTransitionError(SearchHuntError):
    """Raised when a state transition is not allowed."""


class SearchHuntValidationError(SearchHuntError):
    """Raised when Search Hunt input or records are invalid."""
