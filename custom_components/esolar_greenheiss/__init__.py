"""The eSolar SAJ (and their resellers) component."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import EsolarApiClient, ESolarConfiguration, EsolarProvider
from .const import (
    CONF_PASSWORD,
    CONF_PLANT_ID,
    CONF_PROVIDER_DOMAIN,
    CONF_PROVIDER_PATH,
    CONF_PROVIDER_USE_SSL,
    CONF_PROVIDER_VERIFY_SSL,
    CONF_SENSORS,
    CONF_USERNAME,
    DOMAIN,
)
from .coordinator import EsolarDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# our platform only has sensors, no switches
PLATFORMS: list[str] = ["sensor"]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities=None
) -> bool:
    """Setup integration config entry."""
    _LOGGER.debug("Setting up eSolar entry: %s", entry.entry_id)
    configEntry = entry.data

    provider = EsolarProvider(
        configEntry.get(CONF_PROVIDER_DOMAIN),
        configEntry.get(CONF_PROVIDER_PATH),
        configEntry.get(CONF_PROVIDER_USE_SSL, True),
        configEntry.get(CONF_PROVIDER_VERIFY_SSL, True),
    )
    esolarConfig = ESolarConfiguration(
        configEntry.get(CONF_USERNAME),
        configEntry.get(CONF_PASSWORD),
        configEntry.get(CONF_SENSORS),
        configEntry.get(CONF_PLANT_ID),
        provider,
    )

    api = EsolarApiClient(hass, esolarConfig)
    coordinator = EsolarDataUpdateCoordinator(hass, api)

    # Perform the first refresh
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a configEntry entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a configEntry entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
