#!/usr/bin/env python
"""   Server to deliver light status and control the light."""

import logging
import multiprocessing
import time
import atexit
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from base import load_settings
import  configuration


IDENTITY = "light_server.py v0.0.1"
inqueue = multiprocessing.Queue()
outqueue = multiprocessing.Queue()
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGLEVEL = logging.CRITICAL
LOGGER = logging.getLogger()
LOGGER.setLevel(LOGLEVEL)


class Bridge():
   def __init__(self):
      self.light_1_on = True
      self.light_2_on = True
      self.light_mode_manual = False
      self.settings = load_settings()

   def _execute(self):
      time_struct = time.localtime()
      current_time = time_struct.tm_hour * 60 * 60 + time_struct.tm_min * 60 + time_struct.tm_sec
      if self.light_mode_manual is False:
         self.light_1_on = current_time >= self.settings["light_1_on_time"] and current_time <= self.settings["light_1_off_time"]
         self.light_2_on = current_time >= self.settings["light_2_on_time"] and current_time <= self.settings["light_2_off_time"]
         #LOGGER.critical(f"light_1_on -> {self.light_1_on}, light_2_on -> {self.light_2_on}")
      
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


port = configuration.light_server_port      
with TheServer(('localhost', port), requestHandler=RequestHandler, logRequests=False) as server:
   server.register_introspection_functions()
   server.register_instance(Bridge())
   server.serve_forever()


""" # light status
light_1_on = True
light_2_on = True
light_mode_manual = False

LOGGER.critical("LIGHT PROCESS STARTED")
settings = load_settings()

while True:
   
   time_struct = time.localtime()
   current_time = time_struct.tm_hour * 60 * 60 + time_struct.tm_min * 60 + time_struct.tm_sec
   if light_mode_manual is False:
      light_1_on = current_time >= settings["light_1_on_time"] and current_time <= settings["light_1_off_time"]
      light_2_on = current_time >= settings["light_2_on_time"] and current_time <= settings["light_2_off_time"]
      LOGGER.info(f"light_1_on -> {light_1_on}, light_2_on -> {light_2_on}")

   time.sleep(0.1)
   
   if not inqueue.empty():
      query = inqueue.get()
      LOGGER.info(f"query -> {query!r}")
      if query == "get":
          reply = {
              "light_1": "ON" if light_1_on else "OFF",
              "light_2": "ON" if light_2_on else "OFF"
          }
          outqueue.put(reply)
      elif query == "reload":
         settings = load_settings()
         outqueue.put("OK")
      elif query == "manual":
         light_mode_manual = True
         light_1_on = False
         light_2_on = False
         outqueue.put("manual-OK")
      elif query == "auto":
         light_mode_manual = False
         outqueue.put("auto-OK")
      elif query == "light1on":
         if light_mode_manual is True:
            light_1_on = True
         outqueue.put("light1on-OK")
      elif query == "light1off":
         if light_mode_manual is True:
            light_1_on = False
         outqueue.put("light1off-OK")
      elif query == "light2on":
         if light_mode_manual is True:
            light_2_on = True
         outqueue.put("light2on-OK")
      elif query == "light2off":
         if light_mode_manual is True:
            light_2_on = False
         outqueue.put("light2off-OK")
      else:
          LOGGER.info(f"out <- ?{str(query)}")
          outqueue.put(f"?{str(query)}")
 """