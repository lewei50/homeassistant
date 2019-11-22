"""Support for devicebit via local API."""
import asyncio

from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.const import CONF_IP_ADDRESS, CONF_PORT ,CONF_NAME,CONF_HOST
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.event import async_track_time_interval
import json
from collections import namedtuple

import aiohttp
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

import json
from collections import namedtuple

import aiohttp
import voluptuous as vol
import async_timeout
import requests

class DevicebitError(Exception):
    """Indicates error communicating with devicebit"""


class DiscoveryError(Exception):
    """Raised when unable to discover devicebit"""


DevicebitResponse = namedtuple('DevicebitResponse',
                              'data, serial_number, mac')


class Devicebit:
    """Base wrapper around devicebit HTTP API"""
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def get_data(self):
        try:
            data = await self.make_request(
                self.host, self.port
            )
        except aiohttp.ClientError as ex:
            msg = "Could not connect to devicebit endpoint"
            raise DevicebitError(msg) from ex
        except ValueError as ex:
            msg = "Received non-JSON data from devicebit endpoint"
            raise DevicebitError(msg) from ex
        except vol.Invalid as ex:
            msg = "Received malformed JSON from devicebit"
            raise DevicebitError(msg) from ex
        except:
        	msg = "error"
        	raise DevicebitError("error")
        return data

    @classmethod
    async def make_request(cls, host, port):
        """
        Return instance of 'devicebitResponse'
        Raise exception if unable to get data
        """
        raise NotImplementedError()

    @classmethod
    def sensor_map(cls):
        """
        Return sensor map
        """
        raise NotImplementedError()

async def fetch(url):
    async with aiohttp.request("GET",url) as r:
        #_LOGGER.error(r.status)
        reponse = await r.text(encoding="utf-8")
        #yield reponse
        
async def discover(host, port) -> Devicebit:
    base = 'http://admin:admin@{}:{}/monitorjson'
    url = base.format(host, port)
    #_LOGGER.error(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            #print(resp.status)
            json_data = await resp.json()
            #_LOGGER.error(json_data)
            #json_response = json.loads(json_data)
            if json_data.has_key('HT'):
                _LOGGER.info('3080')
            if json_data.has_key('PM'):
                _LOGGER.info('3000')
    raise DiscoveryError()


class WTH3080(Devicebit):
    __schema = vol.Schema({
    	vol.Required('SN'): str,
    	vol.Required('mac'): str,
    	vol.Required('Data'): list,
    }, extra=vol.REMOVE_EXTRA)
	#Temperature,Humidity
    __sensor_map = {
        'Temperature':             (0, '℃'),
        'Humidity':                (1, '%'),

    }
    
    @staticmethod
    def map_response(resp_data, sensor_map):
        return {
            f"{sensor_name}": resp_data[i]
            for sensor_name, (i, _)
            in sensor_map.items()
        }

    @classmethod
    async def make_request(cls, host, port=80):
        base = 'http://admin:admin@{}:{}/monitorjson'
        url = base.format(host, port)
        #_LOGGER.error(url)
        resp = requests.get(url)
        json_response = resp.json()
        #_LOGGER.error(json_response)
        response = cls.__schema(json_response)
        #_LOGGER.error(cls.map_response(response['Data'], cls.__sensor_map))
        cls.dev_type = "WTH3080"
        return DevicebitResponse(
            data=cls.map_response(response['Data'], cls.__sensor_map),
            serial_number=response['SN'],
            mac=response['mac']
        )

    @classmethod
    def sensor_map(cls):
        """
        Return sensor map
        """
        return cls.__sensor_map

class YNM3000(Devicebit):
    __schema = vol.Schema({
    	vol.Required('SN'): str,
    	vol.Required('mac'): str,
    	vol.Required('Data'): list,
    }, extra=vol.REMOVE_EXTRA)
	#Temperature,Humidity
    __sensor_map = {
        'Temperature':			(0, '℃'),
        'Humidity':				(1, '%'),
		'PM25':					(2, 'ug/m3'),
		'AQI':					(3, ''),
		
		'HCHO':					(4, 'mg/m3'),
		'CO2':					(5, 'ppm'),

    }
    
    @staticmethod
    def map_response(resp_data, sensor_map):
        return {
            f"{sensor_name}": resp_data[i]
            for sensor_name, (i, _)
            in sensor_map.items()
        }

    @classmethod
    async def make_request(cls, host, port=80):
        base = 'http://admin:admin@{}:{}/monitorjson'
        url = base.format(host, port)
        #_LOGGER.error(url)
        resp = requests.get(url)
        json_response = resp.json()
        #_LOGGER.error(json_response)
        response = cls.__schema(json_response)
        #_LOGGER.error(cls.map_response(response['Data'], cls.__sensor_map))
        cls.dev_type = "YNM3000"
        return DevicebitResponse(
            data=cls.map_response(response['Data'], cls.__sensor_map),
            serial_number=response['SN'],
            mac=response['mac']
        )

    @classmethod
    def sensor_map(cls):
        """
        Return sensor map
        """
        return cls.__sensor_map

