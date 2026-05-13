"""Coordinator for eSolar integration."""

from __future__ import annotations
import asyncio
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from elekeeper import PlantOverview

from .api import ApiAuthError, ApiError, EsolarApiClient

_LOGGER = logging.getLogger(__name__)


class EsolarDataUpdateCoordinator(DataUpdateCoordinator[PlantOverview]):
    """Fetch PlantOverview from the Elekeeper API at regular intervals."""

    def __init__(self, hass: HomeAssistant, api_client: EsolarApiClient) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="eSolar Data Update Coordinator",
            update_interval=timedelta(minutes=5),
            always_update=True,
        )
        self.api_client = api_client

    async def _async_update_data(self) -> PlantOverview:
        """Fetch data from the Elekeeper API."""
        _LOGGER.debug("Coordinator async_update_data called")
        try:
            async with asyncio.timeout(60):
                return await self.api_client.fetch_data()
        except ApiAuthError as err:
            raise ConfigEntryAuthFailed from err
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unexpected exception in coordinator")
            raise UpdateFailed(f"Unknown error: {err}") from err
