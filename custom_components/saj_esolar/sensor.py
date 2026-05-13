"""Sensor class for the SAJ eSolar entities — powered by pysaj-elekeeper."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
import logging
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from elekeeper import PlantOverview

import voluptuous as vol

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SENSORS
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import (
    CONF_LEGACY_VERIFY_SSL,
    CONF_PASSWORD,
    CONF_PLANT_UID,
    CONF_PROVIDER_DOMAIN,
    CONF_PROVIDER_PATH,
    CONF_PROVIDER_USE_SSL,
    CONF_RESOURCES,
    CONF_USERNAME,
    DOMAIN,
    H1_SENSORS,
    SAJ_SENSORS,
    SENSOR_TYPES,
)
from .coordinator import EsolarDataUpdateCoordinator

CONF_PLANT_ID: Final = "plant_id"

_LOGGER = logging.getLogger(__name__)

SENSOR_PREFIX = "esolar "  # do not change


# Migration from old saj_esolar yaml
PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_RESOURCES, default=[*SAJ_SENSORS, *H1_SENSORS]): vol.All(
            cv.ensure_list,
            [vol.In([*SAJ_SENSORS, *H1_SENSORS])],
        ),
        vol.Optional(CONF_SENSORS, default="None"): cv.string,
        vol.Optional(CONF_PLANT_ID, default=0): cv.positive_int,
        vol.Optional(CONF_PROVIDER_DOMAIN, default="eop.saj-electric.com"): cv.string,
        vol.Optional(CONF_PROVIDER_PATH, default="dev-api"): cv.string,
        vol.Optional(CONF_PROVIDER_USE_SSL, default=True): cv.boolean,
        vol.Optional(CONF_LEGACY_VERIFY_SSL, default=True): cv.boolean,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Import legacy YAML config into a config entry."""
    _LOGGER.warning(
        "YAML configuration for 'saj_esolar' is deprecated. "
        "Please remove it from configuration.yaml after migration"
    )
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "import"},
            data=config,
        )
    )


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable
):
    """Set up the eSolar sensors from a config entry."""
    coordinator: EsolarDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SAJeSolarMeterSensor(coordinator, description)
        for description in SENSOR_TYPES
    ]
    async_add_entities(entities, True)
    return True


class SAJeSolarMeterSensor(CoordinatorEntity[EsolarDataUpdateCoordinator], SensorEntity):
    """A single SAJ eSolar sensor reading from a PlantOverview."""

    def __init__(
        self,
        coordinator: EsolarDataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        _LOGGER.debug("Initializing esolar sensor: %s", description.key)
        self.entity_description = description
        self._attr_name = f"{SENSOR_PREFIX}{description.name}"
        self._attr_unique_id = f"{SENSOR_PREFIX}_{description.key}"
        self._attr_icon = description.icon
        self._attr_state_class = description.state_class
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_device_class = description.device_class

    @property
    def native_value(self) -> StateType | date | datetime:
        """Return the sensor value from the PlantOverview."""
        overview: PlantOverview | None = self.coordinator.data
        if overview is None:
            return None

        desc = self.entity_description
        if not hasattr(desc, "value_fn") or desc.value_fn is None:
            return None

        try:
            return desc.value_fn(overview)
        except Exception:  # noqa: BLE001
            _LOGGER.debug("Could not read value for sensor %s", desc.key)
            return None
