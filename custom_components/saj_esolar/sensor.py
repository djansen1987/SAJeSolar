"""
Alternative for the SAJ local API sensor. Unfortunally there is no public api. 
This Sensor will read the private api of the eSolar portal at https://fop.saj-electric.com/
"""

import asyncio
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
    ATTR_LAST_RESET,
    ATTR_STATE_CLASS,
    PLATFORM_SCHEMA,
    STATE_CLASS_MEASUREMENT,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_NAME,
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_HOST,
    CONF_PORT,
    CONF_RESOURCES,
    CONF_USERNAME, 
    CONF_PASSWORD, 
    CONF_SENSORS,
    CONF_DEVICE_ID,
    CONF_SCAN_INTERVAL,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
)
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

currentdate = datetime.date.today().strftime('%Y-%m-%d')

BASE_URL = 'https://fop.saj-electric.com/saj/login'
_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=300)

SENSOR_PREFIX = 'esolar '
ATTR_MEASUREMENT = "measurement"
ATTR_SECTION = "section"

SENSOR_LIST = {
    "nowPower",
    "runningState",
    "todayElectricity",
    "monthElectricity",
    "yearElectricity",
    "totalElectricity",
    "todayGridIncome",
    "income",
    "lastUploadTime",
    "totalPlantTreeNum",
    "totalReduceCo2",
    "todayAlarmNum",
    "plantuid",
    "plantname",
    "currency",
    "address",
    "isOnline",
    "status",
    "peakPower",
    "pvElec",
    "useElec",
    "buyElec",
    "sellElec",
    "buyRate",
    "sellRate",
    "selfConsumedRate1",
    "selfConsumedRate2",
    "selfConsumedEnergy1",
    "selfConsumedEnergy2",
    "plantTreeNum",
    "reduceCo2",
    "totalGridPower",
    "totalLoadPower",
    "totalPvgenPower",
}

