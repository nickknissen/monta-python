"""Exceptions for the Monta API client."""


class MontaApiClientError(Exception):
    """Exception to indicate a general API error."""


class MontaApiClientCommunicationError(MontaApiClientError):
    """Exception to indicate a communication error."""


class MontaApiClientAuthenticationError(MontaApiClientError):
    """Exception to indicate an authentication error.

    Carries ``status``, the HTTP status the API answered with, so a refused
    token (401) can be told apart from a request the credentials are not
    allowed to make (403). Only the former is worth presenting another token
    for.
    """

    def __init__(self, message: str, status: int | None = None) -> None:
        """Initialize with the HTTP status the API answered with."""
        super().__init__(message)
        self.status = status


class MontaApiClientRateLimitError(MontaApiClientError):
    """Exception to indicate the API rate limit (HTTP 429) was hit.

    Carries ``retry_after`` (seconds) parsed from the ``Retry-After`` response
    header when present, so callers can decide their own backoff policy. The
    client itself does not retry or sleep -- that is left to the caller.
    """

    def __init__(self, message: str, retry_after: int | None = None) -> None:
        """Initialize with an optional retry-after hint in seconds."""
        super().__init__(message)
        self.retry_after = retry_after
