"""Constants for the SAJ eSolar integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)

DOMAIN = "saj_esolar"

# configuration entry keys
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SENSORS = "sensors"
CONF_PLANT_ID = "plant_id"
CONF_PLANT_UID = "plant_uid"
CONF_PROVIDER_DOMAIN = "provider_domain"
CONF_PROVIDER_PATH = "provider_path"
CONF_PROVIDER_USE_SSL = "provider_use_ssl"
CONF_PROVIDER_VERIFY_SSL = "provider_verify_ssl"
CONF_LEGACY_VERIFY_SSL = "provider_ssl"
CONF_RESOURCES = "resources"


@dataclass(frozen=True)
class SajSensorDescription(SensorEntityDescription):
    """SensorEntityDescription extended with a PlantOverview accessor."""

    value_fn: Callable[[Any], Any] | None = None


# Sensor lists kept for YAML migration compat
BASIC_SENSORS = [
    "nowPower", "runningState", "devOnlineNum", "todayElectricity",
    "monthElectricity", "yearElectricity", "totalElectricity",
    "todayGridIncome", "income", "lastUploadTime", "totalPlantTreeNum",
    "totalReduceCo2", "plantuid", "plantname", "currency", "address",
    "isOnline", "status", "peakPower", "systemPower",
    "pvElec", "useElec", "buyElec", "sellElec", "buyRate", "sellRate",
    "selfUseRate", "selfConsumedRate1", "selfConsumedRate2",
    "selfConsumedEnergy1", "selfConsumedEnergy2", "plantTreeNum", "reduceCo2",
]

SAJ_SENSORS = [
    *BASIC_SENSORS,
    "totalPvEnergy", "totalLoadEnergy", "totalBuyEnergy", "totalSellEnergy",
    "gridLoadPower", "solarLoadPower", "homeLoadPower", "exportPower", "powerFlow",
]

H1_SENSORS = [
    *BASIC_SENSORS,
    "totalBuyElec", "totalConsumpElec", "totalSellElec",
    "chargeElec", "dischargeElec",
    "isStorageAlarm", "batCapcity", "batCurr", "batEnergyPercent",
    "batteryDirection", "batteryPower", "gridDirection", "gridPower",
    "h1Online", "outPower", "outPutDirection", "pvDirection", "pvPower", "solarPower",
]

SENSOR_TYPES: Final[tuple[SajSensorDescription, ...]] = (
    # ── Live power ──────────────────────────────────────────────────────────
    SajSensorDescription(
        key="nowPower",
        name="nowPower",
        icon="mdi:solar-power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: o.pv_power_w,
    ),
    SajSensorDescription(
        key="pvPower",
        name="pvPower",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: o.pv_power_w,
    ),
    SajSensorDescription(
        key="solarPower",
        name="solarPower",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: o.pv_power_w,
    ),
    SajSensorDescription(
        key="homeLoadPower",
        name="homeLoadPower",
        icon="mdi:home-lightning-bolt-outline",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: o.load_power_w,
    ),
    SajSensorDescription(
        key="outPower",
        name="outPower",
        icon="mdi:home-lightning-bolt-outline",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: o.load_power_w,
    ),
    SajSensorDescription(
        key="totalLoadPower",
        name="totalLoadPower",
        icon="mdi:home-lightning-bolt-outline",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: o.load_power_w,
    ),
    SajSensorDescription(
        key="gridPower",
        name="gridPower",
        icon="mdi:transmission-tower",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: o.grid_power_w,
    ),
    SajSensorDescription(
        key="totalGridPower",
        name="totalGridPower",
        icon="mdi:transmission-tower",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: o.grid_power_w,
    ),
    SajSensorDescription(
        key="gridLoadPower",
        name="gridLoadPower",
        icon="mdi:transmission-tower-import",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: (
            o.grid_power_w if o.grid_power_w is not None and o.grid_power_w > 0 else 0.0
        ),
    ),
    SajSensorDescription(
        key="exportPower",
        name="exportPower",
        icon="mdi:transmission-tower-export",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: (
            abs(o.grid_power_w) if o.grid_power_w is not None and o.grid_power_w < 0 else 0.0
        ),
    ),
    SajSensorDescription(
        key="solarLoadPower",
        name="solarLoadPower",
        icon="mdi:solar-power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: o.pv_power_w,
    ),
    SajSensorDescription(
        key="totalPvgenPower",
        name="totalPvgenPower",
        icon="mdi:solar-panel",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: o.pv_power_w,
    ),
    SajSensorDescription(
        key="powerFlow",
        name="Power Flow",
        icon="mdi:transmission-tower",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        # positive = importing, negative = exporting (matches original beta logic)
        value_fn=lambda o: o.grid_power_w,
    ),
    # ── Battery live ────────────────────────────────────────────────────────
    SajSensorDescription(
        key="batteryPower",
        name="batteryPower",
        icon="mdi:battery-charging",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: o.battery_power_w,
    ),
    SajSensorDescription(
        key="batteryDirection",
        name="batteryDirection",
        icon="mdi:battery-sync",
        value_fn=lambda o: o.battery_direction,
    ),
    SajSensorDescription(
        key="gridDirection",
        name="gridDirection",
        icon="mdi:transmission-tower",
        value_fn=lambda o: o.grid_direction,
    ),
    SajSensorDescription(
        key="pvDirection",
        name="pvDirection",
        icon="mdi:solar-power-variant",
        value_fn=lambda o: (
            "Exporting" if o.pv_power_w is not None and o.pv_power_w > 0 else "Standby"
        ),
    ),
    SajSensorDescription(
        key="outPutDirection",
        name="outPutDirection",
        icon="mdi:home-lightning-bolt-outline",
        value_fn=lambda o: (
            "Exporting" if o.load_power_w is not None and o.load_power_w > 0 else "Standby"
        ),
    ),
    # ── Battery state ────────────────────────────────────────────────────────
    SajSensorDescription(
        key="batEnergyPercent",
        name="batEnergyPercent",
        icon="mdi:battery-heart-variant",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: o.battery_soc_percent,
    ),
    SajSensorDescription(
        key="batCapcity",
        name="batCapcity",
        icon="mdi:battery-check",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: o.battery_soh_percent,
    ),
    SajSensorDescription(
        key="batCurr",
        name="batCurr",
        icon="mdi:current-dc",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: o.battery_current_a,
    ),
    SajSensorDescription(
        key="batVoltage",
        name="batVoltage",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: o.battery_voltage_v,
    ),
    SajSensorDescription(
        key="batTemperature",
        name="batTemperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda o: o.battery_temperature,
    ),
    SajSensorDescription(
        key="isStorageAlarm",
        name="isStorageAlarm",
        icon="mdi:battery-alert",
        value_fn=lambda o: None,  # not exposed by Elekeeper API — kept for compat
    ),
    SajSensorDescription(
        key="h1Online",
        name="h1Online",
        icon="mdi:connection",
        value_fn=lambda o: None,  # not exposed by Elekeeper API — kept for compat
    ),
    # ── Today energy ─────────────────────────────────────────────────────────
    SajSensorDescription(
        key="todayElectricity",
        name="todayElectricity",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda o: o.today_pv_energy_kwh,
    ),
    SajSensorDescription(
        key="pvElec",
        name="pvElec",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        value_fn=lambda o: o.today_pv_energy_kwh,
    ),
    SajSensorDescription(
        key="useElec",
        name="useElec",
        icon="mdi:home-lightning-bolt-outline",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda o: o.today_load_energy_kwh,
    ),
    SajSensorDescription(
        key="buyElec",
        name="buyElec",
        icon="mdi:transmission-tower-import",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda o: o.today_grid_import_kwh,
    ),
    SajSensorDescription(
        key="sellElec",
        name="sellElec",
        icon="mdi:transmission-tower-export",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda o: o.today_grid_export_kwh,
    ),
    SajSensorDescription(
        key="chargeElec",
        name="chargeElec",
        icon="mdi:battery-arrow-up",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda o: o.today_battery_charge_kwh,
    ),
    SajSensorDescription(
        key="dischargeElec",
        name="dischargeElec",
        icon="mdi:battery-arrow-down",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda o: o.today_battery_discharge_kwh,
    ),
    # ── Total / lifetime energy ───────────────────────────────────────────────
    SajSensorDescription(
        key="totalElectricity",
        name="totalElectricity",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda o: o.total_pv_energy_kwh,
    ),
    SajSensorDescription(
        key="totalPvEnergy",
        name="totalPvEnergy",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda o: o.total_pv_energy_kwh,
    ),
    SajSensorDescription(
        key="totalLoadEnergy",
        name="totalLoadEnergy",
        icon="mdi:home-lightning-bolt-outline",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda o: o.total_load_energy_kwh,
    ),
    SajSensorDescription(
        key="totalConsumpElec",
        name="totalConsumpElec",
        icon="mdi:home-lightning-bolt-outline",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        value_fn=lambda o: o.total_load_energy_kwh,
    ),
    SajSensorDescription(
        key="totalBuyElec",
        name="totalBuyElec",
        icon="mdi:transmission-tower-import",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda o: o.total_grid_import_kwh,
    ),
    SajSensorDescription(
        key="totalBuyEnergy",
        name="totalBuyEnergy",
        icon="mdi:transmission-tower-import",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda o: o.total_grid_import_kwh,
    ),
    SajSensorDescription(
        key="totalSellElec",
        name="totalSellElec",
        icon="mdi:transmission-tower-export",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda o: o.total_grid_export_kwh,
    ),
    SajSensorDescription(
        key="totalSellEnergy",
        name="totalSellEnergy",
        icon="mdi:transmission-tower-export",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda o: o.total_grid_export_kwh,
    ),
    # ── Monthly / yearly (not exposed by Elekeeper — kept for compat) ─────────
    SajSensorDescription(
        key="monthElectricity",
        name="monthElectricity",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="yearElectricity",
        name="yearElectricity",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        value_fn=lambda o: None,
    ),
    # ── Plant metadata ────────────────────────────────────────────────────────
    SajSensorDescription(
        key="runningState",
        name="runningState",
        icon="mdi:state-machine",
        value_fn=lambda o: o.mode,
    ),
    SajSensorDescription(
        key="devOnlineNum",
        name="devOnlineNum",
        icon="mdi:devices",
        value_fn=lambda o: len(o.devices) if o.devices else None,
    ),
    SajSensorDescription(
        key="lastUploadTime",
        name="lastUploadTime",
        icon="mdi:timer-sand",
        value_fn=lambda o: o.updated_at,
    ),
    SajSensorDescription(
        key="plantuid",
        name="plantuid",
        icon="mdi:api",
        value_fn=lambda o: o.uid,
    ),
    SajSensorDescription(
        key="plantname",
        name="plantname",
        icon="mdi:solar-power-variant-outline",
        value_fn=lambda o: o.name,
    ),
    SajSensorDescription(
        key="isOnline",
        name="isOnline",
        icon="mdi:connection",
        value_fn=lambda o: o.mode is not None,
    ),
    SajSensorDescription(
        key="status",
        name="status",
        icon="mdi:list-status",
        value_fn=lambda o: o.mode,
    ),
    # ── Fields not available in Elekeeper — kept as None for compat ───────────
    SajSensorDescription(
        key="todayGridIncome",
        name="todayGridIncome",
        icon="mdi:currency-eur",
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="income",
        name="income",
        icon="mdi:currency-eur",
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="totalPlantTreeNum",
        name="totalPlantTreeNum",
        icon="mdi:tree",
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="totalReduceCo2",
        name="totalReduceCo2",
        icon="mdi:molecule-co2",
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="plantTreeNum",
        name="plantTreeNum",
        icon="mdi:tree",
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="reduceCo2",
        name="reduceCo2",
        icon="mdi:molecule-co2",
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="currency",
        name="currency",
        icon="mdi:currency-eur",
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="address",
        name="address",
        icon="mdi:map-marker",
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="peakPower",
        name="peakPower",
        icon="mdi:solar-panel",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="systemPower",
        name="systemPower",
        icon="mdi:solar-panel",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="buyRate",
        name="buyRate",
        icon="mdi:transmission-tower-import",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="sellRate",
        name="sellRate",
        icon="mdi:transmission-tower-export",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="selfUseRate",
        name="selfUseRate",
        icon="mdi:home-lightning-bolt-outline",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="selfConsumedRate1",
        name="selfConsumedRate1",
        icon="mdi:home-lightning-bolt-outline",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="selfConsumedRate2",
        name="selfConsumedRate2",
        icon="mdi:home-lightning-bolt-outline",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="selfConsumedEnergy1",
        name="selfConsumedEnergy1",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        value_fn=lambda o: None,
    ),
    SajSensorDescription(
        key="selfConsumedEnergy2",
        name="selfConsumedEnergy2",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        value_fn=lambda o: None,
    ),
)