SENSOR_TYPES: Final[tuple[SensorEntityDescription]] = (
    SensorEntityDescription(
        key="nowPower",
        name="nowPower",
        icon="mdi:solar-power",
        unit_of_measurement=POWER_WATT,
        device_class=DEVICE_CLASS_POWER,
    ),
    SensorEntityDescription(
        key="runningState",
        name="runningState",
        icon="mdi:solar-panel",
    ),
    SensorEntityDescription(
        key="todayElectricity",
        name="todayElectricity",
        icon="mdi:solar-panel-large",
        unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    SensorEntityDescription(
        key="monthElectricity",
        name="monthElectricity",
        icon="mdi:solar-panel-large",
        unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    SensorEntityDescription(
        key="yearElectricity",
        name="yearElectricity",
        icon="mdi:solar-panel-large",
        unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    SensorEntityDescription(
        key="totalElectricity",
        name="totalElectricity",
        icon="mdi:solar-panel-large",
        unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_MEASUREMENT,
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
        key="todayAlarmNum",
        name="todayAlarmNum",
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
        unit_of_measurement=POWER_WATT,
        device_class=DEVICE_CLASS_POWER,
    ),
    SensorEntityDescription(
        key="pvElec",
        name="pvElec",
        icon="mdi:solar-panel-large",
        unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    SensorEntityDescription(
        key="useElec",
        name="useElec",
        icon="mdi:solar-panel-large",
        unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    SensorEntityDescription(
        key="buyElec",
        name="buyElec",
        icon="mdi:solar-panel-large",
        unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    SensorEntityDescription(
        key="sellElec",
        name="sellElec",
        icon="mdi:solar-panel-large",
        unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_MEASUREMENT,
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
        unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    SensorEntityDescription(
        key="selfConsumedEnergy2",
        name="selfConsumedEnergy2",
        icon="mdi:solar-panel-large",
        unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_MEASUREMENT,
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
        unit_of_measurement=POWER_WATT,
        device_class=DEVICE_CLASS_POWER,
    ),
    SensorEntityDescription(
        key="totalLoadPower",
        name="totalLoadPower",
        icon="mdi:solar-panel",
        unit_of_measurement=POWER_WATT,
        device_class=DEVICE_CLASS_POWER,
    ),
    SensorEntityDescription(
        key="totalPvgenPower",
        name="totalPvgenPower",
        icon="mdi:solar-panel",
        unit_of_measurement=POWER_WATT,
        device_class=DEVICE_CLASS_POWER,
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
        vol.Optional(CONF_DEVICE_ID, default="None"): cv.string,
    }
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):

    """Setup the SAJ eSolar sensors."""

    session = async_get_clientsession(hass)
    data = SAJeSolarMeterData(session, config.get(CONF_USERNAME), config.get(CONF_PASSWORD), config.get(CONF_SENSORS), config.get(CONF_DEVICE_ID))
    await data.async_update()

    entities = []
    for description in SENSOR_TYPES:
        if description.key in config[CONF_RESOURCES]:
            sensor = SAJeSolarMeterSensor(description, data)
            entities.append(sensor)
    async_add_entities(entities, True)
    return True

class SAJeSolarMeterData(object):
    """Handle eSolar object and limit updates."""

    def __init__(self, session, username, password, sensors, sec_sn):
        """Initialize the data object."""

        self._session = session
        self._url = BASE_URL
        self.username = username
        self.password = password
        self.sensors = sensors
        self.sec_sn = sec_sn
        self._data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Download and update data from SAJeSolar."""

        try:
            with async_timeout.timeout(55):

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
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Cache-Control': 'max-age=0',
                    'Connection': 'keep-alive',
                    'Content-Length': '79',
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
                response = await self._session.post(url, headers=headers, data=payload)

                _LOGGER.debug(response.json())
                _LOGGER.debug(response.text())

                if response.status != 200:
                    _LOGGER.error(f"{response.url} returned {response.status}")
                    return

# Get API Plant info from Esolar Portal

                url2 = 'https://fop.saj-electric.com/saj/monitor/site/getUserPlantList'
                headers2 = {
                    'Connection': 'keep-alive',
                    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'DNT': '1',
                    'X-Requested-With': 'XMLHttpRequest',
                    'sec-ch-ua-mobile': '?0',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Origin': 'https://fop.saj-electric.com',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Referer': 'https://fop.saj-electric.com/saj/monitor/site/list',
                    'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7'
                }

                payload2= "pageNo=&pageSize=&orderByIndex=&officeId=&clientDate={}&runningState=&selectInputType=1&plantName=&deviceSn=&type=&countryCode=&isRename=&isTimeError=&systemPowerLeast=&systemPowerMost=".format(clientDate)
                response2 = await self._session.post(url2, headers=headers2, data=payload2)

                _LOGGER.debug(response2.json())
                _LOGGER.debug(response2.text())

                if response2.status != 200:
                    _LOGGER.error(f"{response2.url} returned {response2.status}")
                    return

                plantInfo = await response2.json()
                plantuid = plantInfo['plantList'][0]['plantuid']

# Get API Plant Solar Details

                url3 = "https://fop.saj-electric.com/saj/monitor/site/getPlantDetailInfo"   
                payload3="plantuid={}&clientDate={}".format(plantuid,currentdate)
                headers3 = {
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
                response3 = await self._session.post(url3, headers=headers3, data=payload3)
                
                _LOGGER.debug(response3.json())
                _LOGGER.debug(response3.text())

                if response3.status != 200:
                    _LOGGER.error(f"{response3.url} returned {response3.status}")
                    return

                plantDetails = await response3.json()
                plantDetails.update(plantInfo)


# getPlantDetailChart2

                plantuid = plantDetails['plantList'][0]['plantuid']
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
                                
                url4 = "https://fop.saj-electric.com/saj/monitor/site/getPlantDetailChart2?plantuid={}&chartDateType=1&energyType=0&clientDate={}&deviceSnArr={}&chartCountType=2&previousChartDay={}&nextChartDay={}&chartDay={}&previousChartMonth={}&nextChartMonth={}&chartMonth={}&previousChartYear={}&nextChartYear={}&chartYear={}&elecDevicesn=&_={}".format(plantuid,clientDate,deviceSnArr,previousChartDay,nextChartDay,chartDay,previousChartMonth,nextChartMonth,chartMonth,previousChartYear,nextChartYear,chartYear,epochmilliseconds)
                headers4 = {
                    'Connection': 'keep-alive',
                    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'DNT': '1',
                    'X-Requested-With': 'XMLHttpRequest',
                    'sec-ch-ua-mobile': '?0',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Referer': 'https://fop.saj-electric.com/saj/monitor/home/index',
                    'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7'
                }

                response4 = await self._session.post(url4, headers=headers4)

                _LOGGER.debug(response4.json())
                _LOGGER.debug(response4.text())

                if response4.status != 200:
                    _LOGGER.error(f"{response4.url} returned {response4.status}")
                    return

                plantcharts = await response4.json()
                plantDetails.update(plantcharts)




                if self.sensors == "saj_sec":
# getPlantMeterModuleList
                    url_module = "https://fop.saj-electric.com/saj/cloudmonitor/plantMeterModule/getPlantMeterModuleList"

                    payload_module = "pageNo=&pageSize=&plantUid={}".format(plantuid)
                    headers_module = {
                        'Connection': 'keep-alive',
                        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'DNT': '1',
                        'X-Requested-With': 'XMLHttpRequest',
                        'sec-ch-ua-mobile': '?0',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
                        'Sec-Fetch-Site': 'same-origin',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Dest': 'empty',
                        'Referer': 'https://fop.saj-electric.com/saj/monitor/home/index',
                        'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7'
                    }                  
                    
                    response_module = await self._session.post(url_module, headers=headers_module, data=payload_module)
                
                    _LOGGER.debug(response_module.json())
                    _LOGGER.debug(response_module.text())

                    if response_module.status != 200:
                        _LOGGER.error(f"{response_module.url} returned {response_module.status}")
                        return

                    getPlantMeterModuleList = await response_module.json()
                    plantDetails.update(getPlantMeterModuleList)
                    _LOGGER.debug(getPlantMeterModuleList)

# findDevicePageList

                    url_findDevicePageList = "https://fop.saj-electric.com/saj/cloudMonitor/device/findDevicePageList"

                    payload_findDevicePageList = "officeId=1&pageNo=&pageSize=&orderName=1&orderType=2&plantuid={}&deviceStatus=&localDate={}&localMonth={}".format(plantuid,chartMonth,chartMonth)
                    headers_findDevicePageList = {
                        'Connection': 'keep-alive',
                        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'DNT': '1',
                        'X-Requested-With': 'XMLHttpRequest',
                        'sec-ch-ua-mobile': '?0',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
                        'Sec-Fetch-Site': 'same-origin',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Dest': 'empty',
                        'Referer': 'https://fop.saj-electric.com/saj/monitor/home/index',
                        'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7'
                    }

                    response_findDevicePageList = await self._session.post(url_findDevicePageList, headers=headers_findDevicePageList, data=payload_findDevicePageList)
                
                    _LOGGER.debug(response_findDevicePageList.json())
                    _LOGGER.debug(response_findDevicePageList.text())

                    if response_findDevicePageList.status != 200:
                        _LOGGER.error(f"{response_findDevicePageList.url} returned {response_findDevicePageList.status}")
                        return

                    findDevicePageList = await response_findDevicePageList.json()
                    plantDetails.update(findDevicePageList)

                    
                    # Get Sec Meter details 1/2
                    # moduleSn = self.sec_sn #plantDetails['list'][0]['kitSn']
                    moduleSn = plantDetails['moduleList'][0]['moduleSn']
                    # _LOGGER.warning(moduleSn)

                    url_getPlantMeterChartData = "https://fop.saj-electric.com/saj/monitor/site/getPlantMeterChartData?plantuid={}&chartDateType=1&energyType=0&clientDate={}&deviceSnArr=&chartCountType=2&previousChartDay={}&nextChartDay={}&chartDay={}&previousChartMonth={}&nextChartMonth={}&chartMonth={}&previousChartYear={}&nextChartYear={}&chartYear={}&moduleSn={}&_={}".format(plantuid,clientDate,previousChartDay,nextChartDay,chartDay,previousChartMonth,nextChartMonth,chartMonth,previousChartYear,nextChartYear,chartYear,moduleSn,epochmilliseconds)
                    # _LOGGER.warning(url6)

                    headers_getPlantMeterChartData = {
                        'Connection': 'keep-alive',
                        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'DNT': '1',
                        'X-Requested-With': 'XMLHttpRequest',
                        'sec-ch-ua-mobile': '?0',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
                        'Sec-Fetch-Site': 'same-origin',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Dest': 'empty',
                        'Referer': 'https://fop.saj-electric.com/saj/monitor/home/index',
                        'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7'
                    }

                    response_getPlantMeterChartData = await self._session.post(url_getPlantMeterChartData, headers=headers_getPlantMeterChartData)
                
                    _LOGGER.debug(response_getPlantMeterChartData.json())
                    _LOGGER.debug(response_getPlantMeterChartData.text())

                    if response_getPlantMeterChartData.status != 200:
                        _LOGGER.error(f"{response_getPlantMeterChartData.url} returned {response_getPlantMeterChartData.status}")
                        return

                    getPlantMeterChartData = await response_getPlantMeterChartData.json()
                    plantDetails.update(getPlantMeterChartData)

                    self._data = plantDetails
                    _LOGGER.debug(self._data) 
                    # _LOGGER.debug(self._session.cookie_jar.filter_cookies("https://fop.saj-electric.com"))
                    # self._session.cookie_jar.clear()
                elif self.sensors == "None":
                    self._data = plantDetails
                    _LOGGER.debug(self._data) 
                    # _LOGGER.debug(self._session.cookie_jar.filter_cookies("https://fop.saj-electric.com"))
                    # self._session.cookie_jar.clear()
                else:
                    self._data = plantDetails
                    _LOGGER.debug(self._data) 
                
                _LOGGER.debug(self._session.cookie_jar.filter_cookies("https://fop.saj-electric.com"))
                self._session.cookie_jar.clear()

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

    @property
    def latest_data(self):
        """Return the latest data object."""
        if self._data:
            return self._data
        _LOGGER.error("return data NONE")
        return None

class SAJeSolarMeterSensor(SensorEntity):
    """Collecting data and return sensor entity."""

    def __init__(self, description: SensorEntityDescription, data):
        """Initialize the sensor."""
        self.entity_description = description
        self._data = data

        self._state = None

        self._type = self.entity_description.key
        self._name = SENSOR_PREFIX + self.entity_description.name
        self._icon = self.entity_description.icon
        self._unit_of_measurement = self.entity_description.unit_of_measurement
        self._state_class = self.entity_description.state_class
        self._device_class = self.entity_description.device_class
        self._last_reset = dt.utc_from_timestamp(0)

        self._discovery = False
        self._dev_id = {}

    @property
    def unique_id(self):
        """Return the unique id."""
        return f"{SENSOR_PREFIX}_{self._type}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor. (total/current power consumption/production or total gas used)"""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return self._unit_of_measurement

    @property
    def device_class(self):
        """Return the device class of this entity."""
        return self._device_class

    @property
    def state_class(self):
        """Return the state class of this entity."""
        return self._state_class

    @property
    def last_reset(self):
        """Return the last reset of measurement of this entity."""
        if self._device_class == DEVICE_CLASS_ENERGY:
            return self._last_reset
        return None

    async def async_update(self):
        """Get the latest data and use it to update our sensor state."""

        await self._data.async_update()
        energy = self._data.latest_data

        if energy:
            
            if self._type == 'nowPower':
                self._state = float(energy['plantDetail']["nowPower"])

            if self._type == 'runningState':
                self._state = int(energy['plantDetail']["runningState"])

            if self._type == 'todayElectricity':
                self._state = float(energy['plantDetail']["todayElectricity"])

            if self._type == 'monthElectricity':
                self._state = float(energy['plantDetail']["monthElectricity"])

            if self._type == 'yearElectricity':
                self._state = float(energy['plantDetail']["yearElectricity"])

            if self._type == 'totalElectricity':
                self._state = float(energy['plantDetail']["totalElectricity"])

            if self._type == 'todayGridIncome':
                self._state = float(energy['plantDetail']["todayGridIncome"])

            if self._type == 'income':
                self._state = float(energy['plantDetail']["income"])

            if self._type == 'lastUploadTime':
                self._state = (energy['plantDetail']["lastUploadTime"])

            if self._type == 'totalPlantTreeNum':
                self._state = (energy['plantDetail']["totalPlantTreeNum"])

            if self._type == 'totalReduceCo2':
                self._state = (energy['plantDetail']["totalReduceCo2"])

            if self._type == 'todayAlarmNum':
                self._state = (energy['plantDetail']["todayAlarmNum"])

            if self._type == 'plantuid':
                self._state = (energy['plantList'][0]["plantuid"])

            if self._type == 'plantname':
                self._state = (energy['plantList'][0]["plantname"])

            if self._type == 'currency':
                self._state = (energy['plantList'][0]["currency"])

            if self._type == 'address':
                self._state = (energy['plantList'][0]["address"])

            if self._type == 'isOnline':
                self._state = (energy['plantList'][0]["isOnline"])

            if self._type == 'peakPower':
                if 'peakPower' in energy:
                    if energy['peakPower'] is not None:
                        self._state = float(energy['peakPower'])

            if self._type == 'status':
                self._state = (energy['status'])



            # Sec module Sensors:

            # viewBeam
            if self._type == 'pvElec':
                self._state = float(energy['viewBean']["pvElec"])
                
            if self._type == 'useElec':
                self._state = float(energy['viewBean']["useElec"])

            if self._type == 'buyElec':
                self._state = float(energy['viewBean']["buyElec"])

            if self._type == 'sellElec':
                self._state = float(energy['viewBean']["sellElec"])

            if self._type == 'buyRate':
                self._state = (energy['viewBean']["buyRate"])

            if self._type == 'sellRate':
                self._state = (energy['viewBean']["sellRate"])

            if self._type == 'selfConsumedRate1':
                self._state = (energy['viewBean']["selfConsumedRate1"])

            if self._type == 'selfConsumedRate2':
                self._state = (energy['viewBean']["selfConsumedRate2"])

            if self._type == 'selfConsumedEnergy1':
                self._state = float(energy['viewBean']["selfConsumedEnergy1"])

            if self._type == 'selfConsumedEnergy2':
                self._state = float(energy['viewBean']["selfConsumedEnergy2"])

            if self._type == 'reduceCo2':
                self._state = float(energy['viewBean']["reduceCo2"])


            # dataCountList
            if self._type == 'totalGridPower':
                self._state = float(energy['dataCountList'][4][-1])

            if self._type == 'totalLoadPower':
                self._state = float(energy['dataCountList'][2][-1])

            if self._type == 'totalPvgenPower':
                self._state = float(energy['dataCountList'][3][-1])

            _LOGGER.debug("Device: {} State: {}".format(self._type, self._state)) #debug