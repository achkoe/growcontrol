#!/usr/bin/env python
"""Server to deliver temperature and humidity over xmlrpc."""


import logging
import os
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from dotenv import load_dotenv
import RPi.GPIO as GPIO
import smbus2
from bme280 import BME280
import ADS1x15
from base import load_settings
import configuration
from configuration import port_waterlow, port_watermedium, port_waterhigh

load_dotenv()

# set to True to use mocked values
USE_MOCK_VALUES = os.getenv("USE_MOCK_VALUES", False)


IDENTITY = "sensors_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGLEVEL = int(os.getenv("SENSOR_SERVER_LOGLEVEL", logging.CRITICAL))
LOGGER = logging.getLogger()
LOGGER.setLevel(LOGLEVEL)

GPIO.setmode(GPIO.BCM)


class Bridge():
    def __init__(self):
        GPIO.setup(configuration.port_waterlow, GPIO.IN)
        GPIO.setup([port_waterlow, port_watermedium, port_waterhigh], GPIO.IN)

        # initialize BME280 sensor for temperature and humidity
        bus = smbus2.SMBus(1)
        self.bme280 = BME280(i2c_dev=bus)

        # settings for moisture
        # max value ~17390: dry
        # min value ~7470: wet
        self._min = 7500
        self._max = 17000
        self._slope = (100.0 - 0.0) / (self._min - self._max)
        self._offset = - self._slope * self._max
        self.adc = ADS1x15.ADS1115(1, 0x48)
        self.adc.setGain(self.adc.PGA_4_096V)
        self.adc.setMode(self.adc.MODE_CONTINUOUS)

        self.settings = load_settings()
        self._execute()

    def _execute(self):
        if USE_MOCK_VALUES:
            self._temperature = 24.1
            self._humidity = 48
            self._waterlevel = 0
        else:
            self._temperature = self.bme280.get_temperature()
            self._humidity = self.bme280.get_humidity()
            waterlevels = [GPIO.input(pin) for pin in (
                port_waterlow, port_watermedium, port_waterhigh)]
            # [1, 1, 1] -> water level is below low marker
            # [0, 1, 1] -> water is between low and medium marker
            # [0, 0, 1] -> water is between medium and high marker
            # [0, 0, 0] -> water is between above high marker
            # LOGGER.critical(waterlevels)
            if waterlevels[0] == 1:
                self._waterlevel = 0
            elif waterlevels[1] == 1:
                self._waterlevel = 1
            elif waterlevels[2] == 1:
                self._waterlevel = 2
            else:
                self._waterlevel = 3
            LOGGER.info(
                f"T={self._temperature:4.1f}°C, H={self._humidity:5.1f}%, WL={self._waterlevel}")

    def settemperature(self, value):
        LOGGER.info(("settemperature", repr(value), type(value)))
        self._temperature = value
        return self._temperature

    def sethumidity(self, value):
        LOGGER.info(("sethumidity", repr(value), type(value)))
        self._humidity = value
        return self._humidity

    def identity(self):
        return IDENTITY

    def temperature(self):
        return self._temperature

    def humidity(self):
        return self._humidity

    def waterlevel(self):
        return self._waterlevel

    def setwaterlevel(self, value):
        LOGGER.info(("setwaterlevel", repr(value), type(value)))
        self._waterlevel = value
        return self._waterlevel

    def moisture(self, channel):
        """Return moisture between 0 ... 100"""
        self.adc.requestADC(channel)
        rval = self.adc.getValue()
        LOGGER.debug(f"moisture:getValue() -> {rval}")
        rval = min(self._max, rval)      # set upper limit
        rval = max(self._min, rval)      # set lower limit
        rval = self._slope * rval + self._offset
        return rval

    def reload(self):
        self.settings = load_settings()
        return "OK"


class TheServer(SimpleXMLRPCServer):
    def service_actions(self):
        self.instance._execute()


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


LOGGER.critical("SENSOR PROCESS STARTED")
port = configuration.sensors_server_port
with TheServer(('localhost', port), requestHandler=RequestHandler, logRequests=False) as server:
    server.register_introspection_functions()
    server.register_instance(Bridge())
    server.serve_forever()