# registry of devicebits
REGISTRY = [WTH3080,YNM3000]


REQUEST_TIMEOUT = 5


async def rt_request(inv, retry, t_wait=0):
    """Make call to devicebit endpoint."""
    if t_wait > 0:
        msg = "Timeout connecting to devicebit, waiting %d to retry."
        _LOGGER.error(msg, t_wait)
        await asyncio.sleep(t_wait)
    new_wait = (t_wait*2)+5
    retry = retry - 1
    try:
        with async_timeout.timeout(REQUEST_TIMEOUT):
            return await inv.get_data()
    except asyncio.TimeoutError:
        if retry > 0:
            return await rt_request(inv,
                                    retry,
                                    new_wait)
        _LOGGER.error("Too many timeouts connecting to Devicebit.")
        raise


async def real_time_api(ip_address, port=80):
    i = await discover(ip_address, port)
    return RealTimeAPI(i)


class RealTimeAPI:
    """devicebit real time API"""
    # pylint: disable=too-few-public-methods

    def __init__(self, inv):
        """Initialize the API client."""
        self.devicebit = inv

    async def get_data(self):
        """Query the real time API"""
        return await rt_request(self.devicebit,3)


DEFAULT_PORT = 80

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    }
)

SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Platform setup."""
    _LOGGER.info("setup:"+config[CONF_HOST])
    try:
        base = 'http://admin:admin@{}:{}/monitorjson'
        url = base.format(config[CONF_HOST], config[CONF_PORT])
        #_LOGGER.error(url)
        resp = requests.get(url)
        json_data = resp.json()
        if 'SN' in json_data:
            serial = json_data['SN']
        if 'mac' in json_data:
            mac = json_data['mac']
        if 'server' in json_data:
            server = json_data['server']
    except:
        raise PlatformNotReady
    #_LOGGER.error(mac)
    
    
    #_LOGGER.error(api.devicebit.dev_type)
    devices = []
    
    if 'HT'==server:
        _LOGGER.info('3080')
        api = RealTimeAPI(WTH3080(config[CONF_HOST], config[CONF_PORT]))
        for sensor, (idx, unit) in api.devicebit.sensor_map().items():
	        uid = f"{config[CONF_NAME]}-{mac}-{serial}-{idx}"
	        #_LOGGER.error(f"3080 uid:{uid}")
	        devices.append(Devicebit(uid, serial, sensor, unit,config[CONF_NAME]))
    if 'PM'==server:
        _LOGGER.info('3000')
        api = RealTimeAPI(YNM3000(config[CONF_HOST], config[CONF_PORT]))
        for sensor, (idx, unit) in api.devicebit.sensor_map().items():
	        uid = f"{config[CONF_NAME]}-{mac}-{serial}-{idx}"
	        #_LOGGER.error(f"3000 uid:{uid}")
	        devices.append(Devicebit(uid, serial, sensor, unit,config[CONF_NAME]))
			
    endpoint = RealTimeDataEndpoint(hass, api)
    endpoint.ready.set()
    hass.async_add_job(endpoint.async_refresh)
    async_track_time_interval(hass, endpoint.async_refresh, SCAN_INTERVAL)
    endpoint.sensors = devices
    async_add_entities(devices)


class RealTimeDataEndpoint:
    """Representation of a Sensor."""

    def __init__(self, hass, api):
        """Initialize the sensor."""
        self.hass = hass
        self.api = api
        self.ready = asyncio.Event()
        self.sensors = []

    async def async_refresh(self, now=None):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            api_response = await self.api.get_data()
            self.ready.set()
        except DevicebitError:
            if now is not None:
                self.ready.clear()
                return
            raise PlatformNotReady
        data = api_response.data
        for sensor in self.sensors:
            if sensor.key in data:
                sensor.value = data[sensor.key]
                sensor.schedule_update_ha_state()


class Devicebit(Entity):
    """Class for a sensor."""

    def __init__(self, uid, serial, key, unit,dev_name):
        """Initialize an devicebit sensor."""
        self.uid = uid
        self.serial = serial
        self.key = key
        self.value = None
        self.unit = unit
        self.dev_name = dev_name
        self.dev_type = "WTH3080"

    @property
    def state(self):
        """State of this devicebit attribute."""
        return self.value

    @property
    def unique_id(self):
        """Return unique id."""
        return self.uid

    @property
    def name(self):
        """Name of this devicebit attribute."""
        return f"{self.dev_name} {self.key}"
        
    @property
    def icon(self):
        return "mdi:flash"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self.unit

    @property
    def should_poll(self):
        """No polling needed."""
        return False                                                                                                                                                                                                                                                                                          
