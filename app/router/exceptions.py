"""Typed exceptions for the intent router."""


class RouterError(Exception):
    """Base class for router errors."""


class RouterValidationError(RouterError):
    """Input validation failed before routing."""
