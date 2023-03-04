"""
Alternative for the SAJ local API sensor. Unfortunally there is no public api.
This Sensor will read the private api of the eSolar portal at https://fop.saj-electric.com/
"""

import asyncio
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from datetime import timedelta
import datetime
import calendar

from functools import reduce
import logging
from typing import Final

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import (
    CONF_RESOURCES,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SENSORS,
    CONF_DEVICE_ID,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
    POWER_KILO_WATT,
    PERCENTAGE,

)
CONF_PLANT_ID: Final = "plant_id"
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle, dt

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)

def add_years(d, years):
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))

BASE_URL = 'https://fop.saj-electric.com/saj/login'
_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)

SENSOR_PREFIX = 'esolar '
ATTR_MEASUREMENT = "measurement"
ATTR_SECTION = "section"

SENSOR_LIST = {
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
    "isAlarm",
    "plantuid",
    "plantname",
    "currency",
    "address",
    "isOnline",
    "status",
    "peakPower",
    "systemPower",
    #sec & h1
    "pvElec",
    "useElec",
    "buyElec",
    "sellElec",
    "buyRate",
    "sellRate",
    "selfUseRate",
    "totalBuyElec",
    "totalConsumpElec",
    "totalSellElec",
    "selfConsumedRate1",
    "selfConsumedRate2",
    "selfConsumedEnergy1",
    "selfConsumedEnergy2",
    "plantTreeNum",
    "reduceCo2",
    "totalGridPower",
    "totalLoadPower",
    "totalPvgenPower",
    "totalPvEnergy",
    "totalLoadEnergy",
    "totalBuyEnergy",
    "totalSellEnergy",
    #h1
    "chargeElec",
    "dischargeElec",
    "batCapcity",
    "isStorageAlarm",
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
}

SENSOR_TYPES: Final[tuple[SensorEntityDescription]] = (
    SensorEntityDescription(
        key="nowPower",
        name="nowPower",
        icon="mdi:solar-power",
        native_unit_of_measurement=POWER_WATT,
        device_class=DEVICE_CLASS_POWER,
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
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
    ),
    SensorEntityDescription(
        key="monthElectricity",
        name="monthElectricity",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
    ),
    SensorEntityDescription(
        key="yearElectricity",
        name="yearElectricity",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
    ),
    SensorEntityDescription(
        key="totalElectricity",
        name="totalElectricity",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="selfUseRate",
        name="selfUseRate",
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="totalBuyElec",
        name="totalBuyElec",
        icon="mdi:solar-panel",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="totalConsumpElec",
        name="totalConsumpElec",
        icon="mdi:solar-panel",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
    ),
    SensorEntityDescription(
        key="totalSellElec",
        name="totalSellElec",
        icon="mdi:solar-panel",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
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
        key="isAlarm",
        name="isAlarm",
        icon="mdi:alarm",
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
        native_unit_of_measurement=POWER_WATT,
        device_class=DEVICE_CLASS_POWER,
    ),
    SensorEntityDescription(
        key="systemPower",
        name="systemPower",
        icon="mdi:solar-panel",
        native_unit_of_measurement=POWER_KILO_WATT,
        device_class=DEVICE_CLASS_POWER,
    ),    
    SensorEntityDescription(
        key="pvElec",
        name="pvElec",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
    ),
    SensorEntityDescription(
        key="useElec",
        name="useElec",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="buyElec",
        name="buyElec",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="sellElec",
        name="sellElec",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="buyRate",
        name="buyRate",
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="sellRate",
        name="sellRate",
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="selfConsumedRate1",
        name="selfConsumedRate1",
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="selfConsumedRate2",
        name="selfConsumedRate2",
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="selfConsumedEnergy1",
        name="selfConsumedEnergy1",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
    ),
    SensorEntityDescription(
        key="selfConsumedEnergy2",
        name="selfConsumedEnergy2",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
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
        key="totalGridPower",
        name="totalGridPower",
        icon="mdi:solar-panel",
        native_unit_of_measurement=POWER_WATT,
    ),
    SensorEntityDescription(
        key="totalLoadPower",
        name="totalLoadPower",
        icon="mdi:solar-panel",
        native_unit_of_measurement=POWER_WATT,
        device_class=DEVICE_CLASS_POWER,
    ),
    SensorEntityDescription(
        key="totalPvgenPower",
        name="totalPvgenPower",
        icon="mdi:solar-panel",
        native_unit_of_measurement=POWER_WATT,
    ),
    SensorEntityDescription(
        key="totalPvEnergy",
        name="totalPvEnergy",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="totalLoadEnergy",
        name="totalLoadEnergy",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="totalBuyEnergy",
        name="totalBuyEnergy",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="totalSellEnergy",
        name="totalSellEnergy",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    #h1
    SensorEntityDescription(
        key="batCapcity",
        name="batCapcity",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement="A⋅h"
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
        native_unit_of_measurement=POWER_WATT,
    ),
    SensorEntityDescription(
        key="gridPower",
        name="gridPower",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=POWER_WATT,
    ),
    SensorEntityDescription(
        key="gridDirection",
        name="gridDirection",
        icon="mdi:solar-panel-large"
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
        native_unit_of_measurement=POWER_WATT,
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
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="dischargeElec",
        name="dischargeElec",
        icon="mdi:solar-panel-large",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_RESOURCES, default=list(SENSOR_LIST)): vol.All(
            cv.ensure_list, [vol.In(SENSOR_LIST)]
        ),
        vol.Optional(CONF_SENSORS, default="None"): cv.string,
        vol.Optional(CONF_PLANT_ID, default=0): cv.positive_int,

    }
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):

    """Setup the SAJ eSolar sensors."""

    session = async_create_clientsession(hass)
    data = SAJeSolarMeterData(session, config.get(CONF_USERNAME), config.get(CONF_PASSWORD), config.get(CONF_SENSORS), config.get(CONF_PLANT_ID))
    await data.async_update()

    entities = []
    for description in SENSOR_TYPES:
        if description.key in config[CONF_RESOURCES]:
            sensor = SAJeSolarMeterSensor(description, data, config.get(CONF_SENSORS), config.get(CONF_PLANT_ID))
            entities.append(sensor)
    async_add_entities(entities, True)
    return True

