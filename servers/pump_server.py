#!/usr/bin/env python
"""Server to deliver pump status and control the pump."""

import logging
import time
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from base import load_settings
import  configuration


IDENTITY = "moisture_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGLEVEL = logging.CRITICAL
LOGGER = logging.getLogger()
LOGGER.setLevel(LOGLEVEL)


class Bridge():
   def __init__(self):
      self.settings = load_settings()
      self.sensors_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.sensors_server_port}")
      self.pump_mode_manual = False
      self.pump_on = False

   def _execute(self):
        pass      
    
   def identity(self):
       return IDENTITY
   
   def get(self):
      return  "OFF"
   
   def set(self, mode, pump_state):
      print(f"Brigde-set {mode} {pump_state}")
      self.pump_mode_manual = mode == "Manual"
      self.pump_on = pump_state == "On"
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


if __name__ == "__main__":
   LOGGER.critical("FAN PROCESS STARTED")
   port = configuration.fan_server_port      
   with TheServer(('localhost', port), requestHandler=RequestHandler, logRequests=False) as server:
      server.register_introspection_functions()
      server.register_instance(Bridge())
      server.serve_forever()

      



