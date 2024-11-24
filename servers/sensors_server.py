#!/usr/bin/env python
"""Server to deliver temperature and humidity over xmlrpc."""


import logging
import os
import pathlib
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from dotenv import dotenv_values
import RPi.GPIO as GPIO
import smbus2
from bme280 import BME280
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

from base import load_settings, get_loglevel
import configuration
from configuration import port_waterlow, port_watermedium, port_waterhigh


# set to True to use mocked values
USE_MOCK_VALUES = os.getenv("USE_MOCK_VALUES", False)


IDENTITY = "sensors_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGGER = logging.getLogger()
LOGGER.setLevel(get_loglevel("SENSOR_SERVER_LOGLEVEL"))

GPIO.setmode(GPIO.BCM)


class Bridge():
    def __init__(self):
        GPIO.setup(configuration.port_waterlow, GPIO.IN)
        GPIO.setup([port_waterlow, port_watermedium, port_waterhigh], GPIO.IN)

        # initialize BME280 sensor for temperature and humidity
        bus = smbus2.SMBus(1)
        self.bme280 = BME280(i2c_dev=bus)

        # Create the I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)
        # Create the ADC object using the I2C bus
        self.ads = ADS.ADS1015(i2c)
        # settings for moisture
        # max value ~17390: dry
        # min value ~7470: wet
        self._min = 7500
        self._max = 17000
        self._slope = (100.0 - 0.0) / (self._min - self._max)
        self._offset = - self._slope * self._max
        # dummy read moisture to clear false readings at startup
        [self.moisture(channel) for channel in [0, 1, 2, 3]]
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
            # LOGGER.critical(waterlevels)
            # [1, 1, 1] -> water level is below low marker
            # [0, 1, 1] -> water is between low and medium marker
            # [0, 0, 1] -> water is between medium and high marker
            # [0, 0, 0] -> water is between above high marker
            # LOGGER.critical(waterlevels)
            if waterlevels == [0, 0, 0]:
                self._waterlevel = 0        # critical
            elif waterlevels == [1, 0, 0]:
                self._waterlevel = 1        # low
            elif waterlevels == [1, 1, 0]:
                self._waterlevel = 2        # medium
            elif waterlevels == [1, 1, 1]:  
                self._waterlevel = 3        # full
            else:
                # this should be impossible, therefore set to critical
                self._waterlevel = 0
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
        adc = AnalogIn(self.ads, channel)
        rval = adc.value
        LOGGER.debug(f"moisture:getValue() -> {rval}")
        rval = min(self._max, rval)      # set upper limit
        rval = max(self._min, rval)      # set lower limit
        rval = self._slope * rval + self._offset
        LOGGER.info(f"moisture:{channel} -> {rval}")
        return rval

    def reload(self):
        self.settings = load_settings()
        LOGGER.setLevel(get_loglevel("SENSOR_SERVER_LOGLEVEL"))
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
