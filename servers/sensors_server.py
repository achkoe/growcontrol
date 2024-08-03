#!/usr/bin/env python
"""Server to deliver temperature and humidity over xmlrpc."""


import multiprocessing
import time
import logging
import atexit
from gi.repository import GLib
from base import create_server
import configuration


IDENTITY = "ht_server.py v0.0.1"
send_queue = multiprocessing.Queue()
recv_queue = multiprocessing.Queue()
logging.basicConfig(format="%(module)s:%(levelname)s:%(message)s", level=logging.DEBUG)
LOGLEVEL = logging.CRITICAL


def process(inqueue: multiprocessing.Queue, outqueue: multiprocessing.Queue) -> None:
    # So far just for testing
    logger = logging.getLogger()
    logger.setLevel(LOGLEVEL)
    logger.critical("SENSORS PROCESS STARTED")
    temperature = 24.23456
    humidity = 48.1
    while True:
        time.sleep(0.01)
        if not inqueue.empty():
            query = inqueue.get()
            logger.info(f"query -> {query!r}")
            if query == "temperature":
                logger.info(f"out <- {temperature}")
                outqueue.put(temperature)
            elif query == "humidity":
                logger.info(f"out <- {humidity}")
                outqueue.put(humidity)
            elif query.startswith("settemperature"):
                temperature = float(query[len("settemperature"):])
                outqueue.put("OK")
            else:
                logger.info(f"out <- ?{str(query)}")
                outqueue.put(f"?{str(query)}")

		
LOGGER = logging.getLogger()
LOGGER.setLevel(LOGLEVEL)

PROCESS = multiprocessing.Process(target=process, args=(send_queue, recv_queue))
PROCESS.start()


def terminate():
   LOGGER.critical("TERMINATE SENSORS PROCESS")    
   PROCESS.terminate()
   

atexit.register(terminate)


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
      send_queue.put(command)
      return recv_queue.get()
	

LOGGER.critical(f"SENSORS SERVER AT PORT {configuration.sensors_server_port} STARTED")
create_server(Bridge, configuration.sensors_server_port)


