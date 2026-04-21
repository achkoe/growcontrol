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
from configuration import port_waterlow, port_watermedium, port_waterhigh


IDENTITY = "sensors_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGGER = logging.getLogger()
LOGGER.setLevel(get_loglevel("SENSOR_SERVER_LOGLEVEL"))


class BridgeBase():
    def __init__(self):
        self.settings = load_settings()
        print(self.settings)
        with pathlib.Path(__file__).parent.parent.joinpath("_data.json").open("r") as fh:
            data = json.load(fh)["sensor"]

        self._temperature = data["temperature"]
        self._humidity = data["humidity"]
        self._waterlevel = data["waterlevel"]
        self._moisture = data["moisture"]

    def settemperature(self, value):
        LOGGER.info(("settemperature", repr(value), type(value)))
        self._temperature = value
        return self._temperature

    def sethumidity(self, value):
        LOGGER.info(("sethumidity", repr(value), type(value)))
        self._humidity = value
        return self._humidity

    def setwaterlevel(self, value):
        LOGGER.info(("setwaterlevel", repr(value), type(value)))
        self._waterlevel = value
        return self._waterlevel
    
    def setmoisture(self, channel, value):
        LOGGER.info(f"{IDENTITY} setmoisture {channel} {value}")
        self._moisture[channel] = value
        return value

    def reload(self):
        self.settings = load_settings()
        LOGGER.setLevel(get_loglevel("SENSOR_SERVER_LOGLEVEL"))
        return "OK"

    def identity(self):
        return IDENTITY
        
    def temperature(self):
        return self._temperature

    def humidity(self):
        return self._humidity

    def waterlevel(self):
        return self._waterlevel
    
    def moisture(self):
        return self._moisture

class Bridge(BridgeBase):
    def __init__(self):
        super().__init__()
        # dummy read moisture to clear false readings at startup
        self._execute()

    def _execute(self):
        with pathlib.Path(__file__).parent.parent.joinpath("_data.json").open("r") as fh:
            data = json.load(fh)["sensor"]

        self._temperature = data["temperature"]
        self._humidity = data["humidity"]
        self._waterlevel = data["waterlevel"]
        self._moisture = data["moisture"]
        
        LOGGER.info(
            f"T={self._temperature:4.1f}°C, H={self._humidity:5.1f}%, WL={self._waterlevel}")


class RemoteControlBride(BridgeBase):
    def _execute(self):
        pass
    
    def moisture(self, channel):
        return self._moisture[channel]

class TheServer(SimpleXMLRPCServer):
    def service_actions(self):
        self.instance._execute()


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


LOGGER.critical("SENSOR PROCESS STARTED")
LOGGER.critical(os.environ.get("REMOTECONTROL", None))
if os.environ.get("REMOTECONTROL", None) is not None:
    bridge = RemoteControlBride()
else:
    bridge = Bridge()
port = configuration.sensors_server_port
with TheServer(('localhost', port), requestHandler=RequestHandler, logRequests=False) as server:
    server.register_introspection_functions()
    server.register_instance(bridge)
    server.serve_forever()
