#!/usr/bin/env python
"""Server to deliver light status and control the light."""

import logging
import multiprocessing
import time
import atexit
import xmlrpc.client
from base import create_server
import  configuration
import json


IDENTITY = "light_server.py v0.0.1"
send_queue = multiprocessing.Queue()
recv_queue = multiprocessing.Queue()
logging.basicConfig(format="%(module)s:%(levelname)s:%(message)s", level=logging.DEBUG)
LOGLEVEL = logging.CRITICAL


def process(inqueue: multiprocessing.Queue, outqueue: multiprocessing.Queue) -> None:
   # So far just for testing
   logger = logging.getLogger()
   logger.setLevel(LOGLEVEL)
   logger.critical("LIGHT PROCESS STARTED")

   # light status
   light_1_status = True
   light_2_status = True

   while True:
      time.sleep(0.1)

      if not inqueue.empty():
         query = inqueue.get()
         logger.info(f"query -> {query!r}")
         if query == "get":
             reply = {
                 "light_1": "ON" if light_1_status else "OFF",
                 "light_2": "ON" if light_2_status else "OFF"
             }
             outqueue.put(reply)
         else:
             logger.info(f"out <- ?{str(query)}")
             outqueue.put(f"?{str(query)}")


LOGGER = logging.getLogger()
LOGGER.setLevel(LOGLEVEL)
		
PROCESS = multiprocessing.Process(target=process, args=(send_queue, recv_queue))
PROCESS.start()


def terminate():
   LOGGER.critical("TERMINATE LIGHT PROCESS")    
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
	

LOGGER.critical(f"LIGHT SERVER AT PORT {configuration.light_server_port} STARTED")
create_server(Bridge, configuration.light_server_port)
