#!/usr/bin/env python
"""Server to deliver temperature and humidity over xmlrpc."""


import logging
import multiprocessing
import time
import atexit
from base import create_server
import configuration


IDENTITY = "sensors_server.py v0.0.1"
inqueue = multiprocessing.Queue()
outqueue = multiprocessing.Queue()
logging.basicConfig(format="%(module)s:%(levelname)s:%(message)s", level=logging.DEBUG)
LOGLEVEL = logging.CRITICAL
LOGGER = logging.getLogger()
LOGGER.setLevel(LOGLEVEL)


class Bridge():
   def settemperature(self, value):
       LOGGER.info(("settemperature", repr(value), type(value)))
       return self._communicate(f"settemperature{value}")
   
   def identity(self):
       return IDENTITY
   
   def temperature(self):
      LOGGER.info("temperature")
      return "{:4.1f}".format(self._communicate("temperature"))       

   def humidity(self):
      LOGGER.info("humidity")
      return "{:4.1f}".format(self._communicate("humidity"))
   
   def _communicate(self, command):
      global PROCESS
      inqueue.put(command)
      return outqueue.get()


def process(inqueue: multiprocessing.Queue, outqueue: multiprocessing.Queue) -> None:
    logger = logging.getLogger()
    logger.setLevel(LOGLEVEL)

    logger.critical(f"SENSORS SERVER AT PORT {configuration.sensors_server_port} STARTED")
    create_server(Bridge, configuration.sensors_server_port)


def terminate():
   LOGGER.critical("TERMINATE SENSORS PROCESS")    
   PROCESS.terminate()


PROCESS = multiprocessing.Process(target=process, args=(inqueue, outqueue))
PROCESS.start()
atexit.register(terminate)


temperature = 24.23456
humidity = 48.1

while True:
    time.sleep(0.01)
    if not inqueue.empty():
        query = inqueue.get()
        LOGGER.info(f"query -> {query!r}")
        if query == "temperature":
            LOGGER.info(f"out <- {temperature}")
            outqueue.put(temperature)
        elif query == "humidity":
            LOGGER.info(f"out <- {humidity}")
            outqueue.put(humidity)
        elif query.startswith("settemperature"):
            temperature = float(query[len("settemperature"):])
            outqueue.put("OK")
        else:
            LOGGER.info(f"out <- ?{str(query)}")
            outqueue.put(f"?{str(query)}")
