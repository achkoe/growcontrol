#!/usr/bin/env python
"""Server to deliver temperature and humidity over xmlrpc."""

import json
import logging
import os
import pathlib
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from dotenv import dotenv_values

from base import load_settings, get_loglevel
import configuration
import  servers.sensor_driver as driver


IDENTITY = "sensors_server.py v0.0.2"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(get_loglevel("SENSOR_SERVER_LOGLEVEL"))
    

class Bridge():
    def __init__(self):
        self.settings = load_settings()
        # dummy read moisture to clear false readings at startup
        self._execute()

    def reload(self):
        self.settings = load_settings()
        LOGGER.setLevel(get_loglevel("SENSOR_SERVER_LOGLEVEL"))
        return "OK"

    def identity(self):
        return IDENTITY
        
    def _execute(self):
        data = driver.get()

        self._temperature = data["temperature"]
        self._humidity = data["humidity"]
        self._waterlevel = data["waterlevel"]
        self._moisture = data["moisture"]
        
    def get(self):
        return dict(
            temperature=self._temperature,
            humidity=self._humidity,
            waterlevel=self._waterlevel,
            moisture=self._moisture
        )

class TheServer(SimpleXMLRPCServer):
    def service_actions(self):
        self.instance._execute()

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


LOGGER.critical("SENSOR PROCESS STARTED")
bridge = Bridge()
port = configuration.sensors_server_port
with TheServer(('localhost', port), requestHandler=RequestHandler, logRequests=False) as server:
    server.register_introspection_functions()
    server.register_instance(bridge)
    server.serve_forever()
