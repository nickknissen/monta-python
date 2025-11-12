"""Data models for Monta API responses."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ChargeState(str, Enum):
    """Valid charge state values for filtering charges."""

    RESERVED = "reserved"
    STARTING = "starting"
    CHARGING = "charging"
    STOPPING = "stopping"
    PAUSED = "paused"
    SCHEDULED = "scheduled"
    STOPPED = "stopped"
    COMPLETED = "completed"


class WalletTransactionState(str, Enum):
    """Valid wallet transaction state values for filtering transactions."""

    COMPLETE = "complete"
    PENDING = "pending"
    FAILED = "failed"
    RESERVED = "reserved"


class SOCSource(str, Enum):
    """Source of state of charge value."""

    CHARGE_POINT = "charge-point"
    VEHICLE = "vehicle"


@dataclass
class SOC:
    """Represents state of charge information."""

    percentage: float
    source: str

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> SOC | None:
        """Create a SOC from a dictionary."""
        if not data:
            return None
        return cls(
            percentage=data.get("percentage", 0.0),
            source=data.get("source", ""),
        )


@dataclass
class Currency:
    """Represents currency information."""

    identifier: str
    name: str
    decimals: int = 2

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Currency | None:
        """Create a Currency from a dictionary."""
        if not data:
            return None
        return cls(
            identifier=data.get("identifier", ""),
            name=data.get("name", ""),
            decimals=data.get("decimals", 2),
        )


@dataclass
class Balance:
    """Represents wallet balance information."""

    amount: float
    credit: float

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Balance | None:
        """Create a Balance from a dictionary."""
        if not data:
            return None
        return cls(
            amount=data.get("amount", 0.0),
            credit=data.get("credit", 0.0),
        )


@dataclass
class Wallet:
    """Represents a personal wallet."""
    id: int
    owner_type: str
    balance: Balance | None
    currency: Currency | None
    status: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Wallet:
        """Create a Wallet from a dictionary."""
        return cls(
            id=data.get("id", 0),
            owner_type=data.get("ownerType", ""),
            balance=Balance.from_dict(data.get("balance")),
            currency=Currency.from_dict(data.get("currency")),
            status=data.get("status", ""),
        )


@dataclass
class Charge:
    """Represents a charging session."""

    id: int
    charge_point_id: int
    state: str
    human_readable_id: str
    consumed_kwh: float | None = None
    start_meter_kwh: float | None = None
    end_meter_kwh: float | None = None
    cost: float | None = None
    price: float | None = None
    average_price_per_kwh: float | None = None
    average_co2_per_kwh: float | None = None
    average_renewable_per_kwh: float | None = None
    kwh_limit: float | None = None
    price_limit: float | None = None
    soc: SOC | None = None
    soc_limit: float | None = None
    failure_reason: str | None = None
    stop_reason: str | None = None
    note: str | None = None
    currency: Currency | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    cable_plugged_in_at: datetime | None = None
    fully_charged_at: datetime | None = None
    failed_at: datetime | None = None
    timeout_at: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Charge:
        """Create a Charge from a dictionary."""
        return cls(
            id=data["id"],
            charge_point_id=data.get("chargePointId", 0),
            state=data.get("state", ""),
            human_readable_id=data.get("humanReadableId", ""),
            consumed_kwh=data.get("consumedKwh"),
            start_meter_kwh=data.get("startMeterKwh"),
            end_meter_kwh=data.get("endMeterKwh"),
            cost=data.get("cost"),
            price=data.get("price"),
            average_price_per_kwh=data.get("averagePricePerKwh"),
            average_co2_per_kwh=data.get("averageCo2PerKwh"),
            average_renewable_per_kwh=data.get("averageRenewablePerKwh"),
            kwh_limit=data.get("kwhLimit"),
            price_limit=data.get("priceLimit"),
            soc=SOC.from_dict(data.get("soc")),
            soc_limit=data.get("socLimit"),
            failure_reason=data.get("failureReason"),
            stop_reason=data.get("stopReason"),
            note=data.get("note"),
            currency=Currency.from_dict(data.get("currency")),
            created_at=_parse_datetime(data.get("createdAt")),
            updated_at=_parse_datetime(data.get("updatedAt")),
            started_at=_parse_datetime(data.get("startedAt")),
            stopped_at=_parse_datetime(data.get("stoppedAt")),
            cable_plugged_in_at=_parse_datetime(data.get("cablePluggedInAt")),
            fully_charged_at=_parse_datetime(data.get("fullyChargedAt")),
            failed_at=_parse_datetime(data.get("failedAt")),
            timeout_at=_parse_datetime(data.get("timeoutAt")),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert Charge to a dictionary for compatibility."""
        result = {
            "id": self.id,
            "chargePointId": self.charge_point_id,
            "state": self.state,
            "humanReadableId": self.human_readable_id,
            "consumedKwh": self.consumed_kwh,
            "startMeterKwh": self.start_meter_kwh,
            "endMeterKwh": self.end_meter_kwh,
            "cost": self.cost,
            "price": self.price,
            "averagePricePerKwh": self.average_price_per_kwh,
            "averageCo2PerKwh": self.average_co2_per_kwh,
            "averageRenewablePerKwh": self.average_renewable_per_kwh,
            "kwhLimit": self.kwh_limit,
            "priceLimit": self.price_limit,
            "socLimit": self.soc_limit,
            "failureReason": self.failure_reason,
            "stopReason": self.stop_reason,
            "note": self.note,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "stoppedAt": self.stopped_at.isoformat() if self.stopped_at else None,
            "cablePluggedInAt": self.cable_plugged_in_at.isoformat() if self.cable_plugged_in_at else None,
            "fullyChargedAt": self.fully_charged_at.isoformat() if self.fully_charged_at else None,
            "failedAt": self.failed_at.isoformat() if self.failed_at else None,
            "timeoutAt": self.timeout_at.isoformat() if self.timeout_at else None,
        }

        # Add SOC if present
        if self.soc:
            result["soc"] = {
                "percentage": self.soc.percentage,
                "source": self.soc.source,
            }

        # Add currency if present
        if self.currency:
            result["currency"] = {
                "identifier": self.currency.identifier,
                "name": self.currency.name,
                "decimals": self.currency.decimals,
            }

        return result


