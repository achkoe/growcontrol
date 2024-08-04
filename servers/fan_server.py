#!/usr/bin/env python
"""Server to deliver fan status and control the fan."""

import logging
import multiprocessing
import time
import atexit
import xmlrpc.client
from base import create_server
import  configuration


IDENTITY = "fan_server.py v0.0.1"
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
   logger = logging.getLogger()
   logger.setLevel(LOGLEVEL)
   logger.critical(f"FAN SERVER AT PORT {configuration.fan_server_port} STARTED")
   create_server(Bridge, configuration.fan_server_port)


def terminate():
   LOGGER.critical("TERMINATE FAN SERVER")    
   PROCESS.terminate()


PROCESS = multiprocessing.Process(target=process, args=())
PROCESS.start()
atexit.register(terminate)


sensors_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.sensors_server_port}")
# fan status
fan_status = True

LOGGER.critical("FAN PROCESS STARTED")
while True:
   time.sleep(0.01)
   temperature = float(sensors_proxy.temperature())
   if temperature > 25:
      fan_status = True
   else:
      fan_status = False    

   if not inqueue.empty():
      query = inqueue.get()
      LOGGER.info(f"query -> {query!r}")
      if query == "get":
          reply = "ON" if fan_status is True else "OFF"
          outqueue.put(reply)
      else:
          LOGGER.info(f"out <- ?{str(query)}")
          outqueue.put(f"?{str(query)}")