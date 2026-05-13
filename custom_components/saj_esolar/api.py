"""API adapter — wraps elekeeper.SajClient for use inside the coordinator."""

from __future__ import annotations

import logging

import httpx

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.httpx_client import get_async_client

from elekeeper import PlantOverview, SajApiError, SajAuthError, SajClient

_LOGGER = logging.getLogger(__name__)


class ApiError(HomeAssistantError):
    """Raised when a non-auth API call fails."""


class ApiAuthError(HomeAssistantError):
    """Raised when authentication fails."""


class EsolarApiClient:
    """Thin adapter that exposes a single `fetch_data()` coroutine returning a PlantOverview."""

    def __init__(
        self,
        hass: HomeAssistant,
        username: str,
        password: str,
        plant_uid: str | None = None,
        base_url: str = "https://eop.saj-electric.com",
    ) -> None:
        self._username = username
        self._password = password
        self._plant_uid = plant_uid
        self._client = SajClient(
            base_url=base_url,
            client=get_async_client(hass),
        )

    async def fetch_data(self) -> PlantOverview:
        """Login and return a fully-populated PlantOverview."""
        try:
            await self._client.login(self._username, self._password)
            return await self._client.get_plant_overview(self._plant_uid)
        except SajAuthError as err:
            raise ApiAuthError(str(err)) from err
        except SajApiError as err:
            raise ApiError(str(err)) from err
        except httpx.HTTPError as err:
            raise ApiError(f"Network error: {err}") from err

    async def verify_login(self) -> None:
        """Validate credentials by attempting a login (used by config flow)."""
        try:
            await self._client.login(self._username, self._password)
        except SajAuthError as err:
            raise ApiAuthError(str(err)) from err
        except SajApiError as err:
            raise ApiError(str(err)) from err
        except httpx.HTTPError as err:
            raise ApiError(f"Network error: {err}") from err
