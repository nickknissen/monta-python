"""Tests for what the client does when the API refuses a token.

Access tokens last an hour and refresh tokens rotate, so being turned down
is routine and says nothing about the client id and secret. The client is
expected to work its way back to a usable token on its own, and to raise
only when the credentials themselves stop being accepted.
"""

from __future__ import annotations

import asyncio
from datetime import timedelta

import pytest

from monta import MontaApiClientAuthenticationError

from .conftest import FakeResponse, token_payload

WALLET = {"id": 1, "balance": {"amount": 10.0, "currency": "DKK"}}


def ok(payload: dict) -> FakeResponse:
    """Return a successful response."""
    return FakeResponse(200, payload)


def unauthorized() -> FakeResponse:
    """Return the response the API gives for a token it will not accept."""
    return FakeResponse(401, {"message": "Unauthorized"})


async def test_first_call_authenticates_with_the_credentials(build_client) -> None:
    """With nothing cached, the client mints a token set and uses it."""
    client, session = build_client(
        {
            "auth/token": [ok(token_payload("1"))],
            "wallets/personal": [ok(WALLET)],
        }
    )

    await client.async_get_personal_wallet()

    assert session.paths() == ["auth/token", "wallets/personal"]
    assert session.tokens_used()[-1] == "access-1"


async def test_expired_access_token_is_refreshed(build_client) -> None:
    """An access token near its expiry is refreshed, not re-minted."""
    client, session = build_client(
        {
            "auth/token": [ok(token_payload("1", timedelta(seconds=60)))],
            "auth/refresh": [ok(token_payload("2"))],
            "wallets/personal": [ok(WALLET)],
        }
    )

    # The first call mints a token that is already inside the preemptive
    # refresh window, so the second call has to replace it.
    await client.async_get_personal_wallet()
    await client.async_get_personal_wallet()

    assert session.count("auth/refresh") == 1
    assert session.count("auth/token") == 1
    assert session.tokens_used()[-1] == "access-2"


async def test_refused_refresh_token_falls_back_to_the_credentials(
    build_client,
) -> None:
    """A refresh token the API rejects is not the end of the road.

    Refresh tokens rotate and can be revoked, while the client id and secret
    stay good. Before this, a single rejected refresh was fatal: the stored
    expiry is a month out, so every later call retried the same dead token
    and the caller had no way back other than new credentials.
    """
    client, session = build_client(
        {
            "auth/token": [ok(token_payload("1", timedelta(seconds=60)))],
            "auth/refresh": [unauthorized()],
            "wallets/personal": [ok(WALLET)],
        }
    )

    await client.async_get_personal_wallet()
    session.set_responses("auth/token", [ok(token_payload("2"))])

    await client.async_get_personal_wallet()

    assert session.count("auth/refresh") == 1
    assert session.count("auth/token") == 2
    assert session.tokens_used()[-1] == "access-2"


async def test_refused_access_token_is_replaced_and_the_request_retried(
    build_client,
) -> None:
    """A token the client still believes in can be refused by the API.

    Validity is judged locally, against the expiry the API reported and this
    machine's clock, so the two ends can disagree: a slow clock, or a token
    revoked early. The refused token is dropped and the call tried again.
    """
    client, session = build_client(
        {
            "auth/token": [ok(token_payload("1"))],
            "auth/refresh": [ok(token_payload("2"))],
            "wallets/personal": [ok(WALLET)],
        },
        rejected_tokens={"access-1"},
    )

    wallet = await client.async_get_personal_wallet()

    assert wallet is not None
    assert session.count("wallets/personal") == 2
    assert session.tokens_used() == [None, "access-1", None, "access-2"]


async def test_a_refused_token_is_retried_only_once(build_client) -> None:
    """A token refused twice running is an authentication failure."""
    client, session = build_client(
        {
            "auth/token": [ok(token_payload("1"))],
            "auth/refresh": [ok(token_payload("2"))],
            "wallets/personal": [ok(WALLET)],
        },
        rejected_tokens={"access-1", "access-2"},
    )

    with pytest.raises(MontaApiClientAuthenticationError):
        await client.async_get_personal_wallet()

    assert session.count("wallets/personal") == 2


async def test_refused_credentials_raise(build_client) -> None:
    """Credentials the API will not accept are the caller's problem."""
    client, _ = build_client({"auth/token": [unauthorized()]})

    with pytest.raises(MontaApiClientAuthenticationError):
        await client.async_get_personal_wallet()


async def test_concurrent_refusals_replace_the_token_once(build_client) -> None:
    """Calls refused together share one replacement token.

    Replacing per call would have them rotating the refresh token out from
    under each other, so the losers would be refused again.
    """
    client, session = build_client(
        {
            "auth/token": [ok(token_payload("1"))],
            "auth/refresh": [ok(token_payload("2"))],
            "wallets/personal": [ok(WALLET)],
        }
    )

    # Prime the client so all three calls start from the same stored tokens,
    # then have the API stop accepting the token they are all holding.
    await client.async_get_personal_wallet()
    session.rejected_tokens.add("access-1")

    results = await asyncio.gather(
        client.async_get_personal_wallet(),
        client.async_get_personal_wallet(),
        client.async_get_personal_wallet(),
    )

    assert all(result is not None for result in results)
    assert session.count("auth/refresh") == 1
    assert session.count("auth/token") == 1


async def test_start_charge_survives_a_refused_token(build_client) -> None:
    """The retry reaches the calls that act, not just the ones that read."""
    charge = {"id": 5, "chargePointId": 1, "state": "started"}
    client, session = build_client(
        {
            "auth/token": [ok(token_payload("1"))],
            "auth/refresh": [ok(token_payload("2"))],
            "charges": [ok(charge)],
        },
        rejected_tokens={"access-1"},
    )

    started = await client.async_start_charge(1)

    assert started.id == 5
    assert session.count("charges") == 2
