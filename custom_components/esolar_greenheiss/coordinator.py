"""Coordinator for eSolar integration."""

import asyncio
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ApiAuthError, ApiError, EsolarApiClient

_LOGGER = logging.getLogger(__name__)


class EsolarDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching eSolar data from the API at regular intervals."""

    def __init__(self, hass: HomeAssistant, api_client: EsolarApiClient) -> None:
        """Initialize the esolar coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="eSolar Data Update Coordinator",
            update_interval=timedelta(minutes=5),
            always_update=True,
        )
        self.api_client = api_client

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        _LOGGER.debug("Coordinator async_update_data called")
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with asyncio.timeout(10):
                return await self.api_client.fetch_data()
        except ApiAuthError as err:
            raise ConfigEntryAuthFailed from err
        except ApiError as err:
            raise UpdateFailed("Error communicating with API") from err
