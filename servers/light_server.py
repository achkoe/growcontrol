#!/usr/bin/env python
"""   Server to deliver light status and control the light."""

import logging
import time
import os
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import RPi.GPIO as GPIO
from servers.base import load_settings, get_loglevel
import configuration


IDENTITY = "light_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGGER = logging.getLogger()
LOGGER.setLevel(get_loglevel("LIGHT_SERVER_LOGLEVEL"))

GPIO.setmode(GPIO.BCM)


class Bridge():
    def __init__(self):
        self.light_on = True
        self.light_mode_manual = False
        self.settings = load_settings()
        self.port_light = configuration.port_light
        GPIO.setup(configuration.port_light, GPIO.OUT)

    def _execute(self):
        time_struct = time.localtime()
        current_time = time_struct.tm_hour * 60 * 60 + \
            time_struct.tm_min * 60 + time_struct.tm_sec

        light_on_time_i = self.settings["light_on_time_i"]
        light_off_time_i = self.settings["light_off_time_i"]
        invert = light_on_time_i > light_off_time_i
        if invert:
            light_on_time_i, light_off_time_i = light_off_time_i, light_on_time_i
            
        if self.light_mode_manual is False:
            light_on = invert ^ (current_time >= light_on_time_i and current_time <= light_off_time_i)
            
            if light_on != self.light_on:
                self.light_on = light_on
                LOGGER.critical(
                    f"light_on -> {self.light_on}")
        GPIO.output(self.port_light, GPIO.HIGH if self.light_on else GPIO.LOW)
        
    def identity(self):
        return IDENTITY

    def get(self):
        return {
            "light": "ON" if self.light_on else "OFF",
        }
        
    def get_mode(self):
        return "Manual" if self.light_mode_manual else "Auto"

    def set(self, mode, light):
        print(f"Bridge-set {mode}, {light}")
        self.light_mode_manual = mode == "Manual"
        self.light_on = light == "On"
        return "OK"

    def reload(self):
        self.settings = load_settings()
        LOGGER.setLevel(get_loglevel("LIGHT_SERVER_LOGLEVEL"))
        return "OK"


class TheServer(SimpleXMLRPCServer):
    def service_actions(self):
        self.instance._execute()


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


if __name__ == "__main__":
    LOGGER.critical("LIGHT PROCESS STARTED")
    port = configuration.light_server_port
    with TheServer(('localhost', port), requestHandler=RequestHandler, logRequests=False) as server:
        server.register_introspection_functions()
        server.register_instance(Bridge())
        server.serve_forever()
