#!/usr/bin/env python
"""Server to deliver light status and control the light."""

import logging
import multiprocessing
import time
import pathlib
import atexit
from base import create_server
import  configuration
import json


IDENTITY = "light_server.py v0.0.1"
inqueue = multiprocessing.Queue()
outqueue = multiprocessing.Queue()
logging.basicConfig(format="%(module)s:%(levelname)s:%(message)s", level=logging.DEBUG)
LOGLEVEL = logging.CRITICAL
LOGGER = logging.getLogger()
LOGGER.setLevel(LOGLEVEL)


class Bridge():
   def identity(self):
       return IDENTITY
   
   def get(self):
      return self._communicate("get")
   
   def _communicate(self, command):
      inqueue.put(command)
      return outqueue.get()


def process() -> None:
   # So far just for testing
   logger = logging.getLogger()
   logger.setLevel(LOGLEVEL)
   
   logger.critical(f"LIGHT SERVER AT PORT {configuration.light_server_port} STARTED")
   create_server(Bridge, configuration.light_server_port)

		
def terminate():
   LOGGER.critical("TERMINATE LIGHT SERVER")    
   PROCESS.terminate()


PROCESS = multiprocessing.Process(target=process, args=())
PROCESS.start()
atexit.register(terminate)


def load_settings():
   pass
      

# light status
light_1_status = True
light_2_status = True

LOGGER.critical("LIGHT PROCESS STARTED")
while True:
   time.sleep(0.1)

   if not inqueue.empty():
      query = inqueue.get()
      LOGGER.info(f"query -> {query!r}")
      if query == "get":
          reply = {
              "light_1": "ON" if light_1_status else "OFF",
              "light_2": "ON" if light_2_status else "OFF"
          }
          outqueue.put(reply)
      elif query == "reload":
         pass            
      else:
          LOGGER.info(f"out <- ?{str(query)}")
          outqueue.put(f"?{str(query)}")
