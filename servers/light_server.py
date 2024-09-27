#!/usr/bin/env python
"""   Server to deliver light status and control the light."""

import logging
import time
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import RPi.GPIO as GPIO
from base import load_settings
import configuration


IDENTITY = "light_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGLEVEL = logging.CRITICAL
LOGGER = logging.getLogger()
LOGGER.setLevel(LOGLEVEL)

GPIO.setmode(GPIO.BCM)


class Bridge():
    def __init__(self):
        self.light_1_on = True
        self.light_2_on = True
        self.light_mode_manual = False
        self.settings = load_settings()
        self.port_light1 = configuration.port_light1
        self.port_light2 = configuration.port_light2
        GPIO.setup([configuration.port_light1,
                   configuration.port_light2], GPIO.OUT)

    def _execute(self):
        time_struct = time.localtime()
        current_time = time_struct.tm_hour * 60 * 60 + \
            time_struct.tm_min * 60 + time_struct.tm_sec
        if self.light_mode_manual is False:
            light_1_on = current_time >= self.settings[
                "light_1_on_time_i"] and current_time <= self.settings["light_1_off_time_i"]
            light_2_on = current_time >= self.settings[
                "light_2_on_time_i"] and current_time <= self.settings["light_2_off_time_i"]
            if light_1_on != self.light_1_on or light_2_on != self.light_2_on:
                self.light_1_on = light_1_on
                self.light_2_on = light_2_on
                LOGGER.critical(
                    f"light_1_on -> {self.light_1_on}, light_2_on -> {self.light_2_on}")
        GPIO.output(self.port_light1,
                    GPIO.HIGH if self.light_1_on else GPIO.LOW)
        GPIO.output(self.port_light2,
                    GPIO.HIGH if self.light_2_on else GPIO.LOW)

    def identity(self):
        return IDENTITY

    def get(self):
        return {
            "light_1": "ON" if self.light_1_on else "OFF",
            "light_2": "ON" if self.light_2_on else "OFF"
        }

    def set(self, mode, light1, light2):
        print(f"Bridge-set {mode}, {light1}, {light2}")
        self.light_mode_manual = mode == "Manual"
        self.light_1_on = light1 == "On"
        self.light_2_on = light2 == "On"
        return "OK"

    def reload(self):
        self.settings = load_settings()
        return "OK"


class TheServer(SimpleXMLRPCServer):
    def service_actions(self):
        self.instance._execute()


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


LOGGER.critical("LIGHT PROCESS STARTED")
port = configuration.light_server_port
with TheServer(('localhost', port), requestHandler=RequestHandler, logRequests=False) as server:
    server.register_introspection_functions()
    server.register_instance(Bridge())
    server.serve_forever()
