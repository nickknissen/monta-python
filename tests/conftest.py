"""Fixtures for the Monta client tests."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from monta import MontaApiClient, TokenStorage


def iso(offset: timedelta) -> str:
    """Return an ISO 8601 timestamp the given distance from now."""
    return (datetime.now(timezone.utc) + offset).isoformat()


def token_payload(
    suffix: str,
    access_token_lifetime: timedelta = timedelta(hours=1),
    refresh_token_lifetime: timedelta = timedelta(days=31),
) -> dict[str, Any]:
    """Return what the API answers with on auth/token and auth/refresh."""
    return {
        "accessToken": f"access-{suffix}",
        "accessTokenExpirationDate": iso(access_token_lifetime),
        "refreshToken": f"refresh-{suffix}",
        "refreshTokenExpirationDate": iso(refresh_token_lifetime),
        "userId": "user-1",
    }


class FakeResponse:
    """The parts of an aiohttp response the client reads."""

    def __init__(self, status: int, payload: Any) -> None:
        self.status = status
        self.headers: dict[str, str] = {}
        self._payload = payload

    def raise_for_status(self) -> None:
        """Do nothing: the client checks the statuses it cares about."""

    async def json(self) -> Any:
        """Return the response body."""
        return self._payload


class RecordingTokenStorage(TokenStorage):
    """Token storage that keeps a copy of every set it was asked to save.

    A store that outlives the process serialises what it is handed, so it
    never sees a later in-place edit to the same dict. Copying here is what
    makes a test able to tell a token that was dropped from one that was only
    dropped in memory.
    """

    def __init__(self) -> None:
        self.saved: list[dict[str, Any]] = []

    async def load(self) -> dict[str, Any] | None:
        """Return a copy of the last set saved, if there is one."""
        return deepcopy(self.saved[-1]) if self.saved else None

    async def save(self, data: dict[str, Any]) -> None:
        """Record a copy of the set being saved."""
        self.saved.append(deepcopy(data))

    def access_tokens(self) -> list[str | None]:
        """Return the access token in each saved set, in order."""
        return [entry["access_token"] for entry in self.saved]


class FakeSession:
    """Answers requests from a per-path script.

    Each path maps to a list of responses, consumed in order; the last one
    repeats once the list runs out, so a test only has to spell out the
    responses that differ.

    Tokens in ``rejected_tokens`` are refused wherever they are presented,
    which is how the API behaves: it turns down a particular token, not the
    next request to arrive. Scripting the refusals per path instead would
    make the result depend on the order concurrent calls happen to reach it.
    """

    def __init__(
        self,
        responses: dict[str, list[FakeResponse]],
        rejected_tokens: set[str] | None = None,
    ) -> None:
        self._responses = responses
        self.rejected_tokens = rejected_tokens or set()
        self.requests: list[dict[str, Any]] = []

    def set_responses(self, path: str, responses: list[FakeResponse]) -> None:
        """Replace what a path answers with from here on."""
        self._responses[path] = responses

    def paths(self) -> list[str]:
        """Return the path of every request made, in order."""
        return [request["path"] for request in self.requests]

    def tokens_used(self) -> list[str | None]:
        """Return the bearer token sent with each request, in order."""
        return [request["token"] for request in self.requests]

    def count(self, path: str) -> int:
        """Return how many requests were made to paths starting with path."""
        return len([p for p in self.paths() if p.startswith(path)])

    async def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        json: dict | None = None,  # noqa: A002
    ) -> FakeResponse:
        """Return the next scripted response for the requested path."""
        path = url.split("/api/v1/", 1)[1]
        authorization = (headers or {}).get("authorization", "")
        token = authorization.removeprefix("Bearer ") or None
        self.requests.append(
            {"method": method, "path": path, "body": json, "token": token}
        )

        if token is not None and token in self.rejected_tokens:
            return FakeResponse(401, {"message": "Unauthorized"})

        key = next(
            (known for known in self._responses if path.startswith(known)), None
        )
        if key is None:
            raise AssertionError(f"unexpected request to {path}")

        scripted = self._responses[key]
        return scripted.pop(0) if len(scripted) > 1 else scripted[0]


@pytest.fixture
def build_client():  # noqa: ANN201
    """Return a factory building a client over a scripted session."""

    def build(
        responses: dict[str, list[FakeResponse]],
        rejected_tokens: set[str] | None = None,
        token_storage: TokenStorage | None = None,
    ) -> tuple[MontaApiClient, FakeSession]:
        session = FakeSession(responses, rejected_tokens)
        client = MontaApiClient(
            client_id="client-id",
            client_secret="client-secret",
            session=session,  # type: ignore[arg-type]
            token_storage=token_storage,
        )
        return client, session

    return build
