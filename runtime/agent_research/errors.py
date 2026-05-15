"""Errors for disabled agent research task records."""


class AgentResearchError(Exception):
    """Base error for agent research task contracts."""


class AgentResearchValidationError(AgentResearchError):
    """Raised when an agent research task or report contract is invalid."""


class AgentResearchNotFoundError(AgentResearchError):
    """Raised when an agent research task cannot be found."""


class AgentResearchClosedError(AgentResearchError):
    """Raised when a closed agent research store is used."""
