"""Exceptions for the Monta API client."""


class MontaApiClientError(Exception):
    """Exception to indicate a general API error."""


class MontaApiClientCommunicationError(MontaApiClientError):
    """Exception to indicate a communication error."""


class MontaApiClientAuthenticationError(MontaApiClientError):
    """Exception to indicate an authentication error."""


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
