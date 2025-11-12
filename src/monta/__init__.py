"""Monta API Client for Python.

A Python client library for the Monta EV charging API.
"""

from .client import InMemoryTokenStorage, MontaApiClient, TokenStorage
from .const import ChargerStatus, WalletStatus
from .exceptions import (
    MontaApiClientAuthenticationError,
    MontaApiClientCommunicationError,
    MontaApiClientError,
)
from .models import (
    Address,
    Balance,
    Charge,
    ChargePoint,
    ChargeState,
    Connector,
    Coordinates,
    Currency,
    Location,
    SOC,
    SOCSource,
    TokenResponse,
    Wallet,
    WalletTransaction,
    WalletTransactionState,
)

__version__ = "0.1.0"

__all__ = [
    # Client
    "MontaApiClient",
    "TokenStorage",
    "InMemoryTokenStorage",
    # Exceptions
    "MontaApiClientError",
    "MontaApiClientCommunicationError",
    "MontaApiClientAuthenticationError",
    # Models
    "TokenResponse",
    "ChargePoint",
    "Charge",
    "Wallet",
    "Balance",
    "Currency",
    "WalletTransaction",
    "SOC",
    "Coordinates",
    "Address",
    "Location",
    "Connector",
    # Enums
    "ChargeState",
    "ChargerStatus",
    "WalletStatus",
    "WalletTransactionState",
    "SOCSource",
]
