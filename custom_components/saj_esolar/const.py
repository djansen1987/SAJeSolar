"""Constants for the eSolar Greenheiss integration."""

from typing import Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower

DOMAIN = "saj_esolar"

# configuration entry data
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SENSORS = "sensors"
CONF_PLANT_ID = "plant_id"
CONF_PROVIDER_DOMAIN = "provider_domain"
CONF_PROVIDER_PATH = "provider_path"
CONF_PROVIDER_USE_SSL = "provider_use_ssl"
CONF_PROVIDER_VERIFY_SSL = "provider_verify_ssl"
CONF_RESOURCES = "resources"

DEVICE_TYPES = {
    "Inverter": 0,
    "Meter": 1,  # TODO: Pending to confirm
    "Battery": 2,
    0: "Inverter",
    1: "Meter",  # TODO: Pending to confirm
    2: "Battery",
}


BASIC_SENSORS = [
    "nowPower",
    "runningState",
    "devOnlineNum",
    "todayElectricity",
    "monthElectricity",
    "yearElectricity",
    "totalElectricity",
    "todayGridIncome",
    "income",
    "lastUploadTime",
    "totalPlantTreeNum",
    "totalReduceCo2",
    "plantuid",
    "plantname",
    "currency",
    "address",
    "isOnline",
    "status",
    "peakPower",
    "systemPower",
    "pvElec",
    "useElec",
    "buyElec",
    "sellElec",
    "buyRate",
    "sellRate",
    "selfUseRate",
    "selfConsumedRate1",
    "selfConsumedRate2",
    "selfConsumedEnergy1",
    "selfConsumedEnergy2",
    "plantTreeNum",
    "reduceCo2",
]

SAJ_SENSORS = [
    *BASIC_SENSORS,
    "totalPvEnergy",
    "totalLoadEnergy",  # Energy -> Grid consumption
    "totalBuyEnergy",
    "totalSellEnergy",  # Energy -> Return to grid
    "gridLoadPower",  # Power imported from the grid
    "solarLoadPower",  # Solar power being currently self-consumed
    "homeLoadPower",  # Total power being consumed by the plant (the home)
    "exportPower",  # Power being exported to the grid
]

