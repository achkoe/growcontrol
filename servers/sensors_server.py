#!/usr/bin/env python
"""Server to deliver temperature and humidity over xmlrpc."""


import logging
import time
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from base import load_settings
import  configuration


IDENTITY = "sensors_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGLEVEL = logging.INFO
LOGGER = logging.getLogger()
LOGGER.setLevel(LOGLEVEL)


class Bridge():
    def __init__(self):
        self._temperature = 24.1
        self._humidity = 48
        self._moisture_list = [10] * configuration.number_of_moisture_sensors
        self._waterlevel = 10
        self.settings = load_settings()
    
    def _execute(self):
        pass
    
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
      LOGGER.info("temperature")
      return "{:4.1f}".format(self._temperature)       

    def humidity(self):
        LOGGER.info("humidity")
        return "{:4.1f}".format(self._humidity)

    def waterlevel(self):
        LOGGER.info("waterlevel")
        return "{:d}".format(self._waterlevel)
    
    def setwaterlevel(self, value):
       LOGGER.info(("setwaterlevel", repr(value), type(value)))
       self._waterlevel = value
       return self._waterlevel

    def moisture(self):
        LOGGER.info("moisture")
        return ["{:d}".format(item) for item in self._moisture_list]
   
    def setmoisture(self, value):
       LOGGER.info(("setmoisture", repr(value), type(value)))
       self._moisture_list = [value] * configuration.number_of_moisture_sensors
       return self._moisture_list

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