@dataclass
class Coordinates:
    """Represents GPS coordinates."""

    latitude: float
    longitude: float

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Coordinates | None:
        """Create Coordinates from a dictionary."""
        if not data:
            return None
        return cls(
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
        )


@dataclass
class Address:
    """Represents a physical address."""

    address1: str
    city: str
    zip: str
    country: str
    address2: str | None = None
    address3: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Address | None:
        """Create Address from a dictionary."""
        if not data:
            return None
        return cls(
            address1=data.get("address1", ""),
            address2=data.get("address2"),
            address3=data.get("address3"),
            zip=data.get("zip", ""),
            city=data.get("city", ""),
            country=data.get("country", ""),
        )


@dataclass
class Location:
    """Represents location information for a charge point."""

    coordinates: Coordinates | None = None
    address: Address | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Location | None:
        """Create Location from a dictionary."""
        if not data:
            return None
        return cls(
            coordinates=Coordinates.from_dict(data.get("coordinates")),
            address=Address.from_dict(data.get("address")),
        )


@dataclass
class Connector:
    """Represents a connector type available at a charge point."""

    identifier: str
    name: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Connector:
        """Create Connector from a dictionary."""
        return cls(
            identifier=data.get("identifier", ""),
            name=data.get("name", ""),
        )


@dataclass
class ChargePoint:
    """Represents a charge point (charging station)."""

    id: int
    visibility: str
    created_at: datetime
    updated_at: datetime
    location: Location
    connectors: list[Connector]
    name: str | None = None
    serial_number: str | None = None
    type: str | None = None
    state: str | None = None
    max_kw: float | None = None
    note: str | None = None
    last_meter_reading_kwh: float | None = None
    brand_name: str | None = None
    model_name: str | None = None
    firmware_version: str | None = None
    cable_plugged_in: bool = False
    charges: list[Charge] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChargePoint:
        """Create a ChargePoint from a dictionary."""
        # Parse charges if they exist in the data
        charges_data = data.get("charges", [])
        charges = [Charge.from_dict(charge) for charge in charges_data] if charges_data else []

        # Parse connectors
        connectors_data = data.get("connectors", [])
        connectors = [Connector.from_dict(conn) for conn in connectors_data]

        return cls(
            id=data["id"],
            name=data.get("name"),
            serial_number=data.get("serialNumber"),
            type=data.get("type"),
            state=data.get("state"),
            visibility=data.get("visibility", ""),
            max_kw=data.get("maxKw"),
            note=data.get("note"),
            last_meter_reading_kwh=data.get("lastMeterReadingKwh"),
            brand_name=data.get("brandName"),
            model_name=data.get("modelName"),
            firmware_version=data.get("firmwareVersion"),
            cable_plugged_in=data.get("cablePluggedIn", False),
            created_at=_parse_datetime(data.get("createdAt")),
            updated_at=_parse_datetime(data.get("updatedAt")),
            location=Location.from_dict(data.get("location")),
            connectors=connectors,
            charges=charges,
        )


