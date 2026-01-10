"""Domain-specific exceptions for CryptoStory."""


class DomainException(Exception):
    """Base exception for domain errors."""


class InvalidIntervalError(DomainException):
    """Raised when an unsupported interval is provided."""


class InvalidTimestampRangeError(DomainException):
    """Raised when a timestamp range is invalid."""


class DuplicateCandleError(DomainException):
    """Raised when a duplicate candle insert is detected."""


class CandleMismatchError(DomainException):
    """Raised when an existing candle has conflicting values."""


class SymbolNotFoundError(DomainException):
    """Raised when a symbol is not found in storage."""
