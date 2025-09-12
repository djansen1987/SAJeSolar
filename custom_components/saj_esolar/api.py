"""API client for interacting with the eSolar site."""

import calendar
from datetime import UTC, date, datetime, timedelta
import logging
from ssl import SSLCertVerificationError

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.exceptions import HomeAssistantError

from .const import DEVICE_TYPES, DOMAIN

_LOGGER = logging.getLogger(__name__)

UNKNOWN_AUTH_ERROR = "Authentication failed for unknown reasons"
AUTHENTICATION_FAILED = "Authentication failed, please check your credentials"


def _add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _add_years(d, years):
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))


class EsolarProvider:
    """Handless the information of the url of a particular esolar provider (e.g. saj, greenheiss)."""

    def __init__(
        self, host: str, path: str, use_https: bool = True, verify_ssl: bool = True
    ) -> None:
        """Initialize the sensor with the specified host, path, and protocol.

        Args:
            host (str): The hostname or IP address of the target device.
            path (str): The API or resource path to access on the device.
            use_https (str): if https should be used (defaults true).
            verify_ssl (bool): Whether to verify SSL certificates. Default to true.
        """
        self.host = host
        self.path = path
        self.protocol = "https" if use_https else "http"
        self.verify_ssl = verify_ssl

    def getBaseDomain(self):
        """Returns the domain part of the provider url."""
        return f"{self.protocol}://{self.host}"

    def getBaseUrl(self):
        """Returns the base path of the application.

        It is mostly 'cloud' or 'saj'. but might change depending on the provider
        """
        return f"{self.getBaseDomain()}/{self.path}"

    def getLoginUrl(self):
        """The url where users can login."""
        return f"{self.getBaseUrl()}/login"

    def getVerifySSL(self):
        """Return if SSL should be verified."""
        return self.verify_ssl


class ESolarConfiguration:
    """Holds configuration for the integration."""

    def __init__(
        self,
        username: str,
        password: str,
        sensors: str,
        plant_id: int,
        provider: EsolarProvider,
    ) -> None:
        """Initialize the data object."""

        self.provider = provider
        self.username = username
        self.password = password
        self.sensors = sensors
        self.plant_id = plant_id
        self._data = None


class ApiError(HomeAssistantError):
    """Custom exception for API errors."""


class ApiAuthError(HomeAssistantError):
    """Custom exception for API authentication errors."""