@dataclass
class WalletTransaction:
    """Represents a wallet transaction."""

    id: int
    state: str
    summary: str
    from_amount: float
    from_currency: Currency | None
    to_amount: float
    to_currency: Currency | None
    exchange_rate: float
    note: str | None = None
    from_wallet_id: int | None = None
    to_wallet_id: int | None = None
    charge_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    completed_at: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WalletTransaction:
        """Create a WalletTransaction from a dictionary."""
        return cls(
            id=data["id"],
            state=data.get("state", ""),
            summary=data.get("summary", ""),
            note=data.get("note"),
            from_amount=data.get("fromAmount", 0.0),
            from_currency=Currency.from_dict(data.get("fromCurrency")),
            from_wallet_id=data.get("fromWalletId"),
            to_amount=data.get("toAmount", 0.0),
            to_currency=Currency.from_dict(data.get("toCurrency")),
            to_wallet_id=data.get("toWalletId"),
            charge_id=data.get("chargeId"),
            exchange_rate=data.get("exchangeRate", 1.0),
            created_at=_parse_datetime(data.get("createdAt")),
            updated_at=_parse_datetime(data.get("updatedAt")),
            completed_at=_parse_datetime(data.get("completedAt")),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert WalletTransaction to a dictionary for compatibility."""
        return {
            "id": self.id,
            "state": self.state,
            "summary": self.summary,
            "note": self.note,
            "fromAmount": self.from_amount,
            "fromCurrency": {
                "identifier": self.from_currency.identifier,
                "name": self.from_currency.name,
                "decimals": self.from_currency.decimals,
            } if self.from_currency else None,
            "fromWalletId": self.from_wallet_id,
            "toAmount": self.to_amount,
            "toCurrency": {
                "identifier": self.to_currency.identifier,
                "name": self.to_currency.name,
                "decimals": self.to_currency.decimals,
            } if self.to_currency else None,
            "toWalletId": self.to_wallet_id,
            "chargeId": self.charge_id,
            "exchangeRate": self.exchange_rate,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class TokenResponse:
    """Represents an authentication token response."""

    access_token: str
    access_token_expiration_date: datetime
    refresh_token: str
    refresh_token_expiration_date: datetime
    user_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TokenResponse:
        """Create a TokenResponse from a dictionary."""
        return cls(
            access_token=data["accessToken"],
            access_token_expiration_date=_parse_datetime(
                data["accessTokenExpirationDate"]
            ),
            refresh_token=data["refreshToken"],
            refresh_token_expiration_date=_parse_datetime(
                data["refreshTokenExpirationDate"]
            ),
            user_id=data.get("userId"),
        )


def _parse_datetime(date_string: str | None) -> datetime | None:
    """Parse a datetime string to a datetime object.

    Handles ISO 8601 format datetime strings and converts them to
    timezone-aware datetime objects in UTC.
    """
    if not date_string:
        return None
    if isinstance(date_string, datetime):
        return date_string

    # Parse ISO 8601 format
    try:
        # Try parsing with timezone info
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        # Ensure it's in UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, AttributeError):
        return None