H1_SENSORS = [
    *BASIC_SENSORS,
    "totalBuyElec",  # Energy -> Grid consumption
    "totalConsumpElec",
    "totalSellElec",  # Energy -> Return to grid
    "chargeElec",  # Energy -> Home Battery Storage -> Energy going in to the battery (kWh)
    "dischargeElec",  # Energy -> Home Battery Storage -> Energy coming out of the battery (kWh)
    "isStorageAlarm",
    "batCapcity",
    "batCurr",
    "batEnergyPercent",
    "batteryDirection",
    "batteryPower",
    "gridDirection",
    "gridPower",
    "h1Online",
    "outPower",
    "outPutDirection",
    "pvDirection",
    "pvPower",
    "solarPower",
]
# all sensors supported and their description for hass
SENSOR_TYPES: Final[tuple[SensorEntityDescription, ...]] = (
    SensorEntityDescription(
        key="nowPower",
        name="nowPower",
        icon="mdi:solar-power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        key="runningState",
        name="runningState",
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="devOnlineNum",
        name="devOnlineNum",
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="todayElectricity",
        name="todayElectricity",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    SensorEntityDescription(
        key="monthElectricity",
        name="monthElectricity",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    SensorEntityDescription(
        key="yearElectricity",
        name="yearElectricity",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    SensorEntityDescription(
        key="totalElectricity",
        name="totalElectricity",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="selfUseRate",
        name="selfUseRate",
        icon="mdi:solar-panel",
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="totalBuyElec",
        name="totalBuyElec",
        icon="mdi:solar-panel",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="totalConsumpElec",
        name="totalConsumpElec",
        icon="mdi:solar-panel",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    SensorEntityDescription(
        key="totalSellElec",
        name="totalSellElec",
        icon="mdi:solar-panel",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="todayGridIncome",
        name="todayGridIncome",
        icon="mdi:currency-eur",
    ),
    SensorEntityDescription(
        key="income",
        name="income",
        icon="mdi:currency-eur",
    ),
    SensorEntityDescription(
        key="lastUploadTime",
        name="lastUploadTime",
        icon="mdi:timer-sand",
    ),
    SensorEntityDescription(
        key="totalPlantTreeNum",
        name="totalPlantTreeNum",
        icon="mdi:tree",
    ),
    SensorEntityDescription(
        key="totalReduceCo2",
        name="totalReduceCo2",
        icon="mdi:molecule-co2",
    ),
    SensorEntityDescription(
        key="plantuid",
        name="plantuid",
        icon="mdi:api",
    ),
    SensorEntityDescription(
        key="plantname",
        name="plantname",
        icon="mdi:api",
    ),
    SensorEntityDescription(
        key="currency",
        name="currency",
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="address",
        name="address",
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="isOnline",
        name="isOnline",
        icon="mdi:api",
    ),
    SensorEntityDescription(
        key="status",
        name="status",
        icon="mdi:api",
    ),
    SensorEntityDescription(
        key="peakPower",
        name="peakPower",
        icon="mdi:solar-panel",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        key="systemPower",
        name="systemPower",
        icon="mdi:solar-panel",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        key="pvElec",
        name="pvElec",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    SensorEntityDescription(
        key="useElec",
        name="useElec",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="buyElec",
        name="buyElec",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="sellElec",
        name="sellElec",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="buyRate",
        name="buyRate",
        icon="mdi:solar-panel",
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="sellRate",
        name="sellRate",
        icon="mdi:solar-panel",
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="selfConsumedRate1",
        name="selfConsumedRate1",
        icon="mdi:solar-panel",
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="selfConsumedRate2",
        name="selfConsumedRate2",
        icon="mdi:solar-panel",
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="selfConsumedEnergy1",
        name="selfConsumedEnergy1",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    SensorEntityDescription(
        key="selfConsumedEnergy2",
        name="selfConsumedEnergy2",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    SensorEntityDescription(
        key="plantTreeNum",
        name="plantTreeNum",
        icon="mdi:tree",
    ),
    SensorEntityDescription(
        key="reduceCo2",
        name="reduceCo2",
        icon="mdi:molecule-co2",
    ),
    SensorEntityDescription(
        key="gridLoadPower",
        name="gridLoadPower",
        icon="mdi:transmission-tower-import",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        key="solarLoadPower",
        name="solarLoadPower",
        icon="mdi:solar-power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        key="homeLoadPower",
        name="homeLoadPower",
        icon="mdi:home-lightning-bolt-outline",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        key="exportPower",
        name="exportPower",
        icon="mdi:transmission-tower-export",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        key="totalPvEnergy",
        name="totalPvEnergy",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="totalLoadEnergy",
        name="totalLoadEnergy",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="totalBuyEnergy",
        name="totalBuyEnergy",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="totalSellEnergy",
        name="totalSellEnergy",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    # h1
    SensorEntityDescription(
        key="batCapcity",
        name="batCapcity",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement="A⋅h",
    ),
    SensorEntityDescription(
        key="isStorageAlarm",
        name="isStorageAlarm",
        icon="mdi:alarm",
    ),
    SensorEntityDescription(
        key="batCurr",
        name="batCurr",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement="A⋅h",
    ),
    SensorEntityDescription(
        key="batEnergyPercent",
        name="batEnergyPercent",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="batteryDirection",
        name="batteryDirection",
        icon="mdi:solar-panel-large",
    ),
    SensorEntityDescription(
        key="batteryPower",
        name="batteryPower",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        key="gridPower",
        name="gridPower",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        key="gridDirection", name="gridDirection", icon="mdi:solar-panel-large"
    ),
    SensorEntityDescription(
        key="h1Online",
        name="h1Online",
        icon="mdi:solar-panel-large",
    ),
    SensorEntityDescription(
        key="outPower",
        name="outPower",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        key="outPutDirection",
        name="outPutDirection",
        icon="mdi:solar-panel-large",
    ),
    SensorEntityDescription(
        key="pvPower",
        name="pvPower",
        icon="mdi:solar-panel-large",
    ),
    SensorEntityDescription(
        key="solarPower",
        name="solarPower",
        icon="mdi:solar-panel-large",
    ),
    SensorEntityDescription(
        key="chargeElec",
        name="chargeElec",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="dischargeElec",
        name="dischargeElec",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
)