class EsolarApiClient:
    """API client for interacting with the eSolar site."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: ESolarConfiguration,
    ) -> None:
        """Initialize the API client.

        Args:
            hass: homeassistant object
            config: the configuration of the integration.
        """

        self.config = config
        self.provider = config.provider
        self.username = config.username
        self.password = config.password
        self._session = async_create_clientsession(
            hass, verify_ssl=self.provider.getVerifySSL()
        )  # some providers have SSL chains not accepted by hass

    async def fetch_data(self):
        """Fetch and aggregate data from the eSolar site."""
        data = {}
        try:
            today = date.today()
            clientDate = today.strftime("%Y-%m-%d")
            # Make sure we have a valid session cookie
            await self.verifyLogin()

            headers = {
                "Connection": "keep-alive",
                "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "DNT": "1",
                "X-Requested-With": "XMLHttpRequest",
                "sec-ch-ua-mobile": "?0",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": self.provider.host,
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": f"{self.provider.getBaseUrl()}/monitor/home/index",
                "Accept-Language": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7",
            }
            # Get list of plants from esolar to get configured plant
            url_userPlantList = (
                f"{self.provider.getBaseUrl()}/monitor/site/getUserPlantList"
            )

            payload_userPlantList = f"pageNo=&pageSize=&orderByIndex=&officeId=&clientDate={clientDate}&runningState=&selectInputType=1&plantName=&deviceSn=&type=&countryCode=&isRename=&isTimeError=&systemPowerLeast=&systemPowerMost="
            response_userPlantList = await self._session.post(
                url_userPlantList, headers=headers, data=payload_userPlantList
            )

            if response_userPlantList.status != 200:
                _LOGGER.error(
                    "%s returned %s",
                    response_userPlantList.url,
                    response_userPlantList.status,
                )
                raise ApiError("Error fetching plant info from eSolar API")

            plantListInfo = await response_userPlantList.json()
            plantuid = plantListInfo["plantList"][self.config.plant_id]["plantuid"]

            # Get the details of the configuredd plant
            url_plantDetail = (
                f"{self.provider.getBaseUrl()}/monitor/site/getPlantDetailInfo"
            )
            payload_plantDetail = f"plantuid={plantuid}&clientDate={clientDate}"

            response_plantDetail = await self._session.post(
                url_plantDetail, headers=headers, data=payload_plantDetail
            )

            if response_plantDetail.status != 200:
                _LOGGER.error(
                    "%s returned %s",
                    response_plantDetail.url,
                    response_plantDetail.status,
                )
                raise ApiError("Error fetching plant details from eSolar API")

            plantDetails = await response_plantDetail.json()
            _LOGGER.debug("plantDetails: %s", plantDetails)
            plantDetails.update(plantListInfo)

            # device info. provide info on hardware devices.
            # some of it is required for subsequent requests.
            url_devicesInfo = (
                f"{self.provider.getBaseUrl()}/cloudMonitor/device/findDevicePageList"
            )
            payload_devicesInfo = f"officeId=&pageNo=&pageSize=&orderName=1&orderType=2&plantuid={plantuid}&deviceStatus=&localDate=&localMonth="
            response_deviceInfo = await self._session.post(
                url_devicesInfo, headers=headers, data=payload_devicesInfo
            )
            if response_deviceInfo.status != 200:
                _LOGGER.error(
                    "%s returned %s",
                    response_deviceInfo.url,
                    response_deviceInfo.status,
                )
                raise ApiError("Error fetching device info from eSolar API")

            data_devicesInfo = await response_deviceInfo.json()
            plantDetails.update(data_devicesInfo)
            if self.config.sensors == "h1":
                deviceSnArr = next(
                    (
                        item["devicesn"]
                        for item in plantDetails["list"]
                        if item["type"] == DEVICE_TYPES["Battery"]
                    ),
                    plantDetails["plantDetail"]["snList"][0],
                )
            else:
                deviceSnArr = plantDetails["plantDetail"]["snList"][0]

            # getPlantDetailChart2
            previousChartDay = today - timedelta(days=1)
            nextChartDay = today + timedelta(days=1)
            chartDay = today.strftime("%Y-%m-%d")
            previousChartMonth = _add_months(today, -1).strftime("%Y-%m")
            nextChartMonth = _add_months(today, 1).strftime("%Y-%m")
            chartMonth = today.strftime("%Y-%m")
            previousChartYear = _add_years(today, -1).strftime("%Y")
            nextChartYear = _add_years(today, 1).strftime("%Y")
            chartYear = today.strftime("%Y")
            epochmilliseconds = int(datetime.now(UTC).timestamp() * 1000)
            elecDevicesn = deviceSnArr if self.config.sensors == "h1" else ""
            url_plantDetailChart2 = f"{self.provider.getBaseUrl()}/monitor/site/getPlantDetailChart2?plantuid={plantuid}&chartDateType=1&energyType=0&clientDate={clientDate}&deviceSnArr={deviceSnArr}&chartCountType=2&previousChartDay={previousChartDay}&nextChartDay={nextChartDay}&chartDay={chartDay}&previousChartMonth={previousChartMonth}&nextChartMonth={nextChartMonth}&chartMonth={chartMonth}&previousChartYear={previousChartYear}&nextChartYear={nextChartYear}&chartYear={chartYear}&elecDevicesn={elecDevicesn}&_={epochmilliseconds}"
            response_PlantDetailChart2 = await self._session.post(
                url_plantDetailChart2, headers=headers
            )

            if response_PlantDetailChart2.status != 200:
                _LOGGER.error(
                    "%s returned %s",
                    response_PlantDetailChart2.url,
                    response_PlantDetailChart2.status,
                )
                raise ApiError("Error fetching plant charts from eSolar API")

            plantcharts = await response_PlantDetailChart2.json()
            plantDetails.update(plantcharts)

            # H1 Module
            if self.config.sensors == "h1":
                # getStoreOrAcDevicePowerInfo
                url_getStoreOrAcDevicePowerInfo = f"{self.provider.getBaseUrl()}/monitor/site/getStoreOrAcDevicePowerInfo?plantuid=&devicesn={deviceSnArr}&_={epochmilliseconds}"

                response_getStoreOrAcDevicePowerInfo = await self._session.post(
                    url_getStoreOrAcDevicePowerInfo, headers=headers
                )

                if response_getStoreOrAcDevicePowerInfo.status != 200:
                    _LOGGER.error(
                        "%s returned %s",
                        response_getStoreOrAcDevicePowerInfo.url,
                        response_getStoreOrAcDevicePowerInfo.status,
                    )
                    raise ApiError("Error fetching H1 module data from eSolar API")

                result_getStoreOrAcDevicePowerInfo = (
                    await response_getStoreOrAcDevicePowerInfo.json()
                )
                plantDetails.update(result_getStoreOrAcDevicePowerInfo)
                _LOGGER.debug(
                    "result_getStoreOrAcDevicePowerInfo: %s",
                    result_getStoreOrAcDevicePowerInfo,
                )

            elif self.config.sensors == "None":
                data = plantDetails
            else:
                # Data = plantdetails
                data = plantDetails

            # Sec module
            if self.config.sensors == "saj_sec":
                # getPlantMeterModuleList
                url_module = f"{self.provider.getBaseUrl()}/cloudmonitor/plantMeterModule/getPlantMeterModuleList"

                payload_module = f"pageNo=&pageSize=&plantUid={plantuid}"

                response_module = await self._session.post(
                    url_module, headers=headers, data=payload_module
                )

                if response_module.status != 200:
                    _LOGGER.error(
                        "%s returned %s", response_module.url, response_module.status
                    )
                    raise ApiError("Error fetching module list from eSolar API")

                getPlantMeterModuleList = await response_module.json()

                temp_getPlantMeterModuleList = {}
                temp_getPlantMeterModuleList["getPlantMeterModuleList"] = (
                    getPlantMeterModuleList
                )

                plantDetails.update(temp_getPlantMeterModuleList)

                moduleSn = plantDetails["getPlantMeterModuleList"]["moduleList"][0][
                    "moduleSn"
                ]

                # -Debug- Sec module serial number
                _LOGGER.debug(moduleSn)

                # findDevicePageList
                url_findDevicePageList = f"{self.provider.getBaseUrl()}/cloudMonitor/device/findDevicePageList"

                payload_findDevicePageList = f"officeId=1&pageNo=&pageSize=&orderName=1&orderType=2&plantuid={plantuid}&deviceStatus=&localDate={chartMonth}&localMonth={chartMonth}"

                response_findDevicePageList = await self._session.post(
                    url_findDevicePageList,
                    headers=headers,
                    data=payload_findDevicePageList,
                )

                if response_findDevicePageList.status != 200:
                    _LOGGER.error(
                        "%s returned %s",
                        response_findDevicePageList.url,
                        response_findDevicePageList.status,
                    )
                    raise ApiError("Error fetching device list from eSolar API")

                findDevicePageList = await response_findDevicePageList.json()

                temp_findDevicePageList = {}
                temp_findDevicePageList["findDevicePageList"] = findDevicePageList

                plantDetails.update(temp_findDevicePageList)

                # getPlantMeterDetailInfo
                url_getPlantMeterDetailInfo = (
                    f"{self.provider.getBaseUrl()}/monitor/site/getPlantMeterDetailInfo"
                )

                payload_getPlantMeterDetailInfo = (
                    f"plantuid={plantuid}&clientDate={clientDate}"
                )

                response_getPlantMeterDetailInfo = await self._session.post(
                    url_getPlantMeterDetailInfo,
                    headers=headers,
                    data=payload_getPlantMeterDetailInfo,
                )

                if response_getPlantMeterDetailInfo.status != 200:
                    _LOGGER.error(
                        "%s returned %s",
                        response_getPlantMeterDetailInfo.url,
                        response_getPlantMeterDetailInfo.status,
                    )
                    raise ApiError("Error fetching meter details from eSolar API")

                getPlantMeterDetailInfo = await response_getPlantMeterDetailInfo.json()

                temp_getPlantMeterDetailInfo = {}
                temp_getPlantMeterDetailInfo["getPlantMeterDetailInfo"] = (
                    getPlantMeterDetailInfo
                )

                plantDetails.update(temp_getPlantMeterDetailInfo)

                # getPlantMeterEnergyPreviewInfo
                url_getPlantMeterEnergyPreviewInfo = f"{self.provider.getBaseUrl()}/monitor/site/getPlantMeterEnergyPreviewInfo?plantuid={plantuid}&moduleSn={moduleSn}&_={epochmilliseconds}"

                response_getPlantMeterEnergyPreviewInfo = await self._session.get(
                    url_getPlantMeterEnergyPreviewInfo, headers=headers
                )

                if response_getPlantMeterEnergyPreviewInfo.status != 200:
                    _LOGGER.error(
                        "%s returned %s",
                        response_getPlantMeterEnergyPreviewInfo.url,
                        response_getPlantMeterEnergyPreviewInfo.status,
                    )
                    raise ApiError("Error fetching energy preview from eSolar API")

                getPlantMeterEnergyPreviewInfo = (
                    await response_getPlantMeterEnergyPreviewInfo.json()
                )

                temp_getPlantMeterEnergyPreviewInfo = {}
                temp_getPlantMeterEnergyPreviewInfo[
                    "getPlantMeterEnergyPreviewInfo"
                ] = getPlantMeterEnergyPreviewInfo

                plantDetails.update(temp_getPlantMeterEnergyPreviewInfo)

                # Get Sec Meter details
                url_getPlantMeterChartData = f"{self.provider.getBaseUrl()}/monitor/site/getPlantMeterChartData?plantuid={plantuid}&chartDateType=1&energyType=0&clientDate={clientDate}&deviceSnArr=&chartCountType=2&previousChartDay={previousChartDay}&nextChartDay={nextChartDay}&chartDay={chartDay}&previousChartMonth={previousChartMonth}&nextChartMonth={nextChartMonth}&chartMonth={chartMonth}&previousChartYear={previousChartYear}&nextChartYear={nextChartYear}&chartYear={chartYear}&moduleSn={moduleSn}&_={epochmilliseconds}"

                response_getPlantMeterChartData = await self._session.post(
                    url_getPlantMeterChartData, headers=headers
                )

                if response_getPlantMeterChartData.status != 200:
                    _LOGGER.error(
                        "%s returned %s",
                        response_getPlantMeterChartData.url,
                        response_getPlantMeterChartData.status,
                    )
                    raise ApiError("Error fetching meter chart data from eSolar API")

                getPlantMeterChartData = await response_getPlantMeterChartData.json()

                temp_getPlantMeterChartData = {}
                temp_getPlantMeterChartData["getPlantMeterChartData"] = (
                    getPlantMeterChartData
                )

                plantDetails.update(temp_getPlantMeterChartData)

                # Data = plantdetails including Sec module
                data = plantDetails
            elif self.config.sensors == "None":
                data = plantDetails
            else:
                # Data = plantdetails Wtihout Sec module
                data = plantDetails

        # Error logging
        except aiohttp.ClientError as err:
            _LOGGER.error("Cannot poll eSolar using url: %s", err)
            raise ApiError("Cannot poll eSolar using url") from err
        except TimeoutError as err:
            _LOGGER.error(
                "Timeout error occurred while polling eSolar using url: %s", err
            )
            raise ApiError("Timeout error occurred while polling eSolar ") from err
        return data

    async def verifyLogin(self) -> None:
        """Verify login to eSolar site.

        The eSolar site uses a form based login that returns a redirect and sets a cookie on success.
        The cookie is managed for us by the aiohttp session. So subsequent calls using the same session will be authenticated.
        """
        url = self.provider.getLoginUrl()
        _LOGGER.debug("Trying to login on: %s", url)

        payload = {
            "lang": "en",
            "username": self.username,
            "password": self.password,
            "rememberMe": "true",
        }
        headers_login = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": "org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=en; op:_lang=en",
            "DNT": "1",
            "Host": self.provider.host,
            "Origin": self.provider.host,
            "Referer": self.provider.getLoginUrl(),
            "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            "sec-ch-ua-mobile": "?0",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        }
        # do not allow redirects, because a successful login returns a 302 to the dashboard
        try:
            response = await self._session.post(
                url, headers=headers_login, data=payload, allow_redirects=False
            )
            _LOGGER.debug("login response: %s, %s", response.status, response.text)
        except SSLCertVerificationError as err:
            _LOGGER.error("SSL Certificate error: %s", err)
            raise ApiError("SSL Certificate error") from err

        # the login url is a html page so a bad credential returns a 200 with the same page
        # a good login returns a 302/303 to the dashboard
        _LOGGER.debug("%s returned %s", response.url, response.status)
        if response.status in {200, 401, 403}:
            raise ApiAuthError(AUTHENTICATION_FAILED)
        if response.status in {302, 303} and "Location" in response.headers:
            _LOGGER.debug(
                "apparently successfull redirect %s, redirecting to %s",
                response.status,
                response.headers["Location"],
            )
            return
        raise ApiAuthError(UNKNOWN_AUTH_ERROR)
