"""Sensor class for the esolar entities.

This Sensor will read the private api of the eSolar portal at https://inversores-style.greenheiss.com
"""

from collections.abc import Callable
from datetime import date, datetime
import logging
from typing import Any, Final

import voluptuous as vol

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SENSORS
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_PASSWORD,
    CONF_PROVIDER_DOMAIN,
    CONF_PROVIDER_PATH,
    CONF_PROVIDER_USE_SSL,
    CONF_PROVIDER_VERIFY_SSL,
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

DEVICE_TYPES = {
    "Inverter": 0,
    "Meter": 1,  # TODO: Pending to confirm
    "Battery": 2,
    0: "Inverter",
    1: "Meter",  # TODO: Pending to confirm
    2: "Battery",
}

SENSOR_PREFIX = "esolar "  # do not change


def _toPercentage(value: str) -> str:
    return float(value.strip("%"))


# Migration from old saj_esolar yaml
PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_RESOURCES, default=[*SAJ_SENSORS, *H1_SENSORS]): vol.All(  # type: ignore
            cv.ensure_list,
            [vol.In([*SAJ_SENSORS, *H1_SENSORS])],  # type: ignore
        ),
        vol.Optional(CONF_SENSORS, default="None"): cv.string,  # type: ignore
        vol.Optional(CONF_PLANT_ID, default=0): cv.positive_int,  # type: ignore
        vol.Optional(CONF_PROVIDER_DOMAIN, default="fop.saj-electric.com"): cv.string,
        vol.Optional(CONF_PROVIDER_PATH, default="saj"): cv.string,
        vol.Optional(CONF_PROVIDER_USE_SSL, default="True"): cv.boolean,
        vol.Optional("provider_ssl", default=True): cv.boolean,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Import legacy YAML config into a config entry."""
    _LOGGER.warning(
        "YAML configuration for 'saj_esolar' is deprecated. "
        "Please remove it from configuration.yaml after migration"
    )
    _LOGGER.debug("Imported configuration: %s", config)
    # Forward the YAML data into the new config flow
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
    coordinator = hass.data[DOMAIN][entry.entry_id]
    config = entry.data
    entities = []
    if config[CONF_SENSORS] == "h1":
        sensorlist = H1_SENSORS
    else:
        sensorlist = SAJ_SENSORS

    for description in SENSOR_TYPES:
        if description.key in sensorlist:
            sensor = SAJeSolarMeterSensor(
                coordinator,
                description,
                config.get(CONF_SENSORS),
                config.get(CONF_PLANT_ID),
            )
            entities.append(sensor)
    async_add_entities(entities, True)
    return True


class SAJeSolarMeterSensor(CoordinatorEntity, SensorEntity):
    """Collecting data and return sensor entity."""

    def __init__(
        self,
        coordinator: EsolarDataUpdateCoordinator,
        description: SensorEntityDescription,
        sensors: str,
        plant_id: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        _LOGGER.debug("Initializing esolar sensor: %s", description.key)
        self.entity_description = description
        self._state = None
        self.sensors = sensors
        self.plant_id = plant_id
        self._type = self.entity_description.key
        self._attr_icon = self.entity_description.icon
        self._attr_name = f"{SENSOR_PREFIX}{self.entity_description.name}"
        self._attr_state_class = self.entity_description.state_class
        self._attr_native_unit_of_measurement = (
            self.entity_description.native_unit_of_measurement
        )
        self._attr_device_class = self.entity_description.device_class
        self._attr_unique_id = f"{SENSOR_PREFIX}_{self._type}"

        self._discovery = False
        self._dev_id = {}

    @property
    def native_value(self) -> StateType | date | datetime:
        """Handle updated data from the coordinator."""
        energy = self.coordinator.data
        if energy is None:
            _LOGGER.ERROR("Did not found data for eSolar")
            return None
        # find the data in the data from the coordinator based on the type of sensor this is.
        self.match_basic_cases(energy)
        ## SAJ h1
        # I dont have an H1, so this is untested
        if self.sensors == "h1":
            self.match_h1_sensors(energy)

        #### Sec module Sensors:
        if self.sensors == "saj_sec":
            self.match_sec_sensors(energy)

        # -Debug- adding sensor
        _LOGGER.debug("Device: %s , State %s", self._type, self._state)
        return self._state

    def match_basic_cases(self, energy: dict):
        """Matches the basic cases common for h1 and sec."""
        match self._type:
            case "devOnlineNum":
                self._state = _get_value_from_deep(
                    energy,
                    ["plantDetail", self._type],
                    bool,
                )
            case "runningState":
                self._state = _get_value_from_deep(
                    energy,
                    ["plantDetail", self._type],
                    lambda x: bool(int(x)),
                )
            case n if n in (
                "nowPower",
                "todayElectricity",
                "monthElectricity",
                "yearElectricity",
                "totalElectricity",
                "todayGridIncome",
                "income",
                "totalBuyElec",
                "totalConsumpElec",
                "totalSellElec",
                "totalPlantTreeNum",
                "totalReduceCo2",
            ):
                self._state = _get_value_from_deep(
                    energy,
                    ["plantDetail", self._type],
                    float,
                )
            case "selfUseRate":
                self._state = _get_value_from_deep(
                    energy,
                    ["plantDetail", self._type],
                    _toPercentage,
                )
            case "lastUploadTime":
                self._state = _get_value_from_deep(
                    energy,
                    ["plantDetail", self._type],
                    lambda x: x,  # as-is
                )
            case n if n in (
                "currency",
                "plantuid",
                "plantname",
                "address",
            ):
                if self._type in energy["plantList"][self.plant_id]:
                    value = energy.get("plantList", {})[self.plant_id].get(self._type)
                    self._state = value if value is not None else None
            # there is a typo (systemPower vs systempower). It was present in the original integration. keeping for consistency
            case "systemPower":
                if "systempower" in energy["plantList"][self.plant_id]:
                    value = energy.get("plantList", {})[self.plant_id].get(
                        "systempower"
                    )
                    self._state = value if value is not None else None
            case "isOnline":
                if "isOnline" in energy["plantList"][self.plant_id]:
                    value = energy.get("plantList", {})[self.plant_id].get(self._type)
                    self._state = value.upper() == "Y" if value is not None else None
            case "peakPower":
                if "peakPower" in energy:
                    if energy["peakPower"] is not None:
                        self._state = float(energy["peakPower"])
            case "status":
                if "status" in energy:
                    if energy["status"] is not None:
                        self._state = energy["status"]

    def match_h1_sensors(self, energy: dict):
        match self._type:
            # float cases
            case n if n in (
                "chargeElec",
                "dischargeElec",
                "buyElec",
                "sellElec",
                "pvElec",
                "selfConsumedEnergy1",
                "selfConsumedEnergy2",
                "useElec",
            ):
                self._state = _get_value_from_deep(
                    energy,
                    ["viewBean", self._type],
                    float,
                )
            # percentage cases
            case n if n in (
                "buyRate",
                "selfConsumedRate1",
                "selfConsumedRate2",
                "sellRate",
            ):
                self._state = _get_value_from_deep(
                    energy,
                    ["viewBean", self._type],
                    _toPercentage,
                )
            # storeDevicePower
            # float cases
            case n if n in (
                "batCapcity",
                "batCurr",
                "batEnergyPercent",
                "batteryPower",
                "gridPower",
                "pvPower",
                "solarPower",
                "outPower",
            ):
                self._state = _get_value_from_deep(
                    energy,
                    ["storeDevicePower", self._type],
                    float,
                )
            case "isStorageAlarm":
                self._state = _get_value_from_deep(
                    energy,
                    ["storeDevicePower", self._type],
                    int,
                )
            case "batteryDirection":
                if "batteryDirection" in energy["storeDevicePower"]:
                    if energy["storeDevicePower"]["batteryDirection"] is not None:
                        if energy["storeDevicePower"]["batteryDirection"] == 0:
                            self._state = "Standby"
                        elif energy["storeDevicePower"]["batteryDirection"] == 1:
                            self._state = "Discharging"
                        elif energy["storeDevicePower"]["batteryDirection"] == -1:
                            self._state = "Charging"
                        else:
                            self._state = f"Unknown: {energy['storeDevicePower']['batteryDirection']}"

            case "gridDirection":
                if "gridDirection" in energy["storeDevicePower"]:
                    if energy["storeDevicePower"]["gridDirection"] is not None:
                        if energy["storeDevicePower"]["gridDirection"] == 1:
                            self._state = "Exporting"
                        elif energy["storeDevicePower"]["gridDirection"] == -1:
                            self._state = "Importing"
                        else:
                            self._state = energy["storeDevicePower"]["gridDirection"]
                            _LOGGER.error(
                                "Grid Direction unknown value: %s",
                                self._state,
                            )

            case "h1Online":
                if "isOnline" in energy["storeDevicePower"]:
                    if energy["storeDevicePower"]["isOnline"] is not None:
                        self._state = bool(int(energy["storeDevicePower"]["isOnline"]))
            case "outPutDirection":
                if "outPutDirection" in energy["storeDevicePower"]:
                    if energy["storeDevicePower"]["outPutDirection"] is not None:
                        if energy["storeDevicePower"]["outPutDirection"] == 1:
                            self._state = "Exporting"
                        elif energy["storeDevicePower"]["outPutDirection"] == -1:
                            self._state = "Importing"
                        else:
                            self._state = energy["storeDevicePower"]["outPutDirection"]
                            _LOGGER.error(
                                "Value for outPut Direction unknown: %s",
                                self._state,
                            )
            case "pvDirection":
                if "pvDirection" in energy["storeDevicePower"]:
                    if energy["storeDevicePower"]["pvDirection"] is not None:
                        if energy["storeDevicePower"]["pvDirection"] == 1:
                            self._state = "Exporting"
                        elif energy["storeDevicePower"]["pvDirection"] == -1:
                            self._state = "Importing"
                        else:
                            self._state = energy["storeDevicePower"]["pvDirection"]
                            _LOGGER.error(
                                "Value for pv Direction unknown: %s",
                                self._state,
                            )

    def match_sec_sensors(self, energy: dict):
        """Matches data for sec module sensors."""
        # getPlantMeterChartData - viewBeam
        match self._type:
            # float cases
            case n if n in (
                "pvElec",
                "useElec",
                "buyElec",
                "sellElec",
                "selfConsumedEnergy1",
                "selfConsumedEnergy2",
                "reduceCo2",
                "plantTreeNum",
            ):
                self._state = _get_value_from_deep(
                    energy,
                    ["getPlantMeterChartData", "viewBean", self._type],
                    float,
                )
            # percentage cases
            case n if n in (
                "buyRate",
                "sellRate",
                "selfConsumedRate1",
                "selfConsumedRate2",
            ):
                self._state = _get_value_from_deep(
                    energy,
                    ["getPlantMeterChartData", "viewBean", self._type],
                    _toPercentage,
                )
            case "homeLoadPower":
                value = energy.get("getPlantMeterChartData", {}).get(
                    "dataCountList", {}
                )[1][-1]
                self._state = float(value) if value is not None else None
            case "solarLoadPower":
                value = energy.get("getPlantMeterChartData", {}).get(
                    "dataCountList", {}
                )[2][-1]
                self._state = float(value) if value is not None else None
            case "exportPower":
                value = energy.get("getPlantMeterChartData", {}).get(
                    "dataCountList", {}
                )[3][-1]
                self._state = float(value) if value is not None else None
            case "gridLoadPower":
                value = energy.get("getPlantMeterChartData", {}).get(
                    "dataCountList", {}
                )[4][-1]
                self._state = float(value) if value is not None else None
            # getPlantMeterDetailInfo
            case "selfUseRate":
                self._state = _get_value_from_deep(
                    energy,
                    ["getPlantMeterDetailInfo", "plantDetail", self._type],
                    _toPercentage,
                )
            case n if n in (
                "totalPvEnergy",
                "totalLoadEnergy",
                "totalBuyEnergy",
                "totalSellEnergy",
            ):
                self._state = _get_value_from_deep(
                    energy,
                    ["getPlantMeterDetailInfo", "plantDetail", self._type],
                    float,
                )


def _get_value_from_deep(
    dictionary: dict, keys: list[str], lambda_funct: Callable[[Any], Any] = lambda x: x
) -> Any:
    """Access a nested object in dictionary with a list of keys.

    Receives a lambda to transform the value to the right type.
    """
    for key in keys:
        dictionary = dictionary.get(key, {})
    return lambda_funct(dictionary) if dictionary else None
