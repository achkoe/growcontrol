#!/usr/bin/env python
"""Server to deliver fan status and control the fan."""

import logging
import multiprocessing
import time
import atexit
import xmlrpc.client
from base import create_server
import  settings


IDENTITY = "fan_server.py v0.0.1"
send_queue = multiprocessing.Queue()
recv_queue = multiprocessing.Queue()
logging.basicConfig(format="%(module)s:%(levelname)s:%(message)s", level=logging.DEBUG)
LOGLEVEL = logging.CRITICAL


def process(inqueue: multiprocessing.Queue, outqueue: multiprocessing.Queue) -> None:
   # So far just for testing
   logger = logging.getLogger()
   logger.setLevel(LOGLEVEL)
   logger.critical("FAN PROCESS STARTED")

   ht_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{settings.sensors_server_port}")

   # fan status
   fan_status = True

   while True:
      time.sleep(0.01)
      temperature = float(ht_proxy.temperature())
      if temperature > 25:
         fan_status = True
      else:
         fan_status = False    

      if not inqueue.empty():
         query = inqueue.get()
         logger.info(f"query -> {query!r}")
         if query == "get":
             reply = "ON" if fan_status is True else "OFF"
             outqueue.put(reply)
         else:
             logger.info(f"out <- ?{str(query)}")
             outqueue.put(f"?{str(query)}")


LOGGER = logging.getLogger()
LOGGER.setLevel(LOGLEVEL)
		
PROCESS = multiprocessing.Process(target=process, args=(send_queue, recv_queue))
PROCESS.start()


def terminate():
   LOGGER.critical("TERMINATE FAN PROCESS")    
   PROCESS.terminate()
   

atexit.register(terminate)


class Bridge():
   def identity(self):
       return IDENTITY
   
   def get(self):
      return self._communicate("get")
   
   def _communicate(self, command):
      send_queue.put(command)
      return recv_queue.get()
	

LOGGER.critical(f"FAN SERVER AT PORT {settings.fan_server_port} STARTED")
create_server(Bridge, settings.fan_server_port)