class SAJeSolarMeterData(object):
    """Handle eSolar object and limit updates."""

    def __init__(self, session, username, password, sensors, plant_id):
        """Initialize the data object."""

        self._session = session
        self._url = BASE_URL
        self.username = username
        self.password = password
        self.sensors = sensors
        self.plant_id = plant_id
        self._data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Download and update data from SAJeSolar."""

        try:

            today = datetime.date.today()
            clientDate = today.strftime('%Y-%m-%d')

            # Login to eSolar API
            url = 'https://fop.saj-electric.com/saj/login'
            payload = {
                'lang': 'en',
                'username': self.username,
                'password': self.password,
                'rememberMe': 'true'
            }
            headers_login = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': 'org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=en; op_esolar_lang=en',
                'DNT': '1',
                'Host': 'fop.saj-electric.com',
                'Origin': 'https://fop.saj-electric.com',
                'Referer': 'https://fop.saj-electric.com/saj/login',
                'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
                'sec-ch-ua-mobile': '?0',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent'
                : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
            }
            response = await self._session.post(url, headers=headers_login, data=payload)

            if response.status != 200:
                _LOGGER.error(f"{response.url} returned {response.status}")
                return


            # Get API Plant info from Esolar Portal
            url2 = 'https://fop.saj-electric.com/saj/monitor/site/getUserPlantList'
            headers = {
                'Connection': 'keep-alive',
                'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'DNT': '1',
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua-mobile': '?0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://fop.saj-electric.com',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': 'https://fop.saj-electric.com/saj/monitor/home/index',
                'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7'
            }

            payload2= f"pageNo=&pageSize=&orderByIndex=&officeId=&clientDate={clientDate}&runningState=&selectInputType=1&plantName=&deviceSn=&type=&countryCode=&isRename=&isTimeError=&systemPowerLeast=&systemPowerMost="
            response2 = await self._session.post(url2, headers=headers, data=payload2)

            if response2.status != 200:
                _LOGGER.error(f"{response2.url} returned {response2.status}")
                return

            plantInfo = await response2.json()
            plantuid = plantInfo['plantList'][self.plant_id]['plantuid']


            # Get API Plant Solar Details
            url3 = "https://fop.saj-electric.com/saj/monitor/site/getPlantDetailInfo"
            payload3= f"plantuid={plantuid}&clientDate={clientDate}"

            response3 = await self._session.post(url3, headers=headers, data=payload3)

            if response3.status != 200:
                _LOGGER.error(f"{response3.url} returned {response3.status}")
                return

            plantDetails = await response3.json()
            #_LOGGER.error(f"PlantDetails: {plantDetails}")
            plantDetails.update(plantInfo)


            # getPlantDetailChart2
            plantuid = plantDetails['plantList'][self.plant_id]['plantuid']

            deviceSnArr = plantDetails['plantDetail']['snList'][0]
            previousChartDay = today - timedelta(days=1)
            nextChartDay = today + timedelta(days = 1)
            chartDay = today.strftime('%Y-%m-%d')
            previousChartMonth = add_months(today,-1).strftime('%Y-%m')
            nextChartMonth = add_months(today, 1).strftime('%Y-%m')
            chartMonth = today.strftime('%Y-%m')
            previousChartYear = add_years(today, -1).strftime('%Y')
            nextChartYear = add_years(today, 1).strftime('%Y')
            chartYear = today.strftime('%Y')
            epochmilliseconds = round(int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000))

            url4 = f"https://fop.saj-electric.com/saj/monitor/site/getPlantDetailChart2?plantuid={plantuid}&chartDateType=1&energyType=0&clientDate={clientDate}&deviceSnArr={deviceSnArr}&chartCountType=2&previousChartDay={previousChartDay}&nextChartDay={nextChartDay}&chartDay={chartDay}&previousChartMonth={previousChartMonth}&nextChartMonth={nextChartMonth}&chartMonth={chartMonth}&previousChartYear={previousChartYear}&nextChartYear={nextChartYear}&chartYear={chartYear}&chartEnergyType=0&elecDevicesn={deviceSnArr}&_={epochmilliseconds}"
            #_LOGGER.error(f"PlantCharts URL: {url4}")
            response4 = await self._session.post(url4, headers=headers)

            if response4.status != 200:
                _LOGGER.error(f"{response4.url} returned {response4.status}")
                return

            plantcharts = await response4.json()
            #_LOGGER.error(f"PlantCharts: {plantcharts}")
            plantDetails.update(plantcharts)


            # H1 Module
            if self.sensors == "h1":
                # getStoreOrAcDevicePowerInfo
                url_getStoreOrAcDevicePowerInfo = f"https://fop.saj-electric.com/saj/monitor/site/getStoreOrAcDevicePowerInfo?plantuid=&devicesn={deviceSnArr}&_={epochmilliseconds}"

                response_getStoreOrAcDevicePowerInfo = await self._session.post(url_getStoreOrAcDevicePowerInfo, headers=headers)

                if response_getStoreOrAcDevicePowerInfo.status != 200:
                    _LOGGER.error(f"{response_getStoreOrAcDevicePowerInfo.url} returned {response_getStoreOrAcDevicePowerInfo.status}")
                    return

                result_getStoreOrAcDevicePowerInfo = await response_getStoreOrAcDevicePowerInfo.json()
                #_LOGGER.error(f"{result_getStoreOrAcDevicePowerInfo}")
                plantDetails.update(result_getStoreOrAcDevicePowerInfo)
                _LOGGER.debug(result_getStoreOrAcDevicePowerInfo)

            elif self.sensors == "None":
                self._data = plantDetails
            else:
                # Data = plantdetails
                self._data = plantDetails



            # Sec module
            if self.sensors == "saj_sec":

                # getPlantMeterModuleList
                url_module = "https://fop.saj-electric.com/saj/cloudmonitor/plantMeterModule/getPlantMeterModuleList"

                payload_module = f"pageNo=&pageSize=&plantUid={plantuid}"

                response_module = await self._session.post(url_module, headers=headers, data=payload_module)

                if response_module.status != 200:
                    _LOGGER.error(f"{response_module.url} returned {response_module.status}")
                    return

                getPlantMeterModuleList = await response_module.json()

                temp_getPlantMeterModuleList = dict()
                temp_getPlantMeterModuleList["getPlantMeterModuleList"] = getPlantMeterModuleList

                plantDetails.update(temp_getPlantMeterModuleList)

                moduleSn = plantDetails["getPlantMeterModuleList"]['moduleList'][0]['moduleSn']

                # -Debug- Sec module serial number
                _LOGGER.debug(moduleSn)


                # findDevicePageList
                url_findDevicePageList = "https://fop.saj-electric.com/saj/cloudMonitor/device/findDevicePageList"

                payload_findDevicePageList = f"officeId=1&pageNo=&pageSize=&orderName=1&orderType=2&plantuid={plantuid}&deviceStatus=&localDate={chartMonth}&localMonth={chartMonth}"

                response_findDevicePageList = await self._session.post(url_findDevicePageList, headers=headers, data=payload_findDevicePageList)

                if response_findDevicePageList.status != 200:
                    _LOGGER.error(f"{response_findDevicePageList.url} returned {response_findDevicePageList.status}")
                    return

                findDevicePageList = await response_findDevicePageList.json()

                temp_findDevicePageList = dict()
                temp_findDevicePageList["findDevicePageList"] = findDevicePageList

                plantDetails.update(temp_findDevicePageList)

                # getPlantMeterDetailInfo
                url_getPlantMeterDetailInfo = "https://fop.saj-electric.com/saj/monitor/site/getPlantMeterDetailInfo"

                payload_getPlantMeterDetailInfo = f"plantuid={plantuid}&clientDate={clientDate}"

                response_getPlantMeterDetailInfo = await self._session.post(url_getPlantMeterDetailInfo, headers=headers, data=payload_getPlantMeterDetailInfo)

                if response_getPlantMeterDetailInfo.status != 200:
                    _LOGGER.error(f"{response_getPlantMeterDetailInfo.url} returned {response_getPlantMeterDetailInfo.status}")
                    return

                getPlantMeterDetailInfo = await response_getPlantMeterDetailInfo.json()

                temp_getPlantMeterDetailInfo = dict()
                temp_getPlantMeterDetailInfo["getPlantMeterDetailInfo"] = getPlantMeterDetailInfo

                plantDetails.update(temp_getPlantMeterDetailInfo)

                # getPlantMeterEnergyPreviewInfo
                url_getPlantMeterEnergyPreviewInfo = f"https://fop.saj-electric.com/saj/monitor/site/getPlantMeterEnergyPreviewInfo?plantuid={plantuid}&moduleSn={moduleSn}&_={epochmilliseconds}"

                response_getPlantMeterEnergyPreviewInfo = await self._session.get(url_getPlantMeterEnergyPreviewInfo, headers=headers)

                if response_getPlantMeterEnergyPreviewInfo.status != 200:
                    _LOGGER.error(f"{response_getPlantMeterEnergyPreviewInfo.url} returned {response_getPlantMeterEnergyPreviewInfo.status}")
                    return

                getPlantMeterEnergyPreviewInfo = await response_getPlantMeterEnergyPreviewInfo.json()

                temp_getPlantMeterEnergyPreviewInfo = dict()
                temp_getPlantMeterEnergyPreviewInfo["getPlantMeterEnergyPreviewInfo"] = getPlantMeterEnergyPreviewInfo

                plantDetails.update(temp_getPlantMeterEnergyPreviewInfo)

                # Get Sec Meter details
                url_getPlantMeterChartData = f"https://fop.saj-electric.com/saj/monitor/site/getPlantMeterChartData?plantuid={plantuid}&chartDateType=1&energyType=0&clientDate={clientDate}&deviceSnArr=&chartCountType=2&previousChartDay={previousChartDay}&nextChartDay={nextChartDay}&chartDay={chartDay}&previousChartMonth={previousChartMonth}&nextChartMonth={nextChartMonth}&chartMonth={chartMonth}&previousChartYear={previousChartYear}&nextChartYear={nextChartYear}&chartYear={chartYear}&moduleSn={moduleSn}&_={epochmilliseconds}"

                response_getPlantMeterChartData = await self._session.post(url_getPlantMeterChartData, headers=headers)

                if response_getPlantMeterChartData.status != 200:
                    _LOGGER.error(f"{response_getPlantMeterChartData.url} returned {response_getPlantMeterChartData.status}")
                    return

                getPlantMeterChartData = await response_getPlantMeterChartData.json()

                temp_getPlantMeterChartData = dict()
                temp_getPlantMeterChartData["getPlantMeterChartData"] = getPlantMeterChartData

                plantDetails.update(temp_getPlantMeterChartData)

                # Data = plantdetails including Sec module
                self._data = plantDetails
            elif self.sensors == "None":
                self._data = plantDetails
            else:
                # Data = plantdetails Wtihout Sec module
                self._data = plantDetails

        # Error logging
        except aiohttp.ClientError:
            _LOGGER.error("Cannot poll eSolar using url: %s")
            return
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout error occurred while polling eSolar using url: %s")
            return
        except Exception as err:
            _LOGGER.error("Unknown error occurred while polling eSolar: %s", err)
            self._data = None
            return


        # -Debug- Cookies and Data
        _LOGGER.debug(self._session.cookie_jar.filter_cookies("https://fop.saj-electric.com"))
        _LOGGER.debug(self._data)


        # logout session
        url_logout = "https://fop.saj-electric.com/saj/logout"
        response_logout = await self._session.post(url_logout, headers=headers)

        if response_logout.status != 200:
            _LOGGER.error(f"{response_logout.url} returned {response_logout.status}")
            return


        # Clear session and cookies
        self._session.cookie_jar.clear()
        self._session.close()

    @property
    def latest_data(self):
        """Return the latest data object."""
        if self._data:
            return self._data

        _LOGGER.error("return data NONE")
        return None

class SAJeSolarMeterSensor(SensorEntity):
    """Collecting data and return sensor entity."""

    def __init__(self, description: SensorEntityDescription, data, sensors, plant_id):
        """Initialize the sensor."""
        self.entity_description = description
        self._data = data

        self._state = None
        self.sensors = sensors
        self.plant_id = plant_id
        self._type = self.entity_description.key
        self._attr_icon = self.entity_description.icon
        self._attr_name = SENSOR_PREFIX + self.entity_description.name
        self._attr_state_class = self.entity_description.state_class
        self._attr_native_unit_of_measurement = self.entity_description.native_unit_of_measurement
        self._attr_device_class = self.entity_description.device_class
        self._attr_unique_id = f"{SENSOR_PREFIX}_{self._type}"

        self._discovery = False
        self._dev_id = {}

    @property
    def state(self):
        """Return the state of the sensor. (total/current power consumption/production or total gas used)"""
        return self._state

    async def async_update(self):
        """Get the latest data and use it to update our sensor state."""

        await self._data.async_update()
        energy = self._data.latest_data

        if energy:
            if self._type == 'devOnlineNum':
                if 'devOnlineNum' in energy['plantDetail']:
                    if energy['plantDetail']["devOnlineNum"] is not None:
                        if int(energy['plantDetail']["devOnlineNum"]) is 0:
                            self._state = "No"
                        else:
                            self._state = "Yes"
            if self._type == 'nowPower':
                if 'nowPower' in energy['plantDetail']:
                    if energy['plantDetail']["nowPower"] is not None:
                        self._state = float(energy['plantDetail']["nowPower"])
            if self._type == 'runningState':
                if 'runningState' in energy['plantDetail']:
                    if energy['plantDetail']["runningState"] is not None:
                        if int(energy['plantDetail']["runningState"]) is 0:
                            self._state = "No"
                        else:
                            self._state = "Yes"
            if self._type == 'todayElectricity':
                if 'todayElectricity' in energy['plantDetail']:
                    if energy['plantDetail']["todayElectricity"] is not None:
                        self._state = float(energy['plantDetail']["todayElectricity"])
            if self._type == 'monthElectricity':
                if 'monthElectricity' in energy['plantDetail']:
                    if energy['plantDetail']["monthElectricity"] is not None:
                        self._state = float(energy['plantDetail']["monthElectricity"])
            if self._type == 'yearElectricity':
                if 'yearElectricity' in energy['plantDetail']:
                    if energy['plantDetail']["yearElectricity"] is not None:
                        self._state = float(energy['plantDetail']["yearElectricity"])
            if self._type == 'totalElectricity':
                if 'totalElectricity' in energy['plantDetail']:
                    if energy['plantDetail']["totalElectricity"] is not None:
                        self._state = float(energy['plantDetail']["totalElectricity"])
            if self._type == 'todayGridIncome':
                if 'todayGridIncome' in energy['plantDetail']:
                    if energy['plantDetail']["todayGridIncome"] is not None:
                        self._state = float(energy['plantDetail']["todayGridIncome"])
            if self._type == 'income':
                if 'income' in energy['plantDetail']:
                    if energy['plantDetail']["income"] is not None:
                        self._state = float(energy['plantDetail']["income"])
            if self._type == 'selfUseRate':
                if 'selfUseRate' in energy['plantDetail']:
                    if energy['plantDetail']["selfUseRate"] is not None:
                        self._state = energy['plantDetail']["selfUseRate"]
            if self._type == 'totalBuyElec':
                if 'totalBuyElec' in energy['plantDetail']:
                    if energy['plantDetail']["totalBuyElec"] is not None:
                        self._state = float(energy['plantDetail']["totalBuyElec"])
            if self._type == 'totalConsumpElec':
                if 'totalConsumpElec' in energy['plantDetail']:
                    if energy['plantDetail']["totalConsumpElec"] is not None:
                        self._state = float(energy['plantDetail']["totalConsumpElec"])
            if self._type == 'totalSellElec':
                if 'totalSellElec' in energy['plantDetail']:
                    if energy['plantDetail']["totalSellElec"] is not None:
                        self._state = float(energy['plantDetail']["totalSellElec"])

            if self._type == 'isAlarm':
                if 'isAlarm' in energy['plantDetail']:
                    if energy['plantDetail']["isAlarm"] is not None:
                        self._state = (energy['plantDetail']["isAlarm"])
            if self._type == 'lastUploadTime':
                if 'lastUploadTime' in energy['plantDetail']:
                    if energy['plantDetail']["lastUploadTime"] is not None:
                        self._state = (energy['plantDetail']["lastUploadTime"])
            if self._type == 'totalPlantTreeNum':
                if 'totalPlantTreeNum' in energy['plantDetail']:
                    if energy['plantDetail']["totalPlantTreeNum"] is not None:
                        self._state = (energy['plantDetail']["totalPlantTreeNum"])
            if self._type == 'totalReduceCo2':
                if 'totalReduceCo2' in energy['plantDetail']:
                    if energy['plantDetail']["totalReduceCo2"] is not None:
                        self._state = (energy['plantDetail']["totalReduceCo2"])

            if self._type == 'currency':
                if 'currency' in energy['plantList'][self.plant_id]:
                    if energy['plantList'][self.plant_id]["currency"] is not None:
                        self._state = (energy['plantList'][self.plant_id]["currency"])
            if self._type == 'plantuid':
                if 'plantuid' in energy['plantList'][self.plant_id]:
                    if energy['plantList'][self.plant_id]["plantuid"] is not None:
                        self._state = (energy['plantList'][self.plant_id]["plantuid"])
            if self._type == 'plantname':
                if 'plantname' in energy['plantList'][self.plant_id]:
                    if energy['plantList'][self.plant_id]["plantname"] is not None:
                        self._state = (energy['plantList'][self.plant_id]["plantname"])
            if self._type == 'currency':
                if 'currency' in energy['plantList'][self.plant_id]:
                    if energy['plantList'][self.plant_id]["currency"] is not None:
                        self._state = (energy['plantList'][self.plant_id]["currency"])
            if self._type == 'isOnline':
                if 'isOnline' in energy['plantList'][self.plant_id]:
                    if energy['plantList'][self.plant_id]["isOnline"] is not None:
                        self._state = (energy['plantList'][self.plant_id]["isOnline"])
            if self._type == 'address':
                if 'address' in energy['plantList'][self.plant_id]:
                    if energy['plantList'][self.plant_id]["address"] is not None:
                        self._state = (energy['plantList'][self.plant_id]["address"])
            if self._type == 'systemPower':
                if 'systempower' in energy['plantList'][self.plant_id]:
                    if energy['plantList'][self.plant_id]["systempower"] is not None:
                        self._state = (energy['plantList'][self.plant_id]["systempower"])

            if self._type == 'peakPower':
                if 'peakPower' in energy:
                    if energy["peakPower"] is not None:
                        self._state = float(energy["peakPower"])
            if self._type == 'status':
                if 'status' in energy:
                    if energy["status"] is not None:
                        self._state = (energy["status"])

            ########################################################################## SAJ h1
            if self.sensors == "h1":
                if self._type == 'chargeElec':
                    if 'chargeElec' in energy['viewBean']:
                        if energy['viewBean']["chargeElec"] is not None:
                            self._state = float(energy['viewBean']["chargeElec"])
                if self._type == 'dischargeElec':
                    if 'dischargeElec' in energy['viewBean']:
                        if energy['viewBean']["dischargeElec"] is not None:
                            self._state = float(energy['viewBean']["dischargeElec"])
                if self._type == 'buyElec':
                    if 'pvElec' in energy['viewBean']:
                        if energy['viewBean']["buyElec"] is not None:
                            self._state = float(energy['viewBean']["buyElec"])
                if self._type == 'buyRate':
                    if 'buyRate' in energy['viewBean']:
                        if energy['viewBean']["buyRate"] is not None:
                            self._state = energy['viewBean']["buyRate"]
                if self._type == 'pvElec':
                    if 'pvElec' in energy['viewBean']:
                        if energy['viewBean']["pvElec"] is not None:
                            self._state = float(energy['viewBean']["pvElec"])
                if self._type == 'selfConsumedEnergy1':
                    if 'selfConsumedEnergy1' in energy['viewBean']:
                        if energy['viewBean']["selfConsumedEnergy1"] is not None:
                            self._state = float(energy['viewBean']["selfConsumedEnergy1"])
                if self._type == 'selfConsumedEnergy2':
                    if 'selfConsumedEnergy2' in energy['viewBean']:
                        if energy['viewBean']["selfConsumedEnergy2"] is not None:
                            self._state = float(energy['viewBean']["selfConsumedEnergy2"])
                if self._type == 'selfConsumedRate1':
                    if 'selfConsumedRate1' in energy['viewBean']:
                        if energy['viewBean']["selfConsumedRate1"] is not None:
                            self._state = energy['viewBean']["selfConsumedRate1"]
                if self._type == 'selfConsumedRate2':
                    if 'selfConsumedRate2' in energy['viewBean']:
                        if energy['viewBean']["selfConsumedRate2"] is not None:
                            self._state = energy['viewBean']["selfConsumedRate2"]
                if self._type == 'sellElec':
                    if 'sellElec' in energy['viewBean']:
                        if energy['viewBean']["sellElec"] is not None:
                            self._state = float(energy['viewBean']["sellElec"])
                if self._type == 'sellRate':
                    if 'sellRate' in energy['viewBean']:
                        if energy['viewBean']["sellRate"] is not None:
                            self._state = energy['viewBean']["sellRate"]
                if self._type == 'useElec':
                    if 'useElec' in energy['viewBean']:
                        if energy['viewBean']["useElec"] is not None:
                            self._state = float(energy['viewBean']["useElec"])
                # storeDevicePower
                if self._type == 'batCapcity':
                    if 'batCapcity' in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]['batCapcity'] is not None:
                            self._state = float(energy["storeDevicePower"]["batCapcity"])
                if self._type == 'isStorageAlarm':
                    if 'isStorageAlarm' in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]['isStorageAlarm'] is not None:
                            self._state = int(energy["storeDevicePower"]["isStorageAlarm"])
                if self._type == 'batCurr':
                    if 'batCurr' in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]['batCurr'] is not None:
                            self._state = float(energy["storeDevicePower"]["batCurr"])
                if self._type == 'batEnergyPercent':
                    if 'batEnergyPercent' in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]['batEnergyPercent'] is not None:
                            self._state = float(energy["storeDevicePower"]["batEnergyPercent"])
                if self._type == 'batteryDirection':
                    if 'batteryDirection' in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]['batteryDirection'] is not None:
                            if energy["storeDevicePower"]["batteryDirection"] == 0:
                                self._state = "Standby"
                            elif energy["storeDevicePower"]["batteryDirection"] == 1:
                                self._state = "Discharging"
                            elif energy["storeDevicePower"]["batteryDirection"] == -1:
                                self._state = "Charging"
                            else:
                                self._state = f'Unknown: {energy["storeDevicePower"]["batteryDirection"]}'
                if self._type == 'batteryPower':
                    if 'batteryPower' in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]['batteryPower'] is not None:
                            self._state = float(energy["storeDevicePower"]["batteryPower"])
                if self._type == 'gridDirection':
                    if 'gridDirection' in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]['gridDirection'] is not None:
                            if energy["storeDevicePower"]["gridDirection"] == 1:
                                self._state = "Exporting"
                            elif energy["storeDevicePower"]["gridDirection"] == -1:
                                self._state = "Importing"
                            else:
                                self._state = energy["storeDevicePower"]["gridDirection"]
                                _LOGGER.error(f"Grid Direction unknown value: {self._state}")
                if self._type == 'gridPower':
                    if 'gridPower' in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]['gridPower'] is not None:
                            self._state = float(energy["storeDevicePower"]["gridPower"])
                if self._type == 'h1Online':
                    if 'isOnline' in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]['isOnline'] is not None:
                            if int(energy['storeDevicePower']["isOnline"]) is 0:
                                self._state = "No"
                            else:
                                self._state = "Yes"
                if self._type == 'outPower':
                    if 'outPower' in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]['outPower'] is not None:
                            self._state = float(energy["storeDevicePower"]["outPower"])
                if self._type == 'outPutDirection':
                    if 'outPutDirection' in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]['outPutDirection'] is not None:
                            self._state = float(energy["storeDevicePower"]["outPutDirection"])
                if self._type == 'pvDirection':
                    if 'pvDirection' in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]['pvDirection'] is not None:
                            self._state = int(energy["storeDevicePower"]["pvDirection"])
                if self._type == 'pvPower':
                    if 'pvPower' in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]['pvPower'] is not None:
                            self._state = float(energy["storeDevicePower"]["pvPower"])
                if self._type == 'solarPower':
                    if 'solarPower' in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]['solarPower'] is not None:
                            self._state = float(energy["storeDevicePower"]["solarPower"])
                if self._type == 'totalLoadPower':
                    if 'totalLoadPower' in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]['totalLoadPower'] is not None:
                            self._state = float(energy["storeDevicePower"]['totalLoadPower'])

            ########################################################################## Sec module Sensors:
            if self.sensors == "saj_sec":
                # getPlantMeterChartData - viewBeam
                if self._type == 'pvElec':
                    if 'pvElec' in energy["getPlantMeterChartData"]['viewBean']:
                        if energy["getPlantMeterChartData"]['viewBean']["pvElec"] is not None:
                            self._state = float(energy["getPlantMeterChartData"]['viewBean']["pvElec"])
                if self._type == 'useElec':
                    if 'useElec' in energy["getPlantMeterChartData"]['viewBean']:
                        if energy["getPlantMeterChartData"]['viewBean']["useElec"] is not None:
                            self._state = float(energy["getPlantMeterChartData"]['viewBean']["useElec"])
                if self._type == 'buyElec':
                    if 'buyElec' in energy["getPlantMeterChartData"]['viewBean']:
                        if energy["getPlantMeterChartData"]['viewBean']["buyElec"] is not None:
                            self._state = float(energy["getPlantMeterChartData"]['viewBean']["buyElec"])
                if self._type == 'sellElec':
                    if 'sellElec' in energy["getPlantMeterChartData"]['viewBean']:
                        if energy["getPlantMeterChartData"]['viewBean']["sellElec"] is not None:
                            self._state = float(energy["getPlantMeterChartData"]['viewBean']["sellElec"])
                if self._type == 'selfConsumedEnergy1':
                    if 'selfConsumedEnergy1' in energy["getPlantMeterChartData"]['viewBean']:
                        if energy["getPlantMeterChartData"]['viewBean']["selfConsumedEnergy1"] is not None:
                            self._state = float(energy["getPlantMeterChartData"]['viewBean']["selfConsumedEnergy1"])
                if self._type == 'selfConsumedEnergy2':
                    if 'selfConsumedEnergy2' in energy["getPlantMeterChartData"]['viewBean']:
                        if energy["getPlantMeterChartData"]['viewBean']["selfConsumedEnergy2"] is not None:
                            self._state = float(energy["getPlantMeterChartData"]['viewBean']["selfConsumedEnergy2"])
                if self._type == 'reduceCo2':
                    if 'reduceCo2' in energy["getPlantMeterChartData"]['viewBean']:
                        if energy["getPlantMeterChartData"]['viewBean']["reduceCo2"] is not None:
                            self._state = float(energy["getPlantMeterChartData"]['viewBean']["reduceCo2"])


                if self._type == 'buyRate':
                    if 'buyRate' in energy["getPlantMeterChartData"]['viewBean']:
                        if energy["getPlantMeterChartData"]['viewBean']["buyRate"] is not None:
                            self._state = (energy["getPlantMeterChartData"]['viewBean']["buyRate"])
                if self._type == 'sellRate':
                    if 'sellRate' in energy["getPlantMeterChartData"]['viewBean']:
                        if energy["getPlantMeterChartData"]['viewBean']["sellRate"] is not None:
                            self._state = (energy["getPlantMeterChartData"]['viewBean']["sellRate"])
                if self._type == 'selfConsumedRate1':
                    if 'selfConsumedRate1' in energy["getPlantMeterChartData"]['viewBean']:
                        if energy["getPlantMeterChartData"]['viewBean']["selfConsumedRate1"] is not None:
                            self._state = (energy["getPlantMeterChartData"]['viewBean']["selfConsumedRate1"])
                if self._type == 'selfConsumedRate2':
                    if 'selfConsumedRate2' in energy["getPlantMeterChartData"]['viewBean']:
                        if energy["getPlantMeterChartData"]['viewBean']["selfConsumedRate2"] is not None:
                            self._state = (energy["getPlantMeterChartData"]['viewBean']["selfConsumedRate2"])
                if self._type == 'plantTreeNum':
                    if 'plantTreeNum' in energy["getPlantMeterChartData"]['viewBean']:
                        if energy["getPlantMeterChartData"]['viewBean']["plantTreeNum"] is not None:
                            self._state = (energy["getPlantMeterChartData"]['viewBean']["plantTreeNum"])


                # dataCountList
                if self._type == 'totalGridPower':
                    if 'dataCountList' in energy:
                        if energy["getPlantMeterChartData"]['dataCountList'][4][-1] is not None:
                            self._state = float(energy["getPlantMeterChartData"]['dataCountList'][3][-1])
                if self._type == 'totalLoadPower':
                    if 'dataCountList' in energy:
                        if energy["getPlantMeterChartData"]['dataCountList'][4][-1] is not None:
                            self._state = float(energy["getPlantMeterChartData"]['dataCountList'][2][-1])
                if self._type == 'totalPvgenPower':
                    if 'dataCountList' in energy:
                        if energy["getPlantMeterChartData"]['dataCountList'][4][-1] is not None:
                            self._state = float(energy["getPlantMeterChartData"]['dataCountList'][4][-1])


                # getPlantMeterDetailInfo
                if self._type == 'totalPvEnergy':
                    if 'totalPvEnergy' in energy["getPlantMeterDetailInfo"]['plantDetail']:
                        if energy["getPlantMeterDetailInfo"]['plantDetail']["totalPvEnergy"] is not None:
                            self._state = (energy["getPlantMeterDetailInfo"]['plantDetail']["totalPvEnergy"])
                if self._type == 'totalLoadEnergy':
                    if 'totalLoadEnergy' in energy["getPlantMeterDetailInfo"]['plantDetail']:
                        if energy["getPlantMeterDetailInfo"]['plantDetail']["totalLoadEnergy"] is not None:
                            self._state = (energy["getPlantMeterDetailInfo"]['plantDetail']["totalLoadEnergy"])
                if self._type == 'totalBuyEnergy':
                    if 'totalBuyEnergy' in energy["getPlantMeterDetailInfo"]['plantDetail']:
                        if energy["getPlantMeterDetailInfo"]['plantDetail']["totalBuyEnergy"] is not None:
                            self._state = (energy["getPlantMeterDetailInfo"]['plantDetail']["totalBuyEnergy"])
                if self._type == 'totalSellEnergy':
                    if 'totalSellEnergy' in energy["getPlantMeterDetailInfo"]['plantDetail']:
                        if energy["getPlantMeterDetailInfo"]['plantDetail']["totalSellEnergy"] is not None:
                            self._state = (energy["getPlantMeterDetailInfo"]['plantDetail']["totalSellEnergy"])


            # -Debug- adding sensor
            _LOGGER.debug(f"Device: {self._type} State: {self._state}")
