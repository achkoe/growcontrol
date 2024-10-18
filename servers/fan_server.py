#!/usr/bin/env python
"""Server to deliver fan status and control the fan."""

import logging
import os
import pathlib
import time
import xmlrpc.client
from dotenv import dotenv_values
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import RPi.GPIO as GPIO
from base import load_settings, get_loglevel
import configuration


IDENTITY = "fan_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGGER = logging.getLogger()
LOGGER.setLevel(get_loglevel("FAN_SERVER_LOGLEVEL"))


WAIT, RUN, DOWN = 0, 1, 2
START_AT_MINUTE = 5


GPIO.setmode(GPIO.BCM)


class Bridge():
    def __init__(self):
        self.settings = load_settings()
        self.sensors_proxy = xmlrpc.client.ServerProxy(
            f"http://localhost:{configuration.sensors_server_port}")
        # fan status
        self.fan_is_on = False
        self.fan_mode_manual = False
        self.fan_on = False
        self.state = WAIT
        self.port_fan = configuration.port_fan
        GPIO.setup(configuration.port_fan, GPIO.OUT)

    def _execute(self):
        LOGGER.debug(f"state={self.state}")
        temperature = float(self.sensors_proxy.temperature())
        humidity = float(self.sensors_proxy.humidity())

        def ts(time_struct): return time_struct.tm_min

        if self.fan_mode_manual is False:
            if temperature > float(self.settings["temperature_high_level"]) or humidity > float(self.settings["humidity_high_level"]):
                # start fan to reduce temperature or humidity
                self.fan_is_on = True
                self.state = DOWN
                LOGGER.info(f"1:state: DOWN")
            elif self.state == DOWN and temperature < float(self.settings["temperature_low_level"]) and humidity < float(self.settings["humidity_low_level"]):
                self.fan_is_on = False
                self.state = WAIT
                LOGGER.info(f"2:state: WAIT")
            else:
                time_struct = time.localtime()
                # LOGGER.critical(f"state -> {self.state}, tm_min -> {time_struct.tm_sec}, START_AT_MINUTE -> {START_AT_MINUTE}")
                if self.state == WAIT:
                    if ts(time_struct) >= START_AT_MINUTE and ts(time_struct) <= START_AT_MINUTE + int(self.settings["fan_minutes_in_hour"]):
                        # start fan if minutes is between START_AT_MINUTE and START_AT_MINUTE + fan_minutes_in_hour 
                        LOGGER.info(f"3: state WAIT -> RUN")
                        self.fan_is_on = True
                        self.state = RUN
                    else:
                        self.fan_is_on = False
                else:
                    if ts(time_struct) == START_AT_MINUTE + int(self.settings["fan_minutes_in_hour"]):
                        # stop fan every hour + START_AT_MINUTE minutes + fan_minutes_in_hour
                        self.fan_is_on = False
                        self.state = WAIT
                        LOGGER.info(f"4:state: RUN -> WAIT")
        else:
            self.fan_is_on = self.fan_on
        GPIO.output(self.port_fan, GPIO.HIGH if self.fan_is_on else GPIO.LOW)

    def identity(self):
        return IDENTITY

    def get(self):
        return "ON" if self.fan_is_on is True else "OFF"
    
    def get_mode(self):
        return "Manual" if self.fan_mode_manual else "Auto"

    def set(self, mode, fan_state):
        print(f"Brigde-set {mode} {fan_state}")
        self.fan_mode_manual = mode == "Manual"
        self.fan_on = fan_state == "On"
        if self.fan_mode_manual is False:
            if self.state in [RUN, DOWN]:
                self.fan_is_on = True
        return "OK"

    def reload(self):
        self.settings = load_settings()
        LOGGER.setLevel(get_loglevel("FAN_SERVER_LOGLEVEL"))
        return "OK"


class TheServer(SimpleXMLRPCServer):
    def service_actions(self):
        self.instance._execute()


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


if __name__ == "__main__":
    LOGGER.critical("FAN PROCESS STARTED")
    port = configuration.fan_server_port
    with TheServer(('localhost', port), requestHandler=RequestHandler, logRequests=False) as server:
        server.register_introspection_functions()
        server.register_instance(Bridge())
        server.serve_forever()
