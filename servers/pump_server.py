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
        self.pump_on = True
        self.previous_pump_on = not self.pump_on
        self.pump_mode_manual = False
        self.settings = load_settings()
        self.port_pump = configuration.port_pump
        GPIO.setup(configuration.port_pump, GPIO.OUT)

    def _execute(self):
        time_struct = time.localtime()
        current_time = time_struct.tm_hour * 60 * 60 + \
            time_struct.tm_min * 60 + time_struct.tm_sec

        pump_on_time_i = self.settings["pump_on_time_i"]
        pump_off_time_i = self.settings["pump_off_time_i"]
        invert = pump_on_time_i > pump_off_time_i
        if invert:
            pump_on_time_i, pump_off_time_i = pump_off_time_i, pump_on_time_i
            
        if self.pump_mode_manual is False:
            pump_on = invert ^ (current_time >= pump_on_time_i and current_time <= pump_off_time_i)
            
            if pump_on != self.pump_on:
                self.pump_on = pump_on
                LOGGER.critical(
                    f"pump_on -> {self.pump_on}")
        if self.pump_on != self.previous_pump_on:
            self.previous_pump_on = self.pump_on
            GPIO.output(self.port_pump, GPIO.HIGH if self.pump_on else GPIO.LOW)
        
    def identity(self):
        return IDENTITY

    def get(self):
        return "ON" if self.pump_on else "OFF"
    
    def set(self, onoff):
        print(f"set -> {onoff}")
        self.pump_on = onoff == "ON"
        return "OK"
        
    def get_mode(self):
        return "Manual" if self.pump_mode_manual else "Auto"

    def set_mode(self, mode):
        print(f"Bridge-set {mode}")
        self.pump_mode_manual = mode == "Manual"
        return "OK"

    def reload(self):
        self.settings = load_settings()
        LOGGER.setLevel(get_loglevel("PUMP_SERVER_LOGLEVEL"))
        return "OK"


class TheServer(SimpleXMLRPCServer):
    def service_actions(self):
        self.instance._execute()


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


if __name__ == "__main__":
    LOGGER.critical("PUMP PROCESS STARTED")
    port = configuration.pump_server_port
    with TheServer(('localhost', port), requestHandler=RequestHandler, logRequests=False) as server:
        server.register_introspection_functions()
        server.register_instance(Bridge())
        server.serve_forever()
