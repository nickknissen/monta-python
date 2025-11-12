# Monta

A Python client library for the Monta EV charging API.

## API Documentation

For complete API documentation, visit the official Monta API docs:
[https://docs.public-api.monta.com/reference/home](https://docs.public-api.monta.com/reference/home)

## Requirements

- Python 3.11 or higher
- aiohttp
- async-timeout

## Installation

This package is available on PyPI:
```bash
pip install monta
```

Alternatively, install from source with:
```bash
python -m pip install .
```

## Usage

Here's a basic example of how to use the Monta API client:

```python
import asyncio
import aiohttp
from monta import MontaApiClient

async def main():
    async with aiohttp.ClientSession() as session:
        # Initialize the client
        client = MontaApiClient(
            client_id="your_client_id",
            client_secret="your_client_secret",
            session=session,
        )

        # Get all charge points
        charge_points = await client.async_get_charge_points()
        for charge_point_id, charge_point in charge_points.items():
            print(f"Charge Point {charge_point_id}: {charge_point.name}")

        # Get a specific charge point with full details
        if charge_points:
            first_charge_point_id = next(iter(charge_points.keys()))
            charge_point = await client.async_get_charge_point(first_charge_point_id)

            # Access location information
            if charge_point.location and charge_point.location.coordinates:
                print(f"Location: {charge_point.location.coordinates.latitude}, "
                      f"{charge_point.location.coordinates.longitude}")

            # Access connector information
            print(f"Available connectors: {[c.name for c in charge_point.connectors]}")

            # Get charges for this charge point
            charges = await client.async_get_charges(first_charge_point_id)
            print(f"Found {len(charges)} charges")

        # Get wallet information
        wallet = await client.async_get_personal_wallet()
        print(f"Wallet balance: {wallet.balance.amount} {wallet.balance.currency.identifier}")

# Run the async function
asyncio.run(main())
```

### Available Methods

- `async_get_charge_points(page, per_page)` - Retrieve all available charge points with pagination
- `async_get_charge_point(charge_point_id)` - Get a specific charge point by ID with full details
- `async_get_charges(charge_point_id, state, from_date, to_date, page, per_page)` - Get charges for a specific charge point
- `async_start_charge(charge_point_id)` - Start a charging session
- `async_stop_charge(charge_id)` - Stop a charging session
- `async_get_personal_wallet()` - Get personal wallet information
- `async_get_wallet_transactions(state, from_date, to_date, page, per_page)` - Retrieve wallet transactions

## License

See LICENSE file for details.
