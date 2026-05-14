"""The SAJ eSolar component — powered by pysaj-elekeeper."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import EsolarApiClient
from .const import (
    CONF_PASSWORD,
    CONF_PLANT_UID,
    CONF_USERNAME,
    DOMAIN,
)
from .coordinator import EsolarDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor"]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities=None
) -> bool:
    """Set up the SAJ eSolar config entry."""
    _LOGGER.debug("Setting up eSolar entry: %s", entry.entry_id)
    config = entry.data

    api = EsolarApiClient(
        hass,
        username=config[CONF_USERNAME],
        password=config[CONF_PASSWORD],
        plant_uid=config.get(CONF_PLANT_UID) or None,
        base_url=config.get("base_url", "https://eop.saj-electric.com"),
    )
    coordinator = EsolarDataUpdateCoordinator(hass, api)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
